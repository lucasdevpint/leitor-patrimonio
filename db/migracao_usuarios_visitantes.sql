-- ============================================================
-- MIGRAÇÃO — Gerenciamento de Visitantes
-- Sistema Patrimonial v3.1
-- ============================================================

USE patrimonio;

CREATE TABLE IF NOT EXISTS visitantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    documento VARCHAR(30),
    empresa VARCHAR(150),
    telefone VARCHAR(30),
    email VARCHAR(150),
    observacoes TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_visitantes_nome ON visitantes(nome);
CREATE INDEX idx_visitantes_documento ON visitantes(documento);
CREATE INDEX idx_visitantes_empresa ON visitantes(empresa);

-- ============================================================
-- FIM DA MIGRAÇÃO
-- ============================================================
