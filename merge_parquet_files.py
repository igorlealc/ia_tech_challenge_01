from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq


@dataclass(frozen=True)
class ArgumentosExecucao:
    pasta_origem: Path
    pasta_destino: Path

    @classmethod
    def criar_do_cli(cls) -> "ArgumentosExecucao":
        parser = argparse.ArgumentParser(
            description="Realiza merge de arquivos Parquet com validacao e relatorio HTML."
        )
        parser.add_argument("--pasta-origem", type=Path, required=True)
        parser.add_argument("--pasta-destino", type=Path, required=True)
        argumentos = parser.parse_args()
        return cls(
            pasta_origem=argumentos.pasta_origem,
            pasta_destino=argumentos.pasta_destino,
        )


class LoggerAplicacao:
    def __init__(self, pasta_destino: Path) -> None:
        self._arquivo_log = pasta_destino / "merge_parquet.log"

    @property
    def arquivo_log(self) -> Path:
        return self._arquivo_log

    def criar_logger(self) -> logging.Logger:
        logger = logging.getLogger("merge_parquet")
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
class ResultadoValidacaoMerge:
    pasta_origem_validada: str = "ERRO"
    pasta_destino_validada: str = "ERRO"
    arquivos_localizados: str = "ERRO"
    leitura_realizada: str = "ERRO"
    merge_realizado: str = "ERRO"
    arquivo_final_gerado: str = "ERRO"
    colunas_mantidas: str = "ERRO"
    registros_conferem: str = "ERRO"
    integridade_confirmada: str = "ERRO"


@dataclass(frozen=True)
class MetadadosArquivoParquet:
    caminho_arquivo: Path
    colunas: list[str]
    quantidade_registros: int


@dataclass
class ContextoMerge:
    arquivos_localizados: list[Path] = field(default_factory=list)
    arquivos_validos: list[MetadadosArquivoParquet] = field(default_factory=list)
    arquivo_saida: Path | None = None
    colunas_saida: list[str] = field(default_factory=list)
    registros_saida: int = 0
    resultado: ResultadoValidacaoMerge = field(default_factory=ResultadoValidacaoMerge)


class LocalizadorArquivosParquet:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def localizar(self, pasta_origem: Path) -> list[Path]:
        if not pasta_origem.exists() or not pasta_origem.is_dir():
            self._logger.error("Pasta de origem invalida: %s", pasta_origem)
            return []

        arquivos = sorted(pasta_origem.glob("*.parquet"))
        self._logger.info("Arquivos parquet encontrados: %s", len(arquivos))
        for caminho_arquivo in arquivos:
            self._logger.info("Arquivo localizado: %s", caminho_arquivo.name)
        return arquivos


class LeitorParquet:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def ler_metadados(self, caminho_arquivo: Path) -> MetadadosArquivoParquet:
        self._logger.info("Lendo metadados de %s", caminho_arquivo.name)
        parquet = pq.ParquetFile(caminho_arquivo)
        return MetadadosArquivoParquet(
            caminho_arquivo=caminho_arquivo,
            colunas=list(parquet.schema.names),
            quantidade_registros=parquet.metadata.num_rows,
        )


class UnificadorParquet:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def unificar(self, arquivos_origem: list[Path], arquivo_saida: Path) -> None:
        if not arquivos_origem:
            raise RuntimeError("Nenhum arquivo valido disponivel para merge")

        self._logger.info("Iniciando merge de %s arquivo(s)", len(arquivos_origem))
        consulta = self._montar_consulta(arquivos_origem)
        self._executar_merge(consulta, arquivo_saida)
        self._logger.info("Merge concluido em %s", arquivo_saida)

    def _montar_consulta(self, arquivos_origem: list[Path]) -> str:
        arquivos_sql = ", ".join(self._sql_quote(str(caminho)) for caminho in arquivos_origem)
        return f"SELECT * FROM read_parquet([{arquivos_sql}], union_by_name=true)"

    def _executar_merge(self, consulta: str, arquivo_saida: Path) -> None:
        import duckdb

        conexao = duckdb.connect()
        try:
            comando = (
                f"COPY ({consulta}) TO {self._sql_quote(str(arquivo_saida))} "
                f"(FORMAT PARQUET, COMPRESSION 'snappy')"
            )
            conexao.execute(comando)
        finally:
            conexao.close()

    def _sql_quote(self, valor: str) -> str:
        return "'" + valor.replace("'", "''") + "'"


