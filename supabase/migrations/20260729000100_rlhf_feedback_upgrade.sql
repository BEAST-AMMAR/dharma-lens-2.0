-- Migration: Upgrade RLHF Feedback schema to store chunk citations and model response text
ALTER TABLE public.rlhf_feedback 
  ADD COLUMN IF NOT EXISTS document_id UUID,
  ADD COLUMN IF NOT EXISTS retrieved_chunk_ids TEXT[],
  ADD COLUMN IF NOT EXISTS response_text TEXT,
  ADD COLUMN IF NOT EXISTS user_comment TEXT;

-- Update RLS policy to allow insert for public/anon/authenticated
DROP POLICY IF EXISTS "Allow insert access for authenticated users" ON public.rlhf_feedback;

CREATE POLICY "Allow insert access for all users" ON public.rlhf_feedback
    FOR INSERT WITH CHECK (true);
