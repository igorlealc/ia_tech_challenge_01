from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq


@dataclass(frozen=True)
class ArgumentosExecucao:
    arquivo_entrada: Path
    arquivo_saida: Path
    colunas_remover: tuple[str, ...]
    batch_size: int
    compression: str

    @classmethod
    def criar_do_cli(cls) -> "ArgumentosExecucao":
        parser = argparse.ArgumentParser(
            description="Remove colunas de um arquivo Parquet e grava uma versao reduzida."
        )
        parser.add_argument("--arquivo-entrada", type=Path, required=True)
        parser.add_argument("--arquivo-saida", type=Path, required=True)
        parser.add_argument(
            "--coluna-remover",
            dest="colunas_remover",
            action="append",
            default=[],
            help="Coluna a ser removida. Repita o argumento para varias colunas.",
        )
        parser.add_argument(
            "--arquivo-colunas",
            type=Path,
            help="Arquivo texto com uma coluna por linha para ser removida.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100_000,
            help="Quantidade de linhas por lote durante a escrita incremental.",
        )
        parser.add_argument(
            "--compression",
            default="snappy",
            help="Codec de compressao do parquet de saida. Ex.: snappy, zstd, gzip.",
        )
        argumentos = parser.parse_args()

        colunas = list(argumentos.colunas_remover)
        if argumentos.arquivo_colunas:
            colunas.extend(_ler_colunas_de_arquivo(argumentos.arquivo_colunas))

        colunas_normalizadas = tuple(dict.fromkeys(coluna.strip() for coluna in colunas if coluna.strip()))
        return cls(
            arquivo_entrada=argumentos.arquivo_entrada,
            arquivo_saida=argumentos.arquivo_saida,
            colunas_remover=colunas_normalizadas,
            batch_size=argumentos.batch_size,
            compression=argumentos.compression,
        )


def _ler_colunas_de_arquivo(caminho_arquivo: Path) -> list[str]:
    return caminho_arquivo.read_text(encoding="utf-8").splitlines()


class LoggerAplicacao:
    def __init__(self, arquivo_saida: Path) -> None:
        self._arquivo_log = arquivo_saida.with_suffix(".log")

    def criar_logger(self) -> logging.Logger:
        logger = logging.getLogger("remove_parquet_columns")
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        logger.propagate = False
        formatador = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        manipulador_console = logging.StreamHandler()
        manipulador_console.setFormatter(formatador)

        manipulador_arquivo = logging.FileHandler(self._arquivo_log, encoding="utf-8")
        manipulador_arquivo.setFormatter(formatador)

        logger.addHandler(manipulador_console)
        logger.addHandler(manipulador_arquivo)
        return logger


@dataclass(frozen=True)
class ResultadoReducao:
    colunas_originais: tuple[str, ...]
    colunas_removidas: tuple[str, ...]
    colunas_mantidas: tuple[str, ...]
    linhas_processadas: int
    tamanho_entrada_bytes: int
    tamanho_saida_bytes: int


