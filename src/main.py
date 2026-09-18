"""
main.py
-------
Ponto de entrada do sistema Petpylite Care.
Apresenta uma interface interativa em linha de comando (CLI)
para visualização de prontuários, inventário clínico, relatórios analíticos
e exportação de dados em CSV.

Uso:
    python src/database.py --reset   # Gera e popula o banco inicialmente
    python src/main.py               # Inicia a aplicação no terminal
"""

import sys
from typing import List
import sqlite3

# Garante compatibilidade de saída UTF-8 no Windows (evita erros com emojis e caracteres especiais)
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from database import obter_conexao, inicializar_banco, ARQUIVO_BANCO
    import queries
    import reports
except ImportError:
    from src.database import obter_conexao, inicializar_banco, ARQUIVO_BANCO
    from src import queries
    from src import reports


def renderizar_grade(cabecalho_secao: str, registros: List[sqlite3.Row]) -> None:
    """
    Formata e exibe os registros em formato tabular com larguras de coluna
    calculadas dinamicamente para garantir legibilidade no terminal.
    """
    print("\n" + "━" * 80)
    print(f" 🐾 PETPYLITE CARE :: {cabecalho_secao.upper()}")
    print("━" * 80)

    if not registros:
        print(" [!] Nenhum registro encontrado para os critérios selecionados.\n")
        return

    nomes_colunas = list(registros[0].keys())

    # Prepara os valores em formato de texto e aplica máscara monetária/decimal
    matriz_linhas = []
    for item in registros:
        linha_texto = []
        for coluna in nomes_colunas:
            dado = item[coluna]
            if isinstance(dado, float):
                # Se for valor monetário ou peso
                if any(chave in coluna.lower() for chave in ("valor", "custo", "preco", "total", "subtotal")):
                    linha_texto.append(f"R$ {dado:.2f}")
                else:
                    linha_texto.append(f"{dado:.2f}")
            elif dado is None:
                linha_texto.append("-")
            else:
                linha_texto.append(str(dado))
        matriz_linhas.append(linha_texto)

    # Mede a largura máxima de cada coluna para ajustar os espaçamentos
    larguras = [len(col) for col in nomes_colunas]
    for linha in matriz_linhas:
        for idx, valor in enumerate(linha):
            larguras[idx] = max(larguras[idx], len(valor))

    # Constrói o cabeçalho e divisor
    formato_colunas = " │ ".join(f"{{:<{w}}}" for w in larguras)
    linha_divisoria = "─┼─".join("─" * w for w in larguras)

    print(formato_colunas.format(*[col.upper() for col in nomes_colunas]))
    print(linha_divisoria)

    # Exibe as linhas de conteúdo
    for linha in matriz_linhas:
        print(formato_colunas.format(*linha))
    
    print(f"\nTotal de registros exibidos: {len(matriz_linhas)}")


def exibir_painel_opcoes() -> str:
    """Imprime o painel de navegação e aguarda o comando do operador."""
    print("\n" + "═" * 60)
    print(" 🏥 SISTEMA CLÍNICO VETERINÁRIO - PETPYLITE CARE")
    print("═" * 60)
    print(" [1] 📋 Catálogo de Insumos e Medicamentos")
    print(" [2] 🔍 Filtrar Pets por Espécie (Cachorro, Gato, Outro)")
    print(" [3] 📑 Prontuário Detalhado (Junção das 5 Tabelas)")
    print(" [4] 👤 Métricas e Despesas por Dono (Tutor)")
    print(" [5] ⚖️  Estatísticas de Porte e Peso por Espécie")
    print(" [6] 🏆 Top Insumos e Vacinas mais Aplicados")
    print(" [7] 💰 Faturamento Consolidado de Consultas (VIEW)")
    print(" [8] 📊 Exportar Relatório em CSV (Faturamento / Atendimentos)")
    print(" [0] 🚪 Encerrar Sessão")
    print("─" * 60)
    return input("Selecione uma opção [0-8]: ").strip()


