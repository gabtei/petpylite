"""
queries.py
----------
Camada de consultas analíticas e operacionais da clínica Pet Care.
Centraliza as instruções SQL estruturadas em funções reutilizáveis,
retornando conjuntos de dados manipuláveis (sqlite3.Row).

Competências SQL aplicadas:
- Projeção e restrição (SELECT com WHERE parametrizado)
- Junções relacionais (INNER JOIN / LEFT JOIN)
- Agrupamento e métricas de agregação (COUNT, SUM, AVG, GROUP BY, HAVING)
- Ordenação e paginação (ORDER BY, LIMIT)
- Consumo de VIEW analítica pré-compilada
"""

import sqlite3
from typing import List


def buscar_catalogo_medicamentos(conexao: sqlite3.Connection) -> List[sqlite3.Row]:
    """Retorna todo o estoque de insumos e medicamentos ordenado por tipo e nome."""
    comando = """
        SELECT id, nome, tipo, preco, estoque
        FROM medicamentos
        ORDER BY tipo ASC, nome ASC;
    """
    return conexao.execute(comando).fetchall()


def filtrar_animais_por_especie(conexao: sqlite3.Connection, especie: str) -> List[sqlite3.Row]:
    """Filtra animais por espécie trazendo o respectivo dono e contato (WHERE parametrizado + JOIN)."""
    comando = """
        SELECT 
            a.id          AS pet_id,
            a.nome        AS pet_nome,
            a.especie     AS especie,
            a.peso        AS peso_kg,
            d.nome        AS dono_nome,
            d.telefone    AS telefone_contato
        FROM animais a
        INNER JOIN donos d ON d.id = a.dono_id
        WHERE a.especie = ?
        ORDER BY a.nome ASC;
    """
    return conexao.execute(comando, (especie,)).fetchall()


def relatorio_atendimentos_completos(conexao: sqlite3.Connection) -> List[sqlite3.Row]:
    """
    Gera o prontuário detalhado de cada aplicação clínica unindo 5 tabelas:
    consultas -> animais -> donos -> itens_consulta -> medicamentos.
    """
    comando = """
        SELECT 
            c.id                     AS consulta_id,
            c.data_consulta          AS data_atendimento,
            d.nome                   AS dono,
            a.nome                   AS pet,
            c.motivo                 AS diagnostico_motivo,
            m.nome                   AS insumo_aplicado,
            ic.quantidade            AS qtd_administrada,
            ic.valor_unitario        AS custo_unidade,
            (ic.quantidade * ic.valor_unitario) AS subtotal_medicamento
        FROM consultas c
        INNER JOIN animais a         ON a.id = c.animal_id
        INNER JOIN donos d           ON d.id = a.dono_id
        INNER JOIN itens_consulta ic ON ic.consulta_id = c.id
        INNER JOIN medicamentos m    ON m.id = ic.medicamento_id
        ORDER BY c.data_consulta DESC, c.id DESC;
    """
    return conexao.execute(comando).fetchall()


def metricas_por_dono(conexao: sqlite3.Connection) -> List[sqlite3.Row]:
    """Calcula quantidade de pets cadastrados e volume de consultas realizadas por dono."""
    comando = """
        SELECT 
            d.nome                       AS dono,
            d.email                      AS contato_email,
            COUNT(DISTINCT a.id)         AS total_pets,
            COUNT(DISTINCT c.id)         AS total_consultas,
            COALESCE(SUM(c.valor_consulta), 0) AS total_gasto_consultas
        FROM donos d
        LEFT JOIN animais a   ON a.dono_id = d.id
        LEFT JOIN consultas c ON c.animal_id = a.id
        GROUP BY d.id, d.nome, d.email
        ORDER BY total_consultas DESC, dono ASC;
    """
    return conexao.execute(comando).fetchall()


def estatisticas_peso_por_especie(conexao: sqlite3.Connection) -> List[sqlite3.Row]:
    """Média de peso, peso mínimo e máximo agrupados por espécie de animal (AVG, MIN, MAX, COUNT)."""
    comando = """
        SELECT 
            especie,
            COUNT(id)         AS total_cadastrado,
            ROUND(AVG(peso), 2) AS peso_medio_kg,
            MIN(peso)         AS menor_peso_kg,
            MAX(peso)         AS maior_peso_kg
        FROM animais
        GROUP BY especie
        ORDER BY total_cadastrado DESC;
    """
    return conexao.execute(comando).fetchall()


def insumos_mais_utilizados(conexao: sqlite3.Connection, top_n: int = 3) -> List[sqlite3.Row]:
    """Ranking dos medicamentos/vacinas com maior saída nos atendimentos clínicos."""
    comando = """
        SELECT 
            m.nome                     AS medicamento,
            m.tipo                     AS classificacao,
            SUM(ic.quantidade)         AS total_aplicado,
            SUM(ic.quantidade * ic.valor_unitario) AS receita_gerada
        FROM itens_consulta ic
        INNER JOIN medicamentos m ON m.id = ic.medicamento_id
        GROUP BY m.id, m.nome, m.tipo
        ORDER BY total_aplicado DESC
        LIMIT ?;
    """
    return conexao.execute(comando, (top_n,)).fetchall()


def faturamento_geral_consultas(conexao: sqlite3.Connection) -> List[sqlite3.Row]:
    """Consome a VIEW vw_resumo_consultas criada no schema.sql para exibição dos fechamentos."""
    comando = """
        SELECT 
            consulta_id,
            data,
            dono,
            pet,
            especie,
            valor_base,
            total_medicamentos,
            custo_total
        FROM vw_resumo_consultas
        ORDER BY data DESC;
    """
    return conexao.execute(comando).fetchall()