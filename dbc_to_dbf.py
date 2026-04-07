from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from datasus_dbc import decompress as datasus_dbc_decompress
except Exception:  # pragma: no cover
    datasus_dbc_decompress = None


@dataclass(frozen=True)
class ArgumentosExecucao:
    pasta_origem: Path
    pasta_destino: Path

    @classmethod
    def criar_do_cli(cls) -> "ArgumentosExecucao":
        parser = argparse.ArgumentParser(
            description="Converte arquivos DBC para DBF em lote."
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
        self._arquivo_log = pasta_destino / "conversao_dbc_dbf.log"

    @property
    def arquivo_log(self) -> Path:
        return self._arquivo_log

    def criar_logger(self) -> logging.Logger:
        logger = logging.getLogger("dbc_to_dbf")
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
class ResultadoArquivo:
    nome_dbc: str
    nome_dbf: str | None = None
    status: str = "PENDENTE"
    mensagem: str = ""


@dataclass
class RelatorioExecucao:
    itens: list[ResultadoArquivo] = field(default_factory=list)

    def adicionar(self, item: ResultadoArquivo) -> None:
        self.itens.append(item)

    @property
    def quantidade_sucesso(self) -> int:
        return sum(1 for item in self.itens if item.status == "OK")

    @property
    def quantidade_erro(self) -> int:
        return sum(1 for item in self.itens if item.status == "ERRO")


class ConversorDbcParaDbf:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._comando_blast = shutil.which("blast-dbf")
        self._comando_dbc2dbf = shutil.which("dbc2dbf")

    def validar_dependencias(self) -> None:
        if datasus_dbc_decompress is not None:
            return
        if self._comando_blast is not None:
            return
        if self._comando_dbc2dbf is not None:
            return
        raise RuntimeError(
            "Nenhum backend de conversao DBC -> DBF foi encontrado. "
            "Instale o pacote Python 'datasus-dbc' ou disponibilize "
            "'blast-dbf' ou 'dbc2dbf' no PATH."
        )

    def converter_arquivo(self, caminho_dbc: Path, pasta_destino: Path) -> Path:
        pasta_destino.mkdir(parents=True, exist_ok=True)
        caminho_dbf = pasta_destino / f"{caminho_dbc.stem}.dbf"
        inicio = time.perf_counter()

        backend = self._selecionar_backend()
        self._logger.info("Convertendo %s com backend=%s", caminho_dbc.name, backend)

        if backend == "datasus_dbc":
            self._converter_com_datasus_dbc(caminho_dbc, caminho_dbf)
        elif backend == "blast-dbf":
            self._converter_com_blast_dbf(caminho_dbc, pasta_destino, caminho_dbf)
        else:
            self._converter_com_dbc2dbf(caminho_dbc, caminho_dbf)

        if not caminho_dbf.exists():
            raise RuntimeError(
                f"Conversao concluida sem gerar o arquivo esperado: {caminho_dbf.name}"
            )
        duracao = time.perf_counter() - inicio
        tamanho_mb = caminho_dbf.stat().st_size / (1024 * 1024)
        self._logger.info(
            "Arquivo convertido %s -> %s | backend=%s | %.2fs | %.2f MB",
            caminho_dbc.name,
            caminho_dbf.name,
            backend,
            duracao,
            tamanho_mb,
        )
        return caminho_dbf

    def _selecionar_backend(self) -> str:
        if datasus_dbc_decompress is not None:
            return "datasus_dbc"
        if self._comando_blast is not None:
            return "blast-dbf"
        if self._comando_dbc2dbf is not None:
            return "dbc2dbf"
        raise RuntimeError("Nenhum backend disponivel para conversao.")

    def _converter_com_datasus_dbc(self, caminho_dbc: Path, caminho_dbf: Path) -> None:
        datasus_dbc_decompress(str(caminho_dbc), str(caminho_dbf))

    def _converter_com_blast_dbf(
        self,
        caminho_dbc: Path,
        pasta_destino: Path,
        caminho_dbf: Path,
    ) -> None:
        antes = {arquivo.resolve() for arquivo in pasta_destino.glob("*.dbf")}
        subprocess.run(
            [self._comando_blast, str(caminho_dbc), str(pasta_destino)],
            check=True,
            capture_output=True,
            text=True,
        )
        dbf_gerado = self._localizar_dbf_gerado(caminho_dbc, pasta_destino, antes)
        if dbf_gerado.resolve() != caminho_dbf.resolve():
            dbf_gerado.replace(caminho_dbf)

    def _converter_com_dbc2dbf(self, caminho_dbc: Path, caminho_dbf: Path) -> None:
        subprocess.run(
            [self._comando_dbc2dbf, str(caminho_dbc), str(caminho_dbf)],
            check=True,
            capture_output=True,
            text=True,
        )

    def _localizar_dbf_gerado(
        self,
        caminho_dbc: Path,
        pasta_destino: Path,
        arquivos_antes: set[Path],
    ) -> Path:
        stem_normalizado = caminho_dbc.stem.lower()
        candidatos = [
            arquivo
            for arquivo in pasta_destino.glob("*.dbf")
            if arquivo.stem.lower() == stem_normalizado
        ]
        if candidatos:
            return max(candidatos, key=lambda arquivo: arquivo.stat().st_mtime)

        arquivos_depois = {arquivo.resolve() for arquivo in pasta_destino.glob("*.dbf")}
        novos = sorted(arquivos_depois - arquivos_antes, key=lambda arquivo: arquivo.stat().st_mtime)
        if len(novos) == 1:
            return novos[0]

        raise FileNotFoundError(f"Nao foi possivel localizar o DBF gerado para {caminho_dbc.name}")


class OrquestradorConversao:
    def __init__(self, logger: logging.Logger, conversor: ConversorDbcParaDbf) -> None:
        self._logger = logger
        self._conversor = conversor

    def executar(self, argumentos: ArgumentosExecucao) -> RelatorioExecucao:
        self._validar_pastas(argumentos)
        argumentos.pasta_destino.mkdir(parents=True, exist_ok=True)
        relatorio = RelatorioExecucao()
        arquivos_dbc = self._listar_arquivos_dbc(argumentos.pasta_origem)

        self._logger.info("Inicio do processamento")
        self._logger.info("Pasta de origem: %s", argumentos.pasta_origem)
        self._logger.info("Pasta de destino: %s", argumentos.pasta_destino)

        self._conversor.validar_dependencias()

        if not arquivos_dbc:
            self._logger.warning("Nenhum arquivo DBC encontrado em %s", argumentos.pasta_origem)
            return relatorio

        self._logger.info("Arquivos DBC localizados: %s", len(arquivos_dbc))
        for caminho_dbc in arquivos_dbc:
            relatorio.adicionar(self._processar_arquivo(caminho_dbc, argumentos.pasta_destino))

        self._registrar_resumo(relatorio)
        return relatorio

    def _validar_pastas(self, argumentos: ArgumentosExecucao) -> None:
        if not argumentos.pasta_origem.exists():
            raise FileNotFoundError(f"Pasta de origem nao encontrada: {argumentos.pasta_origem}")
        if not argumentos.pasta_origem.is_dir():
            raise NotADirectoryError(f"Pasta de origem invalida: {argumentos.pasta_origem}")

    def _listar_arquivos_dbc(self, pasta_origem: Path) -> list[Path]:
        arquivos = list(pasta_origem.glob("*.dbc"))
        arquivos.extend(pasta_origem.glob("*.DBC"))
        return sorted(set(arquivos))

    def _processar_arquivo(self, caminho_dbc: Path, pasta_destino: Path) -> ResultadoArquivo:
        resultado = ResultadoArquivo(nome_dbc=caminho_dbc.name)
        try:
            dbf_gerado = self._conversor.converter_arquivo(caminho_dbc, pasta_destino)
            resultado.nome_dbf = dbf_gerado.name
            resultado.status = "OK"
            resultado.mensagem = "Conversao concluida com sucesso."
        except subprocess.CalledProcessError as erro:
            stderr = (erro.stderr or "").strip()
            resultado.status = "ERRO"
            resultado.mensagem = stderr or f"Falha ao executar {erro.cmd!r}."
            self._logger.exception("Falha na conversao de %s", caminho_dbc.name)
        except Exception as erro:
            resultado.status = "ERRO"
            resultado.mensagem = str(erro)
            self._logger.exception("Erro ao processar %s", caminho_dbc.name)
        return resultado

    def _registrar_resumo(self, relatorio: RelatorioExecucao) -> None:
        self._logger.info("Resumo final")
        self._logger.info("Arquivos convertidos com sucesso: %s", relatorio.quantidade_sucesso)
        self._logger.info("Arquivos com erro: %s", relatorio.quantidade_erro)
        for item in relatorio.itens:
            if item.status == "OK":
                self._logger.info("OK | %s -> %s", item.nome_dbc, item.nome_dbf)
            else:
                self._logger.error("ERRO | %s | %s", item.nome_dbc, item.mensagem)


def main() -> None:
    argumentos = ArgumentosExecucao.criar_do_cli()
    argumentos.pasta_destino.mkdir(parents=True, exist_ok=True)
    logger = LoggerAplicacao(argumentos.pasta_destino).criar_logger()
    conversor = ConversorDbcParaDbf(logger)
    orquestrador = OrquestradorConversao(logger, conversor)

    try:
        orquestrador.executar(argumentos)
    except Exception:
        logger.exception("Falha geral na execucao")
        raise SystemExit(1)
    finally:
        logger.info("Log final salvo em %s", argumentos.pasta_destino / "conversao_dbc_dbf.log")


if __name__ == "__main__":
    main()
