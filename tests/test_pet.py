"""
test_pet.py
-----------
Suíte de testes automatizados com pytest para o projeto Petpylite Care.
Cobre:
- Configuração do banco de dados e integridade referencial (FK CASCADE, CHECK constraints)
- Camada de consultas analíticas (src/queries.py)
- Camada de exportação de relatórios em CSV (src/reports.py)
"""

from pathlib import Path
import sqlite3
import csv
import pytest

# Adiciona o diretório src ao path se necessário
import sys
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_SRC = DIRETORIO_RAIZ / "src"
if str(DIRETORIO_SRC) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_SRC))

import database
import queries
import reports


# =====================================================================
# Fixtures do Pytest
# =====================================================================

@pytest.fixture
def banco_teste():
    """
    Cria uma conexão SQLite isolada em memória (:memory:),
    carregando o schema DDL e os dados de seed DML para cada teste.
    Garante integridade referencial ativa e mapeamento nominal sqlite3.Row.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    caminho_schema = DIRETORIO_RAIZ / "data" / "schema.sql"
    caminho_seed = DIRETORIO_RAIZ / "data" / "seed.sql"

    conn.executescript(caminho_schema.read_text(encoding="utf-8"))
    conn.executescript(caminho_seed.read_text(encoding="utf-8"))
    conn.commit()

    yield conn
    conn.close()


# =====================================================================
# 1. Testes Estruturais e Regras de Integridade do Banco de Dados
# =====================================================================

def test_tabelas_e_views_criadas(banco_teste):
    """Verifica se todas as 5 tabelas e a view analítica foram devidamente criadas."""
    cursor = banco_teste.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');"
    )
    objetos = {row["name"] for row in cursor.fetchall()}

    tabelas_esperadas = {"donos", "animais", "medicamentos", "consultas", "itens_consulta"}
    assert tabelas_esperadas.issubset(objetos), f"Faltando tabelas: {tabelas_esperadas - objetos}"
    assert "vw_resumo_consultas" in objetos, "A VIEW vw_resumo_consultas não foi encontrada."


def test_restricao_check_especie_animal(banco_teste):
    """Valida que a tabela de animais rejeita espécies não autorizadas pelo CHECK."""
    with pytest.raises(sqlite3.IntegrityError):
        banco_teste.execute(
            "INSERT INTO animais (dono_id, nome, especie, peso) VALUES (1, 'Loro', 'Papagaio', 0.5);"
        )


def test_restricao_check_peso_positivo(banco_teste):
    """Valida que a tabela de animais rejeita peso <= 0."""
    with pytest.raises(sqlite3.IntegrityError):
        banco_teste.execute(
            "INSERT INTO animais (dono_id, nome, especie, peso) VALUES (1, 'Fantasma', 'Cachorro', -2.5);"
        )


def test_restricao_email_unico_dono(banco_teste):
    """Garante que não é permitido cadastrar dois donos com o mesmo e-mail (UNIQUE)."""
    with pytest.raises(sqlite3.IntegrityError):
        banco_teste.execute(
            "INSERT INTO donos (nome, telefone, email) VALUES ('Clone', '99999-9999', 'ana.sousa@email.com');"
        )


def test_delecao_em_cascata_dono(banco_teste):
    """Valida que a exclusão de um dono remove em cascata seus pets e consultas associadas."""
    # Dono 1 possui pets cadastrados
    pets_antes = banco_teste.execute("SELECT COUNT(*) AS total FROM animais WHERE dono_id = 1;").fetchone()["total"]
    assert pets_antes > 0

    # Remove o Dono 1
    banco_teste.execute("DELETE FROM donos WHERE id = 1;")
    banco_teste.commit()

    # Confirma deleção em cascata
    pets_depois = banco_teste.execute("SELECT COUNT(*) AS total FROM animais WHERE dono_id = 1;").fetchone()["total"]
    assert pets_depois == 0


# =====================================================================
# 2. Testes das Consultas Analíticas (queries.py)
# =====================================================================

def test_buscar_catalogo_medicamentos(banco_teste):
    """Testa a recuperação ordenada do catálogo de medicamentos."""
    medicamentos = queries.buscar_catalogo_medicamentos(banco_teste)
    assert len(medicamentos) == 6
    # Verifica chaves presentes na linha
    chaves = list(medicamentos[0].keys())
    for col in ("id", "nome", "tipo", "preco", "estoque"):
        assert col in chaves


def test_filtrar_animais_por_especie(banco_teste):
    """Testa a filtragem por espécie e o vínculo com os dados do dono."""
    caes = queries.filtrar_animais_por_especie(banco_teste, "Cachorro")
    assert len(caes) == 3
    for pet in caes:
        assert pet["especie"] == "Cachorro"
        assert pet["dono_nome"] is not None
        assert pet["telefone_contato"] is not None

    gatos = queries.filtrar_animais_por_especie(banco_teste, "Gato")
    assert len(gatos) == 2


def test_relatorio_atendimentos_completos(banco_teste):
    """Testa o prontuário que une consultas, animais, donos, itens e medicamentos."""
    atendimentos = queries.relatorio_atendimentos_completos(banco_teste)
    assert len(atendimentos) == 8  # 8 registros em itens_consulta no seed
    primeiro = atendimentos[0]
    assert "consulta_id" in primeiro.keys()
    assert "dono" in primeiro.keys()
    assert "pet" in primeiro.keys()
    assert "insumo_aplicado" in primeiro.keys()
    assert "subtotal_medicamento" in primeiro.keys()
    # Subtotal deve ser igual a quantidade * custo_unidade
    for item in atendimentos:
        esperado = round(item["qtd_administrada"] * item["custo_unidade"], 2)
        assert round(item["subtotal_medicamento"], 2) == esperado


def test_metricas_por_dono(banco_teste):
    """Testa o cálculo de métricas agregadas agrupadas por dono."""
    metricas = queries.metricas_por_dono(banco_teste)
    assert len(metricas) == 5
    # Ana Sousa (id 1) possui 2 pets e 2 consultas no seed
    ana = next(m for m in metricas if m["dono"] == "Ana Sousa")
    assert ana["total_pets"] == 2
    assert ana["total_consultas"] == 3
    assert ana["total_gasto_consultas"] == 350.00  # 120 + 150 + 80


def test_estatisticas_peso_por_especie(banco_teste):
    """Testa o agrupamento estatístico de peso por espécie (AVG, MIN, MAX)."""
    stats = queries.estatisticas_peso_por_especie(banco_teste)
    assert len(stats) == 3
    especies = {s["especie"] for s in stats}
    assert especies == {"Cachorro", "Gato", "Outro"}

    stats_cao = next(s for s in stats if s["especie"] == "Cachorro")
    assert stats_cao["total_cadastrado"] == 3
    assert stats_cao["menor_peso_kg"] == 8.4
    assert stats_cao["maior_peso_kg"] == 28.0


def test_insumos_mais_utilizados(banco_teste):
    """Testa o ranking com controle de TOP N."""
    top2 = queries.insumos_mais_utilizados(banco_teste, top_n=2)
    assert len(top2) == 2
    # O item de maior saída deve estar na primeira posição
    assert top2[0]["total_aplicado"] >= top2[1]["total_aplicado"]


def test_faturamento_geral_consultas(banco_teste):
    """Testa a consulta que consome a VIEW analítica de faturamento."""
    faturamentos = queries.faturamento_geral_consultas(banco_teste)
    assert len(faturamentos) == 6
    # Cada linha deve conter as colunas esperadas da view
    primeiro = faturamentos[0]
    for col in ("consulta_id", "data", "dono", "pet", "valor_base", "total_medicamentos", "custo_total"):
        assert col in primeiro.keys()


# =====================================================================
# 3. Testes da Camada de Exportação CSV (reports.py)
# =====================================================================

def test_exportar_para_csv(tmp_path, banco_teste):
    """Testa a geração de um arquivo CSV a partir de linhas retornadas pelo banco."""
    registros = queries.buscar_catalogo_medicamentos(banco_teste)
    arquivo_saida = tmp_path / "teste_catalogo.csv"

    resultado = reports.exportar_para_csv(registros, arquivo_saida)
    assert resultado.exists()

    # Lê o CSV gerado e valida seu formato
    with arquivo_saida.open("r", encoding="utf-8-sig") as f:
        leitor = list(csv.reader(f, delimiter=";"))

    cabecalho = leitor[0]
    assert cabecalho == ["id", "nome", "tipo", "preco", "estoque"]
    assert len(leitor) == 7  # 1 cabeçalho + 6 medicamentos


def test_exportar_relatorio_faturamento(tmp_path, banco_teste):
    """Testa a exportação específica do relatório consolidado de faturamento."""
    arquivo_saida = tmp_path / "faturamento.csv"
    resultado = reports.exportar_relatorio_faturamento(banco_teste, caminho_destino=arquivo_saida)

    assert resultado.exists()
    with arquivo_saida.open("r", encoding="utf-8-sig") as f:
        leitor = list(csv.reader(f, delimiter=";"))

    assert len(leitor) == 7  # 1 cabeçalho + 6 consultas
    assert "custo_total" in leitor[0]


def test_exportar_relatorio_atendimentos(tmp_path, banco_teste):
    """Testa a exportação do prontuário completo de atendimentos."""
    arquivo_saida = tmp_path / "atendimentos.csv"
    resultado = reports.exportar_relatorio_atendimentos(banco_teste, caminho_destino=arquivo_saida)

    assert resultado.exists()
    with arquivo_saida.open("r", encoding="utf-8-sig") as f:
        leitor = list(csv.reader(f, delimiter=";"))

    assert len(leitor) == 9  # 1 cabeçalho + 8 itens de consultas
    assert "insumo_aplicado" in leitor[0]


def test_exportar_csv_sem_registros(tmp_path):
    """Testa que exportar lista vazia cria o arquivo com segurança e sem erros."""
    arquivo_saida = tmp_path / "vazio.csv"
    resultado = reports.exportar_para_csv([], arquivo_saida)
    assert resultado.exists()
    assert arquivo_saida.read_text(encoding="utf-8-sig") == ""
