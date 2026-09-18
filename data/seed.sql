-- =====================================================================
-- seed.sql — Dados iniciais para testes da Clínica Veterinária (Pet Care)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Donos (Clientes)
-- ---------------------------------------------------------------------
INSERT INTO donos (nome, telefone, email) VALUES
    ('Ana Sousa',       '91234-5678', 'ana.sousa@email.com'),
    ('Bruno Lima',      '92345-6789', 'bruno.lima@email.com'),
    ('Carla Mendes',    '93456-7890', 'carla.mendes@email.com'),
    ('Diogo Fernandes', '96543-2109', 'diogo.fernandes@email.com'),
    ('Elisa Rocha',     '91876-5432', 'elisa.rocha@email.com');

-- ---------------------------------------------------------------------
-- 2. Animais (Pets vinculados aos seus donos)
-- ---------------------------------------------------------------------
INSERT INTO animais (dono_id, nome, especie, peso) VALUES
    (1, 'Max',    'Cachorro', 12.5), -- Pertence à Ana Sousa
    (1, 'Mimi',   'Gato',      4.2), -- Pertence à Ana Sousa
    (2, 'Thor',   'Cachorro', 28.0), -- Pertence ao Bruno Lima
    (3, 'Luna',   'Gato',      3.8), -- Pertence à Carla Mendes
    (4, 'Bob',    'Cachorro',  8.4), -- Pertence ao Diogo Fernandes
    (5, 'Pipoca', 'Outro',     1.1); -- Pertence à Elisa Rocha

-- ---------------------------------------------------------------------
-- 3. Medicamentos e Insumos (Catálogo de produtos clínicos)
-- ---------------------------------------------------------------------
INSERT INTO medicamentos (nome, tipo, preco, estoque) VALUES
    ('Vacina Antirrábica',  'Vacina',      85.00, 30),
    ('Vacina V10',          'Vacina',     110.00, 25),
    ('Antibiótico Amox',    'Remédio',     65.00, 40),
    ('Anti-inflamatório X', 'Remédio',     45.50, 50),
    ('Complexo Vitamínico', 'Suplemento',  55.00, 20),
    ('Vermífugo Plus',      'Remédio',     35.00, 60);

-- ---------------------------------------------------------------------
-- 4. Consultas (Atendimentos clínicos aos animais)
-- ---------------------------------------------------------------------
INSERT INTO consultas (animal_id, data_consulta, motivo, valor_consulta) VALUES
    (1, '2026-06-01', 'Vacinação anual',            120.00), -- Max
    (2, '2026-06-03', 'Apatia e vómito',            150.00), -- Mimi
    (3, '2026-06-10', 'Check-up de rotina',         120.00), -- Thor
    (4, '2026-06-12', 'Alergia de pele',            140.00), -- Luna
    (5, '2026-06-15', 'Vacinação e desparasitação', 120.00), -- Bob
    (1, '2026-06-20', 'Retorno pós-vacina',          80.00); -- Max (segunda consulta)

-- ---------------------------------------------------------------------
-- 5. Itens da Consulta (Medicamentos e vacinas aplicados por atendimento)
-- ---------------------------------------------------------------------
INSERT INTO itens_consulta (consulta_id, medicamento_id, quantidade, valor_unitario) VALUES
    (1, 1, 1,  85.00),  -- Consulta 1: 1x Vacina Antirrábica
    (1, 2, 1, 110.00),  -- Consulta 1: 1x Vacina V10
    (2, 3, 1,  65.00),  -- Consulta 2: 1x Antibiótico Amox
    (2, 4, 1,  45.50),  -- Consulta 2: 1x Anti-inflamatório X
    (3, 5, 2,  55.00),  -- Consulta 3: 2x Complexo Vitamínico
    (4, 4, 1,  45.50),  -- Consulta 4: 1x Anti-inflamatório X
    (5, 1, 1,  85.00),  -- Consulta 5: 1x Vacina Antirrábica
    (5, 6, 1,  35.00);  -- Consulta 5: 1x Vermífugo Plus