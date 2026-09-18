# 🐾 Petpylite Care — Gestão Clínica Veterinária

> *"Aqui cuidamos do seu animal com dedicação e amor, garantindo o melhor acompanhamento clínico e bem-estar para o seu pet."*

---
**Desafio JR: Python + SQLite + IA**

---

## 📌 Visão Geral do Projeto

O **Petpylite Care** é uma aplicação interativa via linha de comando (CLI/Terminal) projetada para orquestrar e analisar as operações de uma clínica veterinária. O sistema integra persistência relacional com **SQLite3**, consultas analíticas consolidadas via **Python**, exportação de relatórios tabulares em **CSV**, e suporte arquitetural orientado por inteligência artificial para otimização de consultas e modelagem de dados.

Desenvolvido como projeto prático do **Desafio Engenheiro de Dados Júnior**, a aplicação simula o fluxo completo de atendimento: desde o cadastro de tutores/donos e seus pets até o faturamento de consultas, administração de medicamentos, indicadores clínicos agregados e exportação de relatórios gerenciais.

---

## 🎯 O que o projeto faz

- **Estruturação Relacional Segura**: Implementa integridade referencial com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`), deleção em cascata (`ON DELETE CASCADE`) e restrições de validação (`CHECK`).
- **Automação de Carga (Data Seeding)**: Script de inicialização idempotente que carrega registros de donos, animais, catálogo de medicamentos e prontuários de consultas.
- **Painel Analítico no Terminal**: Interface interativa com formatação dinâmica de tabelas, máscaras financeiras, tratamento de exceções e compatibilidade de encoding (UTF-8).
- **Relatórios Gerenciais e Métricas Clínicas**:
  - Catálogo completo de insumos, vacinas e medicamentos.
  - Filtro parametrizado de pets por espécie com dados de contato do responsável.
  - Prontuário detalhado com consolidação relacional de 5 tabelas (`consultas`, `animais`, `donos`, `itens_consulta`, `medicamentos`).
  - Resumo de fidelidade e volume de atendimentos agrupados por dono.
  - Análise biométrica com agregação estatística de peso (`AVG`, `MIN`, `MAX`, `COUNT`) por espécie.
  - Ranking de insumos clínicos e vacinas mais utilizados (`LIMIT`).
  - Fechamento financeiro automatizado por meio de uma `VIEW` analítica (`vw_resumo_consultas`).
- **Exportação de Relatórios em CSV**: Módulo modularizado em funções (`src/reports.py`) que exporta os dados analíticos (faturamento consolidado e prontuários de atendimentos) para arquivos `.csv` na pasta `relatorios/`, codificados em `utf-8-sig` para abertura direta e sem falhas no Microsoft Excel.
- **Testes Automatizados com `pytest`**: Suíte de testes automatizados com banco isolado em memória (`:memory:`), testando regras de integridade referencial, restrições de validação, integridade das consultas SQL e geração de CSV.

---

## 🗂️ Estrutura de Arquivos do Projeto

```
petpylite/
├── .gitignore             # Bloqueio de binários (.db), caches, venv e CSVs gerados
├── pytest.ini             # Configuração do pytest e mapeamento do pythonpath (src)
├── README.md              # Documentação técnica e guia de execução passo a passo
├── requirements.txt       # Dependências externas do projeto (pytest)
├── data/
│   ├── schema.sql         # DDL: Criação das 5 tabelas relacionais e da VIEW analítica
│   ├── seed.sql           # DML: Registros iniciais para testes e consultas
│   └── petcare.db         # Banco SQLite gerado localmente (ignorado pelo Git)
├── relatorios/            # Diretório de destino dos relatórios CSV exportados
│   ├── .gitkeep           # Mantém o diretório no versionamento Git
│   ├── relatorio_faturamento_consultas.csv
│   └── relatorio_atendimentos_completos.csv
├── src/
│   ├── database.py        # Módulo de conexão, checagem de integridade e carga DDL/DML
│   ├── queries.py         # Camada de consultas SQL analíticas parametrizadas
│   ├── reports.py         # Módulo de exportação de dados e relatórios em formato CSV
│   └── main.py            # CLI com menu interativo, renderizador tabular e exportação
└── tests/
    └── test_pet.py        # Suíte completa de testes automatizados com pytest