def rotina_filtrar_por_especie(conexao: sqlite3.Connection) -> None:
    """Solicita a espécie e executa a busca parametrizada."""
    print("\nEspécies disponíveis: Cachorro | Gato | Outro")
    especie_escolhida = input("Digite o nome da espécie: ").strip().capitalize()
    if not especie_escolhida:
        print("[!] Nenhuma espécie informada.")
        return
    dados = queries.filtrar_animais_por_especie(conexao, especie_escolhida)
    renderizar_grade(f"Pets Cadastrados da Espécie: {especie_escolhida}", dados)


def rotina_ranking_insumos(conexao: sqlite3.Connection) -> None:
    """Permite definir a quantidade do ranking ou usar padrão top 3."""
    entrada = input("Deseja ver quantos itens no ranking? [Padrão: 3]: ").strip()
    limite = int(entrada) if entrada.isdigit() and int(entrada) > 0 else 3
    dados = queries.insumos_mais_utilizados(conexao, top_n=limite)
    renderizar_grade(f"Top {limite} Insumos com Maior Saída Clínica", dados)


def rotina_exportar_csv(conexao: sqlite3.Connection) -> None:
    """Submenu para escolha e exportação de relatórios em formato CSV."""
    print("\n" + "─" * 55)
    print(" 📥 EXPORTAR RELATÓRIOS EM CSV")
    print("─" * 55)
    print(" [1] Relatório de Faturamento Consolidado (VIEW)")
    print(" [2] Prontuário Completo de Atendimentos")
    print(" [3] Exportar Ambos os Relatórios")
    print(" [0] Cancelar e Voltar ao Menu")
    print("─" * 55)
    opcao = input("Selecione qual relatório exportar [0-3]: ").strip()

    if opcao == "1":
        caminho = reports.exportar_relatorio_faturamento(conexao)
        print(f"\n[✓] Relatório de Faturamento exportado com sucesso!")
        print(f"    Arquivo gerado em: {caminho.resolve()}")
    elif opcao == "2":
        caminho = reports.exportar_relatorio_atendimentos(conexao)
        print(f"\n[✓] Prontuário de Atendimentos exportado com sucesso!")
        print(f"    Arquivo gerado em: {caminho.resolve()}")
    elif opcao == "3":
        c1 = reports.exportar_relatorio_faturamento(conexao)
        c2 = reports.exportar_relatorio_atendimentos(conexao)
        print(f"\n[✓] Relatórios exportados com sucesso!")
        print(f"    1. {c1.resolve()}")
        print(f"    2. {c2.resolve()}")
    elif opcao == "0":
        print("\nOperação cancelada.")
    else:
        print("\n[!] Opção inválida.")


def main() -> None:
    """Fluxo principal do terminal."""
    # Garante a existência do banco de dados na primeira execução
    if not ARQUIVO_BANCO.exists():
        print("[Pet Care] Base de dados inicial não encontrada. Construindo...")
        inicializar_banco(forcar_recriacao=True)

    conexao = obter_conexao()
    
    try:
        while True:
            escolha = exibir_painel_opcoes()

            if escolha == "0":
                print("\n🐾 Cuidando com dedicação e amor. Sessão encerrada!")
                break
            elif escolha == "1":
                renderizar_grade("Estoque de Insumos e Medicamentos", queries.buscar_catalogo_medicamentos(conexao))
            elif escolha == "2":
                rotina_filtrar_por_especie(conexao)
            elif escolha == "3":
                renderizar_grade("Prontuários e Histórico de Atendimentos", queries.relatorio_atendimentos_completos(conexao))
            elif escolha == "4":
                renderizar_grade("Resumo Operacional e Financeiro por Dono", queries.metricas_por_dono(conexao))
            elif escolha == "5":
                renderizar_grade("Métricas de Peso Médio por Espécie", queries.estatisticas_peso_por_especie(conexao))
            elif escolha == "6":
                rotina_ranking_insumos(conexao)
            elif escolha == "7":
                renderizar_grade("Fechamento Financeiro de Atendimentos (VIEW)", queries.faturamento_geral_consultas(conexao))
            elif escolha == "8":
                rotina_exportar_csv(conexao)
            else:
                print("\n[!] Comando não reconhecido. Por favor, digite um número de 0 a 8.")
            
            input("\nPressione [Enter] para retornar ao menu...")
            
    except KeyboardInterrupt:
        print("\n\n[!] Execução interrompida pelo teclado. Até logo!")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()