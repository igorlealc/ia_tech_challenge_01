from __future__ import annotations

import csv
from pathlib import Path

import pyarrow.parquet as pq


# Base principal: Informe Técnico SIASUS 2019/07 (DATASUS), seção 2.3 (PAUFAAMM.DBF)
# Link: https://rfsaldanha.github.io/sis/assets/sia/Informe_Tecnico_SIASUS_2019_07.pdf
FIELD_DICT: dict[str, tuple[str, str]] = {
    "PA_CODUNI": ("Código do estabelecimento no CNES", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_GESTAO": ("Código UF+município do gestor (ou UF0000 sob gestão estadual)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CONDIC": ("Sigla do tipo de gestão habilitada", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_UFMUN": ("Código UF+município de localização do estabelecimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_REGCT": ("Código da regra contratual", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_INCOUT": ("Incremento outros", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_INCURG": ("Incremento urgência", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_TPUPS": ("Tipo de estabelecimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_TIPPRE": ("Tipo de prestador", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_MN_IND": ("Indicador mantido/individual", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CNPJCPF": ("CNPJ do estabelecimento executante", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CNPJMNT": ("CNPJ da mantenedora", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CNPJ_CC": ("CNPJ do órgão que recebeu por cessão de crédito", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_MVM": ("Data de processamento/movimento (AAAAMM)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CMP": ("Competência de realização do procedimento (AAAAMM)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_PROC_ID": ("Código do procedimento ambulatorial", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_TPFIN": ("Tipo de financiamento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_SUBFIN": ("Subtipo de financiamento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_NIVCPL": ("Complexidade do procedimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_DOCORIG": ("Instrumento de registro (P/S/C/A/B/I)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_AUTORIZ": ("Número da APAC/autorização BPA-I", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CNSMED": ("CNS do profissional executante", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CBOCOD": ("Código CBO da ocupação do profissional", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_MOTSAI": ("Motivo de saída", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_OBITO": ("Indicador de óbito (APAC)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_ENCERR": ("Indicador de encerramento (APAC)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_PERMAN": ("Indicador de permanência (APAC)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_ALTA": ("Indicador de alta (APAC)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_TRANSF": ("Indicador de transferência (APAC)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CIDPRI": ("CID principal", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CIDSEC": ("CID secundário", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CIDCAS": ("CID causas associadas", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CATEND": ("Caráter de atendimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_IDADE": ("Idade do paciente", "DATASUS Informe Técnico SIASUS 2019/07"),
    "IDADEMIN": ("Idade mínima para o procedimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "IDADEMAX": ("Idade máxima para o procedimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_FLIDADE": ("Compatibilidade da idade com regra SIGTAP", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_SEXO": ("Sexo do paciente", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_RACACOR": ("Raça/cor do paciente", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_MUNPCN": ("UF+município de residência do paciente", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_QTDPRO": ("Quantidade produzida/apresentada", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_QTDAPR": ("Quantidade aprovada", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_VALPRO": ("Valor produzido/apresentado", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_VALAPR": ("Valor aprovado", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_UFDIF": ("Indicador UF de residência diferente da UF do estabelecimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_MNDIF": ("Indicador município de residência diferente do município do estabelecimento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_DIF_VAL": ("Diferença de valor unitário tabela unificada x gestor x quantidade aprovada", "DATASUS Informe Técnico SIASUS 2019/07"),
    "NU_VPA_TOT": ("Valor unitário do procedimento na tabela VPA", "DATASUS Informe Técnico SIASUS 2019/07"),
    "NU_PA_TOT": ("Valor unitário do procedimento na tabela SIGTAP", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_INDICA": ("Indicativo da situação da produção (0 não aprovado, 5 aprovado total, 6 parcial)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_CODOCO": ("Código de ocorrência", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_FLQT": ("Indicador de erro de quantidade produzida", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_FLER": ("Indicador de erro de corpo da APAC", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_ETNIA": ("Etnia do paciente", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_VL_CF": ("Valor do complemento federal", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_VL_CL": ("Valor do complemento local", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_VL_INC": ("Valor do incremento", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_SRV_C": ("Código do serviço especializado/classificação CBO (em alguns layouts aparece como PA_SRC_C)", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_INE": ("Código de Identificação Nacional de Equipes", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_NAT_JUR": ("Código da natureza jurídica", "DATASUS Informe Técnico SIASUS 2019/07"),
    "PA_FNTORC": ("Fonte orçamentária/fonte de recurso da produção (inferido pelo nome do campo; validar no informe técnico mais recente)", "Inferência técnica"),
    "filename": ("Coluna técnica gerada na leitura de parquet com caminho do arquivo de origem", "Pipeline local (DuckDB/PyArrow)"),
    "arquivo_origem": ("Coluna adicionada no merge para rastrear origem (PARJ2506a/parj2506b)", "Pipeline local (merge_parquet_fase2.py)"),
}


def main() -> None:
    merged = Path('/workspace/trabalho/parquet/merged.parquet')
    out_csv = Path('/workspace/trabalho/dicionario_dados_merged.csv')
    out_md = Path('/workspace/trabalho/dicionario_dados_merged.md')

    pf = pq.ParquetFile(merged)
    cols = pf.schema_arrow.names

    rows = []
    for i, col in enumerate(cols, start=1):
        desc, src = FIELD_DICT.get(col, ("Descrição não mapeada automaticamente", "Não mapeado"))
        rows.append({
            'ordem_no_arquivo': i,
            'coluna': col,
            'descricao': desc,
            'fonte': src,
        })

    with out_csv.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ordem_no_arquivo', 'coluna', 'descricao', 'fonte'])
        writer.writeheader()
        writer.writerows(rows)

    with out_md.open('w', encoding='utf-8') as f:
        f.write('# Dicionário de Dados - merged.parquet\n\n')
        f.write('Base principal: Informe Técnico SIASUS 2019/07 (DATASUS), seção 2.3 (PAUFAAMM.DBF).\n\n')
        f.write('| Ordem | Coluna | Descrição | Fonte |\n')
        f.write('|---:|---|---|---|\n')
        for r in rows:
            f.write(f"| {r['ordem_no_arquivo']} | {r['coluna']} | {r['descricao']} | {r['fonte']} |\n")

    print(f'CSV: {out_csv}')
    print(f'MD:  {out_md}')


if __name__ == '__main__':
    main()
