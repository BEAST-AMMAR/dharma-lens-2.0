-- Remove the insecure role column from profiles table
-- This prevents privilege escalation where users could modify their own roles
ALTER TABLE public.profiles DROP COLUMN role;