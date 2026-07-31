-- Create table for RLHF Feedback
CREATE TABLE IF NOT EXISTS public.rlhf_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID,
    query_text TEXT,
    retrieval_strategy TEXT, -- e.g., 'graph_heavy', 'vector_heavy', 'hybrid'
    reward_score FLOAT, -- 1.0 for thumbs up, 0.0 or -1.0 for thumbs down
    user_corrections JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.rlhf_feedback ENABLE ROW LEVEL SECURITY;

-- Allow insert access to authenticated users
CREATE POLICY "Allow insert access for authenticated users" ON public.rlhf_feedback
    FOR INSERT TO authenticated WITH CHECK (true);
