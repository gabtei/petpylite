-- =====================================================================
-- schema.sql — Estrutura do banco de dados da Clínica Veterinária (Pet Care)
-- Banco: SQLite
-- 5 tabelas relacionais + 1 VIEW analítica
-- =====================================================================

-- Força a verificação de integridade referencial das chaves estrangeiras
PRAGMA foreign_keys = ON;

-- Limpeza preventiva das tabelas na ordem correta de dependência
DROP VIEW IF EXISTS vw_resumo_consultas;
DROP TABLE IF EXISTS itens_consulta;
DROP TABLE IF EXISTS consultas;
DROP TABLE IF EXISTS medicamentos;
DROP TABLE IF EXISTS animais;
DROP TABLE IF EXISTS donos;

-- ---------------------------------------------------------------------
-- Tabela: donos
-- Armazena os clientes/responsáveis pelos animais.
-- ---------------------------------------------------------------------
CREATE TABLE donos (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT    NOT NULL,
    telefone TEXT    NOT NULL,
    email    TEXT    NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- Tabela: animais
-- Armazena os pets vinculados a um dono responsável.
-- ---------------------------------------------------------------------
CREATE TABLE animais (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    dono_id   INTEGER NOT NULL,
    nome      TEXT    NOT NULL,
    especie   TEXT    NOT NULL CHECK (especie IN ('Cachorro', 'Gato', 'Outro')),
    peso      REAL    NOT NULL CHECK (peso > 0),
    FOREIGN KEY (dono_id) REFERENCES donos(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: medicamentos
-- Catálogo de insumos clínicos (remédios, vacinas, suplementos).
-- ---------------------------------------------------------------------
CREATE TABLE medicamentos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT    NOT NULL,
    tipo      TEXT    NOT NULL CHECK (tipo IN ('Vacina', 'Remédio', 'Suplemento')),
    preco     REAL    NOT NULL CHECK (preco >= 0),
    estoque   INTEGER NOT NULL CHECK (estoque >= 0)
);

-- ---------------------------------------------------------------------
-- Tabela: consultas
-- Registra os atendimentos clínicos realizados para cada animal.
-- ---------------------------------------------------------------------
CREATE TABLE consultas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id      INTEGER NOT NULL,
    data_consulta  TEXT    NOT NULL,   -- Formato: 'AAAA-MM-DD'
    motivo         TEXT    NOT NULL,
    valor_consulta REAL    NOT NULL CHECK (valor_consulta >= 0),
    FOREIGN KEY (animal_id) REFERENCES animais(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: itens_consulta
-- Tabela associativa (N:N) que registra vacinas ou remédios administrados
-- durante uma consulta específica.
-- ---------------------------------------------------------------------
CREATE TABLE itens_consulta (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    consulta_id    INTEGER NOT NULL,
    medicamento_id INTEGER NOT NULL,
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    valor_unitario REAL    NOT NULL CHECK (valor_unitario >= 0), -- Histórico do preço na data
    FOREIGN KEY (consulta_id)    REFERENCES consultas(id) ON DELETE CASCADE,
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);

-- ---------------------------------------------------------------------
-- VIEW: faturamento total e resumo por atendimento
-- Consolida dono, pet, data, custo da consulta e total gasto em medicamentos.
-- Permite uso direto de JOIN, SUM e GROUP BY.
-- ---------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS vw_resumo_consultas AS
SELECT 
    c.id                                                        AS consulta_id,
    c.data_consulta                                             AS data,
    d.nome                                                      AS dono,
    a.nome                                                      AS pet,
    a.especie                                                   AS especie,
    c.valor_consulta                                            AS valor_base,
    COALESCE(SUM(ic.quantidade * ic.valor_unitario), 0)         AS total_medicamentos,
    (c.valor_consulta + COALESCE(SUM(ic.quantidade * ic.valor_unitario), 0)) AS custo_total
FROM consultas c
JOIN animais a              ON a.id = c.animal_id
JOIN donos d                ON d.id = a.dono_id
LEFT JOIN itens_consulta ic ON ic.consulta_id = c.id
GROUP BY 
    c.id, c.data_consulta, d.nome, a.nome, a.especie, c.valor_consulta;