class ValidadorMerge:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def validar(self, contexto: ContextoMerge) -> None:
        contexto.resultado.colunas_mantidas = self._status(self._colunas_conferem(contexto))
        contexto.resultado.registros_conferem = self._status(self._registros_conferem(contexto))
        contexto.resultado.integridade_confirmada = self._status(self._integridade_confirmada(contexto))
        self._logger.info("Validacao do merge concluida")

    def _colunas_conferem(self, contexto: ContextoMerge) -> bool:
        colunas_origem = self._colunas_origem(contexto.arquivos_validos)
        return colunas_origem == sorted(contexto.colunas_saida)

    def _registros_conferem(self, contexto: ContextoMerge) -> bool:
        registros_origem = sum(item.quantidade_registros for item in contexto.arquivos_validos)
        return registros_origem == contexto.registros_saida

    def _integridade_confirmada(self, contexto: ContextoMerge) -> bool:
        itens = (
            contexto.resultado.pasta_origem_validada,
            contexto.resultado.pasta_destino_validada,
            contexto.resultado.arquivos_localizados,
            contexto.resultado.leitura_realizada,
            contexto.resultado.merge_realizado,
            contexto.resultado.arquivo_final_gerado,
            contexto.resultado.colunas_mantidas,
            contexto.resultado.registros_conferem,
        )
        return all(item == "OK" for item in itens)

    def _colunas_origem(self, arquivos_validos: list[MetadadosArquivoParquet]) -> list[str]:
        colunas: set[str] = set()
        for metadados in arquivos_validos:
            colunas.update(metadados.colunas)
        return sorted(colunas)

    def _status(self, condicao: bool) -> str:
        if condicao:
            return "OK"
        return "ERRO"


