-- Script para criação da tabela de processamentos no Supabase
-- Por favor, execute este script no painel SQL Editor do seu projeto Supabase.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS processamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_arquivo_original TEXT NOT NULL,
    data_processamento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    caminho_r2_original TEXT,
    caminho_r2_limpo TEXT,
    diagnostico_json JSONB,
    status TEXT
);

-- Desativa RLS para permitir inserções com a chave anon (publishable) 
-- a partir do backend local
ALTER TABLE processamentos DISABLE ROW LEVEL SECURITY;
