from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from dbfread import DBF


@dataclass(frozen=True)
class ArgumentosExecucao:
    pasta_entrada_dbf: Path
    pasta_saida_parquet: Path
    tamanho_lote: int = 50_000

    @classmethod
    def criar_do_cli(cls) -> "ArgumentosExecucao":
        parser = argparse.ArgumentParser(
            description="Converte arquivos DBF para Parquet com validacao e relatorio HTML."
        )
        parser.add_argument("--pasta-entrada-dbf", type=Path, required=True)
        parser.add_argument("--pasta-saida-parquet", type=Path, required=True)
        argumentos = parser.parse_args()
        return cls(
            pasta_entrada_dbf=argumentos.pasta_entrada_dbf,
            pasta_saida_parquet=argumentos.pasta_saida_parquet,
        )


class LoggerAplicacao:
    def __init__(self, pasta_saida: Path) -> None:
        self._arquivo_log = pasta_saida / "conversao_dbf_parquet.log"

    @property
    def arquivo_log(self) -> Path:
        return self._arquivo_log

    def criar_logger(self) -> logging.Logger:
        logger = logging.getLogger("dbf_to_parquet")
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


@dataclass
class ResultadoValidacaoArquivo:
    nome_arquivo: str
    dbf_localizado: str = "ERRO"
    parquet_gerado: str = "ERRO"
    leitura_dbf_ok: str = "ERRO"
    gravacao_parquet_ok: str = "ERRO"
    colunas_conferem: str = "ERRO"
    registros_conferem: str = "ERRO"
    primeiros_10_registros_conferem: str = "ERRO"
    conversao_integra: str = "ERRO"


@dataclass
class MetadadosDbf:
    encoding: str
    colunas: list[str]
    quantidade_registros: int
    primeiros_registros: list[dict[str, str]]


@dataclass
class ResultadoEscritaParquet:
    colunas: list[str]
    quantidade_registros: int


@dataclass
class ContextoArquivo:
    caminho_dbf: Path
    caminho_parquet: Path
    resultado: ResultadoValidacaoArquivo
    metadados_dbf: MetadadosDbf | None = None
    resultado_escrita: ResultadoEscritaParquet | None = None


@dataclass
class RelatorioExecucao:
    itens: list[ResultadoValidacaoArquivo] = field(default_factory=list)

    def adicionar(self, resultado: ResultadoValidacaoArquivo) -> None:
        self.itens.append(resultado)


class LeitorDbf:
    def __init__(self, logger: logging.Logger, tamanho_lote: int) -> None:
        self._logger = logger
        self._tamanho_lote = tamanho_lote
        self._encodings = ("latin1", "cp1252", "utf-8")

    def coletar_metadados(self, caminho_dbf: Path) -> MetadadosDbf:
        encoding = self._detectar_encoding(caminho_dbf)
        leitor = DBF(str(caminho_dbf), encoding=encoding, load=False)
        colunas = self._nomes_colunas(leitor)
        primeiros_registros: list[dict[str, str]] = []
        quantidade_registros = 0

        for registro in leitor:
            quantidade_registros += 1
            if len(primeiros_registros) < 10:
                primeiros_registros.append(self._normalizar_registro(registro))

        return MetadadosDbf(
            encoding=encoding,
            colunas=colunas,
            quantidade_registros=quantidade_registros,
            primeiros_registros=primeiros_registros,
        )

    def iterar_lotes(self, caminho_dbf: Path, encoding: str) -> Iterator[pd.DataFrame]:
        leitor = DBF(str(caminho_dbf), encoding=encoding, load=False)
        lote_atual: list[dict[str, Any]] = []

        for registro in leitor:
            lote_atual.append(self._registro_para_dataframe(registro))
            if len(lote_atual) >= self._tamanho_lote:
                yield pd.DataFrame.from_records(lote_atual)
                lote_atual = []

        if lote_atual:
            yield pd.DataFrame.from_records(lote_atual)

    def _detectar_encoding(self, caminho_dbf: Path) -> str:
        for encoding in self._encodings:
            if self._encoding_funciona(caminho_dbf, encoding):
                self._logger.info("Encoding detectado para %s: %s", caminho_dbf.name, encoding)
                return encoding
        raise RuntimeError(f"Nao foi possivel detectar encoding para {caminho_dbf.name}")

    def _encoding_funciona(self, caminho_dbf: Path, encoding: str) -> bool:
        try:
            leitor = DBF(str(caminho_dbf), encoding=encoding, load=False)
            next(iter(leitor), None)
            return True
        except Exception as erro:
            self._logger.warning(
                "Falha ao testar encoding %s em %s: %s",
                encoding,
                caminho_dbf.name,
                erro,
            )
            return False

    def _nomes_colunas(self, leitor: DBF) -> list[str]:
        return [campo.name for campo in leitor.fields]

    def _registro_para_dataframe(self, registro: Any) -> dict[str, Any]:
        return {coluna: self._valor_dataframe(valor) for coluna, valor in dict(registro).items()}

    def _normalizar_registro(self, registro: Any) -> dict[str, str]:
        return {coluna: self._valor_comparavel(valor) for coluna, valor in dict(registro).items()}

    def _valor_dataframe(self, valor: Any) -> Any:
        if pd.isna(valor):
            return None
        return valor

    def _valor_comparavel(self, valor: Any) -> str:
        if pd.isna(valor):
            return ""
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        return str(valor)


