"""
database.py
-----------
Módulo de infraestrutura e persistência de dados da clínica veterinária Pet Care.
Gerencia a conexão SQLite, inicialização de schemas estruturais e injeção de sementes (seed).
"""

from pathlib import Path
import sqlite3
import sys

# Garante compatibilidade de saída UTF-8 no Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Mapeamento de diretórios usando pathlib (estrutura moderna e independente de SO)
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_DADOS = DIRETORIO_RAIZ / "data"

ARQUIVO_BANCO = DIRETORIO_DADOS / "petcare.db"
ARQUIVO_SCHEMA = DIRETORIO_DADOS / "schema.sql"
ARQUIVO_SEED = DIRETORIO_DADOS / "seed.sql"


def obter_conexao() -> sqlite3.Connection:
    """
    Estabelece e devolve uma conexão ativa com o banco SQLite do Pet Care.
    Configura o acesso nominal às colunas (Row) e garante a imposição de integridade referencial.
    """
    conn = sqlite3.connect(ARQUIVO_BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _carregar_script_sql(caminho_sql: Path, conexao: sqlite3.Connection) -> None:
    """Lê as instruções de um arquivo SQL e aplica na sessão aberta do banco."""
    if not caminho_sql.is_file():
        raise FileNotFoundError(f"Arquivo SQL obrigatório não encontrado: {caminho_sql}")
    
    conteudo = caminho_sql.read_text(encoding="utf-8")
    conexao.executescript(conteudo)


def inicializar_banco(forcar_recriacao: bool = False) -> None:
    """
    Constrói a base de dados da clínica veterinária.
    
    :param forcar_recriacao: Se Verdadeiro, apaga o banco atual e refaz schema + carga de dados.
    """
    # Garante que o diretório data/ exista
    DIRETORIO_DADOS.mkdir(parents=True, exist_ok=True)

    if forcar_recriacao and ARQUIVO_BANCO.exists():
        ARQUIVO_BANCO.unlink()
        print("[Pet Care] Base de dados pré-existente removida.")

    if ARQUIVO_BANCO.exists() and not forcar_recriacao:
        print("[Pet Care] Base de dados já configurada. Para reiniciar do zero, utilize o argumento --reset.")
        return

    print("[Pet Care] Inicializando estruturas do banco de dados...")
    
    with obter_conexao() as conexao:
        try:
            # 1. Criação das tabelas e views (schema)
            _carregar_script_sql(ARQUIVO_SCHEMA, conexao)
            print(" -> Tabelas e Views criadas com sucesso.")

            # 2. Carga inicial de testes (seed)
            _carregar_script_sql(ARQUIVO_SEED, conexao)
            print(" -> Registros iniciais (donos, pets, catálogo e consultas) inseridos com sucesso.")

            conexao.commit()
            print(f"[Pet Care] Banco gerado com sucesso em: {ARQUIVO_BANCO.resolve()}")

        except sqlite3.Error as falha:
            conexao.rollback()
            print(f"[ERRO] Falha crítica durante a montagem do banco: {falha}")


# Execução direta via terminal para setup: "python src/database.py" ou "python src/database.py --reset"
if __name__ == "__main__":
    solicitou_reset = "--reset" in sys.argv
    inicializar_banco(forcar_recriacao=solicitou_reset)