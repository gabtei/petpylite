"""
reports.py
----------
Camada de geração e exportação de relatórios tabulares em formato CSV.
Utiliza exclusivamente a biblioteca padrão do Python (csv, pathlib)
garantindo leveza, independência de bibliotecas externas e alta compatibilidade.
"""

from pathlib import Path
import sqlite3
import csv
from typing import List, Optional, Union

try:
    from database import DIRETORIO_RAIZ
    import queries
except ImportError:
    from src.database import DIRETORIO_RAIZ
    from src import queries

# Diretório padrão onde os relatórios CSV serão gravados
DIRETORIO_RELATORIOS = DIRETORIO_RAIZ / "relatorios"


def exportar_para_csv(
    registros: List[sqlite3.Row],
    caminho_arquivo: Union[Path, str]
) -> Path:
    """
    Exporta uma lista de registros sqlite3.Row para um arquivo CSV.
    
    - Cria os diretórios pais caso não existam.
    - Utiliza codificação utf-8-sig para compatibilidade direta com Microsoft Excel e editores de texto.
    - Retorna o objeto Path apontando para o arquivo gerado.
    """
    caminho_destino = Path(caminho_arquivo)
    caminho_destino.parent.mkdir(parents=True, exist_ok=True)

    if not registros:
        # Se não houver registros, cria arquivo vazio ou com aviso
        with caminho_destino.open("w", encoding="utf-8-sig", newline="") as f:
            f.write("")
        return caminho_destino

    colunas = list(registros[0].keys())

    with caminho_destino.open("w", encoding="utf-8-sig", newline="") as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=";")
        escritor.writerow(colunas)

        for linha in registros:
            escritor.writerow([linha[col] if linha[col] is not None else "" for col in colunas])

    return caminho_destino


def exportar_relatorio_faturamento(
    conexao: sqlite3.Connection,
    caminho_destino: Optional[Union[Path, str]] = None
) -> Path:
    """
    Gera o relatório analítico consolidado de faturamento de consultas (VIEW vw_resumo_consultas)
    e grava em formato CSV.
    """
    if caminho_destino is None:
        caminho_destino = DIRETORIO_RELATORIOS / "relatorio_faturamento_consultas.csv"

    registros = queries.faturamento_geral_consultas(conexao)
    return exportar_para_csv(registros, caminho_destino)


def exportar_relatorio_atendimentos(
    conexao: sqlite3.Connection,
    caminho_destino: Optional[Union[Path, str]] = None
) -> Path:
    """
    Gera o relatório com o prontuário completo de atendimentos clínicos (5 tabelas integradas)
    e grava em formato CSV.
    """
    if caminho_destino is None:
        caminho_destino = DIRETORIO_RELATORIOS / "relatorio_atendimentos_completos.csv"

    registros = queries.relatorio_atendimentos_completos(conexao)
    return exportar_para_csv(registros, caminho_destino)