```

---

## 🧩 Modelo de Dados

O modelo relacional suporta integridade em cascata e relações associativas de cardinalidade $1:N$ e $N:N$:

```
donos (1) ──< animais (1) ──< consultas (1) ──< itens_consulta >── (1) medicamentos
```

- **`donos` ($1 \to N$) `animais`**: Um cliente/dono pode possuir múltiplos pets cadastrados.
- **`animais` ($1 \to N$) `consultas`**: Cada atendimento clínico é registrado individualmente para um pet.
- **`consultas` ($N \to N$) `medicamentos`**: Mapeado via tabela associativa **`itens_consulta`**, permitindo aplicar múltiplas doses/medicamentos com registro histórico de valor unitário por consulta.
- **`VIEW: vw_resumo_consultas`**: Visão agregada que unifica dono, animal, valor-base da consulta e soma dos insumos aplicados.

---

## 🚀 Como Executar

Siga os passos abaixo para preparar o ambiente e rodar o projeto do zero:

### Pré-requisitos
- **Python 3.10 ou superior** instalado.

---

### 1. Clonar o repositório
```bash
git clone https://github.com/gabtei/petpylite.git
cd petpylite
```

---

### 2. Criar e Ativar o Ambiente Virtual (Recomendado)

- **No Windows (PowerShell / Prompt de Comando):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

- **No Linux ou macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Instalar as Dependências

O projeto utiliza a biblioteca padrão do Python para sua operação principal (`sqlite3`, `csv`, `pathlib`, `typing`), demandando apenas o `pytest` para a execução da suíte de testes:

```bash
pip install -r requirements.txt
```

---

### 4. Executar os Testes Automatizados (`pytest`)

Para verificar a integridade estrutural do banco, restrições de validação, consultas SQL e exportação CSV:

```bash
pytest
```
*Ou, explicitamente:*
```bash
python -m pytest tests/test_pet.py -v
```

> **Nota:** Todos os 16 testes utilizam um banco SQLite isolado em memória (`:memory:`), executando em milissegundos sem alterar seu banco de dados local.

---

### 5. Inicializar o Banco de Dados (Opcional)

Você pode criar o schema estrutural e popular os dados de teste executando:

```bash
python src/database.py --reset
```
*(Nota: Ao iniciar o programa principal pela primeira vez, a aplicação detecta automaticamente a ausência do banco e realiza essa montagem de forma transparente).*

---

### 6. Iniciar a Aplicação Interativa (CLI)

```bash
python src/main.py
```

Você verá o menu interativo com todas as opções:

```text
════════════════════════════════════════════════════════════
 🏥 SISTEMA CLÍNICO VETERINÁRIO - PETPYLITE CARE
════════════════════════════════════════════════════════════
 [1] 📋 Catálogo de Insumos e Medicamentos
 [2] 🔍 Filtrar Pets por Espécie (Cachorro, Gato, Outro)
 [3] 📑 Prontuário Detalhado (Junção das 5 Tabelas)
 [4] 👤 Métricas e Despesas por Dono (Tutor)
 [5] ⚖️  Estatísticas de Porte e Peso por Espécie
 [6] 🏆 Top Insumos e Vacinas mais Aplicados
 [7] 💰 Faturamento Consolidado de Consultas (VIEW)
 [8] 📊 Exportar Relatório em CSV (Faturamento / Atendimentos)
 [0] 🚪 Encerrar Sessão
────────────────────────────────────────────────────────────
```

---

### 7. Exportar Relatórios em CSV

A exportação pode ser realizada de duas formas:

1. **Pelo Menu da Aplicação**: Escolha a opção `[8]` no menu do terminal e selecione qual relatório deseja exportar (Faturamento, Prontuário Completo ou ambos).
2. **Via Código Python**:
```python
from database import obter_conexao
import reports

conexao = obter_conexao()
caminho = reports.exportar_relatorio_faturamento(conexao)
print(f"Relatório salvo em: {caminho}")
```

Os relatórios são salvos no diretório `relatorios/` com separador `;` e codificação `UTF-8 com BOM` (`utf-8-sig`), garantindo que caracteres especiais e acentuações abram perfeitamente no **Microsoft Excel**, **Google Sheets** ou **LibreOffice Calc**.

---

## 🧠 Competências e Conceitos Praticados

| Pilar | Conceitos e Ferramentas |
|---|---|
| **Engenharia de Dados & SQL** | `CREATE TABLE`, `CHECK constraints`, `FOREIGN KEY (CASCADE)`, `PRAGMA foreign_keys`, `INNER/LEFT JOIN`, `WHERE` com prepared statements, `GROUP BY`, Funções de Agregação (`SUM`, `COUNT`, `AVG`, `MIN`, `MAX`), `COALESCE`, `ORDER BY`, `LIMIT`, e criação de `VIEW`. |
| **Python Moderno & Arquitetura** | `sqlite3.Row` (mapeamento nominal), `pathlib.Path` para caminhos independentes de sistema operacional, modularização em múltiplos arquivos e funções com tipagem estática (`typing`), context managers (`with`), sanitização de streams de saída UTF-8 para Windows. |
| **Manipulação de Arquivos & Dados** | Módulo nativo `csv`, delimitação controlada, codificação `utf-8-sig` com BOM para interoperabilidade universal com planilhas eletrônicas. |
| **Qualidade de Software & Testes** | Suíte de testes com `pytest`, fixtures de banco em memória (`:memory:`), testes unitários e de integração, validação de regras de integridade e testes de regressão. |
| **Boas Práticas de Repositório** | Organização limpa, exclusão preventiva via `.gitignore`, rastreabilidade de dependências via `requirements.txt` e documentação reproduzível. |

---

## 👤 Autor

- **Desenvolvedor:** Gabriel Teixeira
- **Trilha:** Desafio Engenheiro de Dados Júnior (Python + SQLite + IA)