-- Migration: Add metadata fields to legal_knowledge for real IPC<->BNS mapping and temporal filtering
ALTER TABLE public.legal_knowledge 
  ADD COLUMN IF NOT EXISTS superseded_by TEXT,
  ADD COLUMN IF NOT EXISTS replaces TEXT,
  ADD COLUMN IF NOT EXISTS effective_date DATE,
  ADD COLUMN IF NOT EXISTS jurisdiction TEXT DEFAULT 'India';

-- Update hybrid search function to include superseded_by and replaces metadata
DROP FUNCTION IF EXISTS hybrid_search_legal_knowledge(TEXT, vector, INT, FLOAT, FLOAT);
DROP FUNCTION IF EXISTS hybrid_search_legal_knowledge;

CREATE OR REPLACE FUNCTION hybrid_search_legal_knowledge(

  query_text TEXT,
  query_embedding vector(768),
  match_count INT DEFAULT 5,
  full_text_weight FLOAT DEFAULT 1.0,
  semantic_weight FLOAT DEFAULT 1.0
) RETURNS TABLE (
  id UUID,
  source_type TEXT,
  section_number TEXT,
  title TEXT,
  content TEXT,
  superseded_by TEXT,
  replaces TEXT,
  similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  WITH full_text AS (
    SELECT 
      lk.id,
      ts_rank(lk.fts, plainto_tsquery('english', query_text)) AS rank
    FROM public.legal_knowledge lk
    WHERE lk.fts @@ plainto_tsquery('english', query_text)
    ORDER BY rank DESC
    LIMIT match_count * 2
  ),
  semantic AS (
    SELECT 
      lk.id,
      1 - (lk.embedding <=> query_embedding) AS similarity
    FROM public.legal_knowledge lk
    ORDER BY lk.embedding <=> query_embedding
    LIMIT match_count * 2
  )
  SELECT 
    lk.id,
    lk.source_type,
    lk.section_number,
    lk.title,
    lk.content,
    lk.superseded_by,
    lk.replaces,
    (coalesce(ft.rank, 0.0) * full_text_weight) + (coalesce(s.similarity, 0.0) * semantic_weight) AS combined_similarity
  FROM public.legal_knowledge lk
  LEFT JOIN full_text ft ON ft.id = lk.id
  LEFT JOIN semantic s ON s.id = lk.id
  WHERE ft.id IS NOT NULL OR s.id IS NOT NULL
  ORDER BY combined_similarity DESC
  LIMIT match_count;
END;
$$;
