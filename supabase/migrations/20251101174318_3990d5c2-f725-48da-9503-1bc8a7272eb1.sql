-- Add missing RLS policies for better data management and user privacy

-- Allow users to insert their own profile (though handle_new_user trigger also creates it)
CREATE POLICY "Users can insert their own profile"
ON public.profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

-- Allow users to delete their own processing jobs (for privacy)
CREATE POLICY "Users can delete their own jobs"
ON public.processing_jobs
FOR DELETE
USING (auth.uid() = user_id);

-- Allow users to delete their processing results (for privacy compliance)
CREATE POLICY "Users can delete their own results"
ON public.processing_results
FOR DELETE
USING (auth.uid() = user_id);

-- Allow users to update their processing results if needed
CREATE POLICY "Users can update their own results"
ON public.processing_results
FOR UPDATE
USING (auth.uid() = user_id);