-- ============================================================
-- ATUALIZAÇÃO DO BANCO DE DADOS — Sistema Patrimonial v3
-- Execute esse script no seu banco existente.
-- Ele NÃO apaga dados existentes.
-- ============================================================

-- ── Tabela de usuários ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100)  NOT NULL,
    login        VARCHAR(50)   NOT NULL UNIQUE,
    senha_hash   VARCHAR(255)  NOT NULL,
    nivel        ENUM('admin', 'editor', 'visualizador') NOT NULL DEFAULT 'visualizador',
    ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Usuário admin padrão (senha: admin123 — troque no primeiro acesso)
INSERT IGNORE INTO usuarios (nome, login, senha_hash, nivel)
VALUES ('Administrador', 'admin',
        SHA2('admin123', 256), 'admin');

-- ── Log de auditoria ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auditoria (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id      INT,
    usuario_login   VARCHAR(50),
    acao            VARCHAR(50)  NOT NULL,   -- ex: CADASTRAR, EDITAR, MOVER, LOGIN
    tabela          VARCHAR(50),             -- ex: patrimonio, movimentacoes
    registro_id     INT,                     -- id do registro afetado
    descricao       TEXT,                    -- detalhe da ação
    ip              VARCHAR(45),
    criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- ── Fotos de patrimônio ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS patrimonio_fotos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patrimonio_id   INT NOT NULL,
    caminho         VARCHAR(500) NOT NULL,   -- path relativo ao projeto
    principal       BOOLEAN DEFAULT FALSE,
    criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patrimonio_id) REFERENCES patrimonio(id) ON DELETE CASCADE
);

-- ── Responsáveis por patrimônio ─────────────────────────────
ALTER TABLE patrimonio
    ADD COLUMN IF NOT EXISTS responsavel     VARCHAR(100)  DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS data_aquisicao  DATE          DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS valor           DECIMAL(12,2) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS numero_serie    VARCHAR(100)  DEFAULT NULL;

-- ── Manutenções programadas ─────────────────────────────────
CREATE TABLE IF NOT EXISTS manutencoes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patrimonio_id   INT NOT NULL,
    tipo            ENUM('preventiva', 'corretiva', 'calibracao') NOT NULL DEFAULT 'preventiva',
    descricao       TEXT,
    data_prevista   DATE NOT NULL,
    data_realizada  DATE DEFAULT NULL,
    custo           DECIMAL(10,2) DEFAULT NULL,
    responsavel     VARCHAR(100),
    status          ENUM('pendente', 'realizada', 'cancelada') DEFAULT 'pendente',
    criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patrimonio_id) REFERENCES patrimonio(id) ON DELETE CASCADE
);

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