class GeradorRelatorioHtml:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def gerar(self, resultado: ResultadoValidacaoMerge, caminho_saida: Path) -> None:
        caminho_saida.write_text(self._montar_html(resultado), encoding="utf-8")
        self._logger.info("Relatorio HTML salvo em %s", caminho_saida)

    def _montar_html(self, resultado: ResultadoValidacaoMerge) -> str:
        checklist = [
            ("Pasta origem validada", resultado.pasta_origem_validada),
            ("Pasta destino criada/validada", resultado.pasta_destino_validada),
            ("Arquivos localizados", resultado.arquivos_localizados),
            ("Leitura realizada", resultado.leitura_realizada),
            ("Merge realizado", resultado.merge_realizado),
            ("Arquivo final gerado", resultado.arquivo_final_gerado),
            ("Colunas mantidas", resultado.colunas_mantidas),
            ("Registros conferem", resultado.registros_conferem),
            ("Integridade confirmada", resultado.integridade_confirmada),
        ]
        itens = "\n".join(self._montar_item(rotulo, status) for rotulo, status in checklist)
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Relatorio de Validacao do Merge</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f5f5f5; color: #222; }}
    .bloco {{ background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    ul {{ list-style: none; padding-left: 0; }}
    li {{ padding: 4px 0; }}
    .ok {{ color: #137333; font-weight: bold; }}
    .erro {{ color: #b3261e; font-weight: bold; }}
  </style>
</head>
<body>
  <div class="bloco">
    <h1>Relatorio de Validacao do Merge</h1>
    <ul>
      {itens}
    </ul>
  </div>
</body>
</html>"""

    def _montar_item(self, rotulo: str, status: str) -> str:
        classe = "ok" if status == "OK" else "erro"
        return f'<li>{rotulo}: <span class="{classe}">{status}</span></li>'


class OrquestradorMergeParquet:
    def __init__(
        self,
        logger: logging.Logger,
        localizador: LocalizadorArquivosParquet,
        leitor: LeitorParquet,
        unificador: UnificadorParquet,
        validador: ValidadorMerge,
        gerador_relatorio: GeradorRelatorioHtml,
    ) -> None:
        self._logger = logger
        self._localizador = localizador
        self._leitor = leitor
        self._unificador = unificador
        self._validador = validador
        self._gerador_relatorio = gerador_relatorio

    def executar(self, argumentos: ArgumentosExecucao) -> None:
        contexto = ContextoMerge()
        contexto.resultado.pasta_origem_validada = self._status_pasta_origem(argumentos.pasta_origem)
        contexto.resultado.pasta_destino_validada = self._preparar_pasta_destino(argumentos.pasta_destino)
        self._logar_inicio(argumentos)

        contexto.arquivos_localizados = self._localizador.localizar(argumentos.pasta_origem)
        contexto.resultado.arquivos_localizados = self._status(bool(contexto.arquivos_localizados))
        contexto.arquivo_saida = argumentos.pasta_destino / "parquet_unificado.parquet"

        self._ler_arquivos(contexto)
        self._realizar_merge(contexto)
        self._validar_saida(contexto)
        self._gerar_relatorio(contexto, argumentos.pasta_destino)

    def _logar_inicio(self, argumentos: ArgumentosExecucao) -> None:
        self._logger.info("Inicio da execucao do merge de parquet")
        self._logger.info("Parametro pasta_origem=%s", argumentos.pasta_origem)
        self._logger.info("Parametro pasta_destino=%s", argumentos.pasta_destino)

    def _status_pasta_origem(self, pasta_origem: Path) -> str:
        if pasta_origem.exists() and pasta_origem.is_dir():
            return "OK"
        return "ERRO"

    def _preparar_pasta_destino(self, pasta_destino: Path) -> str:
        pasta_destino.mkdir(parents=True, exist_ok=True)
        if pasta_destino.exists() and pasta_destino.is_dir():
            return "OK"
        return "ERRO"

    def _ler_arquivos(self, contexto: ContextoMerge) -> None:
        for caminho_arquivo in contexto.arquivos_localizados:
            try:
                contexto.arquivos_validos.append(self._leitor.ler_metadados(caminho_arquivo))
            except Exception:
                self._logger.exception("Erro ao ler %s", caminho_arquivo.name)
        contexto.resultado.leitura_realizada = self._status(bool(contexto.arquivos_validos))

    def _realizar_merge(self, contexto: ContextoMerge) -> None:
        caminhos_validos = [item.caminho_arquivo for item in contexto.arquivos_validos]
        try:
            self._unificador.unificar(caminhos_validos, contexto.arquivo_saida)
            contexto.resultado.merge_realizado = "OK"
        except Exception:
            self._logger.exception("Erro durante o merge dos arquivos parquet")
            return
        contexto.resultado.arquivo_final_gerado = self._status(contexto.arquivo_saida.exists())

    def _validar_saida(self, contexto: ContextoMerge) -> None:
        if contexto.resultado.arquivo_final_gerado != "OK":
            return
        try:
            metadados_saida = self._leitor.ler_metadados(contexto.arquivo_saida)
            contexto.colunas_saida = metadados_saida.colunas
            contexto.registros_saida = metadados_saida.quantidade_registros
            self._logger.info("Validando colunas e quantidade de registros")
            self._validador.validar(contexto)
        except Exception:
            self._logger.exception("Erro durante a validacao do parquet final")

    def _gerar_relatorio(self, contexto: ContextoMerge, pasta_destino: Path) -> None:
        caminho_relatorio = pasta_destino / "relatorio_validacao_merge.html"
        self._gerador_relatorio.gerar(contexto.resultado, caminho_relatorio)

    def _status(self, condicao: bool) -> str:
        if condicao:
            return "OK"
        return "ERRO"


def main() -> None:
    argumentos = ArgumentosExecucao.criar_do_cli()
    argumentos.pasta_destino.mkdir(parents=True, exist_ok=True)
    logger = LoggerAplicacao(argumentos.pasta_destino).criar_logger()
    localizador = LocalizadorArquivosParquet(logger)
    leitor = LeitorParquet(logger)
    unificador = UnificadorParquet(logger)
    validador = ValidadorMerge(logger)
    gerador_relatorio = GeradorRelatorioHtml(logger)
    orquestrador = OrquestradorMergeParquet(
        logger=logger,
        localizador=localizador,
        leitor=leitor,
        unificador=unificador,
        validador=validador,
        gerador_relatorio=gerador_relatorio,
    )
    orquestrador.executar(argumentos)


if __name__ == "__main__":
    main()