class EscritorParquet:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def salvar_em_lotes(
        self,
        lotes: Iterator[pd.DataFrame],
        caminho_parquet: Path,
    ) -> ResultadoEscritaParquet:
        escritor: pq.ParquetWriter | None = None
        esquema: pa.Schema | None = None
        colunas: list[str] = []
        quantidade_registros = 0

        try:
            for numero_lote, lote in enumerate(lotes, start=1):
                tabela = self._criar_tabela(lote, colunas)
                if not colunas:
                    colunas = tabela.column_names
                if escritor is None:
                    esquema = tabela.schema
                    escritor = pq.ParquetWriter(caminho_parquet, esquema, compression="snappy")
                tabela = self._alinhar_tabela(tabela, esquema)
                escritor.write_table(tabela)
                quantidade_registros += tabela.num_rows
                self._logger.info(
                    "Parquet %s lote=%s registros_acumulados=%s",
                    caminho_parquet.name,
                    numero_lote,
                    quantidade_registros,
                )
        finally:
            if escritor is not None:
                escritor.close()

        return ResultadoEscritaParquet(
            colunas=colunas,
            quantidade_registros=quantidade_registros,
        )

    def _criar_tabela(self, lote: pd.DataFrame, colunas: list[str]) -> pa.Table:
        dataframe = self._preparar_dataframe(lote, colunas)
        return pa.Table.from_pandas(dataframe, preserve_index=False)

    def _preparar_dataframe(self, lote: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
        dataframe = lote.copy()
        dataframe = self._converter_textos(dataframe)
        if not colunas:
            return dataframe
        return dataframe.reindex(columns=colunas)

    def _converter_textos(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        colunas_texto = dataframe.select_dtypes(include=["object"]).columns
        for coluna in colunas_texto:
            dataframe[coluna] = dataframe[coluna].astype("string")
        return dataframe

    def _alinhar_tabela(self, tabela: pa.Table, esquema: pa.Schema | None) -> pa.Table:
        if esquema is None or tabela.schema == esquema:
            return tabela
        return tabela.cast(esquema, safe=False)


class ValidadorConversao:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def validar(self, contexto: ContextoArquivo) -> None:
        parquet = pq.ParquetFile(contexto.caminho_parquet)
        colunas_parquet = parquet.schema.names
        registros_parquet = parquet.metadata.num_rows
        primeiros_registros_parquet = self._ler_primeiros_registros(parquet)

        contexto.resultado.colunas_conferem = self._status(
            len(contexto.metadados_dbf.colunas) == len(colunas_parquet)
        )
        contexto.resultado.registros_conferem = self._status(
            contexto.metadados_dbf.quantidade_registros == registros_parquet
        )
        contexto.resultado.primeiros_10_registros_conferem = self._status(
            contexto.metadados_dbf.primeiros_registros == primeiros_registros_parquet
        )
        contexto.resultado.conversao_integra = self._status(self._conversao_integra(contexto.resultado))
        self._logger.info("Validacao concluida para %s", contexto.caminho_dbf.name)

    def _ler_primeiros_registros(self, parquet: pq.ParquetFile) -> list[dict[str, str]]:
        for lote in parquet.iter_batches(batch_size=10):
            dataframe = lote.to_pandas()
            dataframe = dataframe.reindex(sorted(dataframe.columns), axis=1)
            return [
                {coluna: self._valor_comparavel(valor) for coluna, valor in linha.items()}
                for linha in dataframe.to_dict(orient="records")
            ]
        return []

    def _valor_comparavel(self, valor: Any) -> str:
        if pd.isna(valor):
            return ""
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        return str(valor)

    def _conversao_integra(self, resultado: ResultadoValidacaoArquivo) -> bool:
        itens = (
            resultado.dbf_localizado,
            resultado.parquet_gerado,
            resultado.leitura_dbf_ok,
            resultado.gravacao_parquet_ok,
            resultado.colunas_conferem,
            resultado.registros_conferem,
            resultado.primeiros_10_registros_conferem,
        )
        return all(item == "OK" for item in itens)

    def _status(self, condicao: bool) -> str:
        if condicao:
            return "OK"
        return "ERRO"


class GeradorRelatorioHtml:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def gerar(self, relatorio: RelatorioExecucao, caminho_saida: Path) -> None:
        caminho_saida.write_text(self._montar_html(relatorio), encoding="utf-8")
        self._logger.info("Relatorio HTML salvo em %s", caminho_saida)

    def _montar_html(self, relatorio: RelatorioExecucao) -> str:
        secoes = "\n".join(self._montar_secao(item) for item in relatorio.itens)
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Relatorio de Validacao</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f5f5f5; color: #222; }}
    .arquivo {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    ul {{ list-style: none; padding-left: 0; }}
    li {{ padding: 4px 0; }}
    .ok {{ color: #137333; font-weight: bold; }}
    .erro {{ color: #b3261e; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Relatorio de Validacao</h1>
  {secoes}
</body>
</html>"""

    def _montar_secao(self, item: ResultadoValidacaoArquivo) -> str:
        checklist = [
            ("DBF localizado", item.dbf_localizado),
            ("Parquet gerado", item.parquet_gerado),
            ("Leitura DBF OK", item.leitura_dbf_ok),
            ("Gravacao Parquet OK", item.gravacao_parquet_ok),
            ("Colunas conferem", item.colunas_conferem),
            ("Registros conferem", item.registros_conferem),
            ("Primeiros 10 registros conferem", item.primeiros_10_registros_conferem),
            ("Conversao integra", item.conversao_integra),
        ]
        itens = "\n".join(self._montar_item(rotulo, status) for rotulo, status in checklist)
        return f"""<section class="arquivo">
  <h2>{item.nome_arquivo}</h2>
  <ul>
    {itens}
  </ul>
</section>"""

    def _montar_item(self, rotulo: str, status: str) -> str:
        classe = "ok" if status == "OK" else "erro"
        return f'<li>{rotulo}: <span class="{classe}">{status}</span></li>'


class OrquestradorConversao:
    def __init__(
        self,
        logger: logging.Logger,
        leitor_dbf: LeitorDbf,
        escritor_parquet: EscritorParquet,
        validador: ValidadorConversao,
        gerador_relatorio: GeradorRelatorioHtml,
    ) -> None:
        self._logger = logger
        self._leitor_dbf = leitor_dbf
        self._escritor_parquet = escritor_parquet
        self._validador = validador
        self._gerador_relatorio = gerador_relatorio

    def executar(self, argumentos: ArgumentosExecucao) -> None:
        argumentos.pasta_saida_parquet.mkdir(parents=True, exist_ok=True)
        arquivos_dbf = sorted(argumentos.pasta_entrada_dbf.glob("*.dbf"))
        relatorio = RelatorioExecucao()

        self._logger.info("Inicio do processamento em %s", argumentos.pasta_entrada_dbf)
        if not arquivos_dbf:
            self._logger.warning("Nenhum arquivo DBF encontrado em %s", argumentos.pasta_entrada_dbf)

        for caminho_dbf in arquivos_dbf:
            relatorio.adicionar(self._processar_arquivo(caminho_dbf, argumentos))

        caminho_relatorio = argumentos.pasta_saida_parquet / "relatorio_validacao.html"
        self._gerador_relatorio.gerar(relatorio, caminho_relatorio)
        self._logger.info("Fim do processamento. Total de arquivos: %s", len(relatorio.itens))

    def _processar_arquivo(
        self,
        caminho_dbf: Path,
        argumentos: ArgumentosExecucao,
    ) -> ResultadoValidacaoArquivo:
        resultado = ResultadoValidacaoArquivo(nome_arquivo=caminho_dbf.name, dbf_localizado="OK")
        caminho_parquet = argumentos.pasta_saida_parquet / f"{caminho_dbf.stem}.parquet"
        contexto = ContextoArquivo(caminho_dbf=caminho_dbf, caminho_parquet=caminho_parquet, resultado=resultado)

        self._logger.info("Processando arquivo %s", caminho_dbf.name)
        try:
            self._coletar_metadados(contexto)
            self._gravar_parquet(contexto)
            self._validar(contexto)
            self._logger.info("Sucesso no arquivo %s", caminho_dbf.name)
        except Exception:
            self._logger.exception("Erro ao processar %s", caminho_dbf.name)
        return resultado

    def _coletar_metadados(self, contexto: ContextoArquivo) -> None:
        contexto.metadados_dbf = self._leitor_dbf.coletar_metadados(contexto.caminho_dbf)
        contexto.metadados_dbf.primeiros_registros = self._ordenar_registros(contexto.metadados_dbf.primeiros_registros)
        contexto.resultado.leitura_dbf_ok = "OK"

    def _gravar_parquet(self, contexto: ContextoArquivo) -> None:
        lotes = self._leitor_dbf.iterar_lotes(
            contexto.caminho_dbf,
            contexto.metadados_dbf.encoding,
        )
        contexto.resultado_escrita = self._escritor_parquet.salvar_em_lotes(lotes, contexto.caminho_parquet)
        contexto.resultado.gravacao_parquet_ok = "OK"
        contexto.resultado.parquet_gerado = self._status_arquivo(contexto.caminho_parquet)

    def _validar(self, contexto: ContextoArquivo) -> None:
        self._validador.validar(contexto)

    def _ordenar_registros(self, registros: list[dict[str, str]]) -> list[dict[str, str]]:
        return [dict(sorted(registro.items())) for registro in registros]

    def _status_arquivo(self, caminho_arquivo: Path) -> str:
        if caminho_arquivo.exists():
            return "OK"
        return "ERRO"


def main() -> None:
    argumentos = ArgumentosExecucao.criar_do_cli()
    argumentos.pasta_saida_parquet.mkdir(parents=True, exist_ok=True)
    logger = LoggerAplicacao(argumentos.pasta_saida_parquet).criar_logger()
    leitor_dbf = LeitorDbf(logger, argumentos.tamanho_lote)
    escritor_parquet = EscritorParquet(logger)
    validador = ValidadorConversao(logger)
    gerador_relatorio = GeradorRelatorioHtml(logger)
    orquestrador = OrquestradorConversao(
        logger=logger,
        leitor_dbf=leitor_dbf,
        escritor_parquet=escritor_parquet,
        validador=validador,
        gerador_relatorio=gerador_relatorio,
    )
    orquestrador.executar(argumentos)


if __name__ == "__main__":
    main()
