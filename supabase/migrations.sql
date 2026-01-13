-- Tabla de interacciones para memoria de sesión
CREATE TABLE IF NOT EXISTS interacciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    model_used TEXT,
    tokens_used INTEGER DEFAULT 0
);

-- Índice para búsquedas rápidas por sesión
CREATE INDEX IF NOT EXISTS idx_interacciones_session_id ON interacciones(session_id);

-- Tabla de configuración de usuario (opcional, para límites futuros)
CREATE TABLE IF NOT EXISTS config_usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    default_model TEXT DEFAULT 'google/gemini-2.0-flash-exp:free',
    token_limit_daily INTEGER DEFAULT 100000,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS (Row Level Security) - Nota: Se asume que se usa Service Role para el Cerebro
-- ALTER TABLE interacciones ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE config_usuario ENABLE ROW LEVEL SECURITY;
