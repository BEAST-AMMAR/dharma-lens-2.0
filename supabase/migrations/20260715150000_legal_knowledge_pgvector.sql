-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for Legal Knowledge Base
CREATE TABLE IF NOT EXISTS public.legal_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL, -- e.g., 'IPC', 'BNS', 'Constitution'
    section_number TEXT,
    title TEXT,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(768), -- For sentence-transformers embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.legal_knowledge ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users
CREATE POLICY "Allow read access for authenticated users" ON public.legal_knowledge
    FOR SELECT TO authenticated USING (true);

-- Create a generic HNSW index for vector similarity search
CREATE INDEX ON public.legal_knowledge USING hnsw (embedding vector_cosine_ops);