class RemovedorColunasParquet:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def executar(self, argumentos: ArgumentosExecucao) -> ResultadoReducao:
        self._validar_argumentos(argumentos)
        dataset = ds.dataset(argumentos.arquivo_entrada, format="parquet")
        colunas_originais = tuple(dataset.schema.names)
        colunas_mantidas = self._definir_colunas_mantidas(colunas_originais, argumentos.colunas_remover)

        self._logger.info("Arquivo de entrada: %s", argumentos.arquivo_entrada)
        self._logger.info("Arquivo de saida: %s", argumentos.arquivo_saida)
        self._logger.info("Colunas originais: %s", len(colunas_originais))
        self._logger.info("Colunas removidas: %s", ", ".join(argumentos.colunas_remover))
        self._logger.info("Colunas mantidas: %s", len(colunas_mantidas))
        self._logger.info("Batch size: %s", argumentos.batch_size)
        self._logger.info("Compressao: %s", argumentos.compression)

        linhas_processadas = self._gravar_saida_incremental(
            dataset=dataset,
            arquivo_saida=argumentos.arquivo_saida,
            colunas_mantidas=colunas_mantidas,
            batch_size=argumentos.batch_size,
            compression=argumentos.compression,
        )

        resultado = ResultadoReducao(
            colunas_originais=colunas_originais,
            colunas_removidas=argumentos.colunas_remover,
            colunas_mantidas=colunas_mantidas,
            linhas_processadas=linhas_processadas,
            tamanho_entrada_bytes=argumentos.arquivo_entrada.stat().st_size,
            tamanho_saida_bytes=argumentos.arquivo_saida.stat().st_size,
        )
        self._logger.info("Linhas processadas: %s", resultado.linhas_processadas)
        self._logger.info("Tamanho entrada: %s bytes", resultado.tamanho_entrada_bytes)
        self._logger.info("Tamanho saida: %s bytes", resultado.tamanho_saida_bytes)
        self._logger.info(
            "Reducao absoluta: %s bytes",
            resultado.tamanho_entrada_bytes - resultado.tamanho_saida_bytes,
        )
        return resultado

    def _validar_argumentos(self, argumentos: ArgumentosExecucao) -> None:
        if not argumentos.arquivo_entrada.exists():
            raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {argumentos.arquivo_entrada}")
        if argumentos.arquivo_entrada.suffix.lower() != ".parquet":
            raise ValueError("O arquivo de entrada precisa ser .parquet")
        if not argumentos.colunas_remover:
            raise ValueError("Informe ao menos uma coluna para remover")
        if argumentos.batch_size <= 0:
            raise ValueError("batch-size deve ser maior que zero")

        argumentos.arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

    def _definir_colunas_mantidas(
        self,
        colunas_originais: tuple[str, ...],
        colunas_remover: tuple[str, ...],
    ) -> tuple[str, ...]:
        ausentes = sorted(set(colunas_remover) - set(colunas_originais))
        if ausentes:
            raise ValueError(f"Colunas nao encontradas no parquet: {', '.join(ausentes)}")

        colunas_mantidas = tuple(coluna for coluna in colunas_originais if coluna not in colunas_remover)
        if not colunas_mantidas:
            raise ValueError("A remocao proposta elimina todas as colunas do arquivo")
        return colunas_mantidas

    def _gravar_saida_incremental(
        self,
        dataset: ds.Dataset,
        arquivo_saida: Path,
        colunas_mantidas: tuple[str, ...],
        batch_size: int,
        compression: str,
    ) -> int:
        writer: pq.ParquetWriter | None = None
        linhas_processadas = 0
        scanner = dataset.scanner(columns=list(colunas_mantidas), batch_size=batch_size, use_threads=True)

        try:
            for batch in scanner.to_batches():
                if writer is None:
                    writer = pq.ParquetWriter(arquivo_saida, batch.schema, compression=compression)
                writer.write_batch(batch)
                linhas_processadas += batch.num_rows
        finally:
            if writer is not None:
                writer.close()

        if writer is None:
            tabela_vazia = pa.Table.from_arrays(
                arrays=[pa.array([], type=campo.type) for campo in dataset.schema if campo.name in colunas_mantidas],
                names=list(colunas_mantidas),
            )
            pq.write_table(tabela_vazia, arquivo_saida, compression=compression)

        return linhas_processadas


def _formatar_bytes(quantidade: int) -> str:
    unidade = "B"
    valor = float(quantidade)
    for proxima_unidade in ("KB", "MB", "GB", "TB"):
        if valor < 1024:
            break
        valor /= 1024
        unidade = proxima_unidade
    return f"{valor:.2f} {unidade}"


def _montar_resumo(resultado: ResultadoReducao) -> str:
    return (
        f"Concluido: {resultado.linhas_processadas} linhas processadas, "
        f"{len(resultado.colunas_removidas)} coluna(s) removida(s), "
        f"entrada={_formatar_bytes(resultado.tamanho_entrada_bytes)}, "
        f"saida={_formatar_bytes(resultado.tamanho_saida_bytes)}."
    )


def main() -> None:
    argumentos = ArgumentosExecucao.criar_do_cli()
    logger = LoggerAplicacao(argumentos.arquivo_saida).criar_logger()
    removedor = RemovedorColunasParquet(logger)
    resultado = removedor.executar(argumentos)
    logger.info(_montar_resumo(resultado))


if __name__ == "__main__":
    main()
