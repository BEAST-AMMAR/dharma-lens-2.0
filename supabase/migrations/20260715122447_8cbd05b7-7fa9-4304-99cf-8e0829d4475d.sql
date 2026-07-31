
-- Revoke EXECUTE on SECURITY DEFINER function from anon/authenticated/public.
-- handle_new_user is only invoked by a trigger on auth.users; no one should call it directly.
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM anon;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM authenticated;

-- Remove tables from the anon-visible GraphQL schema. All policies scope to auth.uid(),
-- so anon should not be able to see these objects at all.
REVOKE SELECT ON public.profiles FROM anon;
REVOKE SELECT ON public.processing_jobs FROM anon;
REVOKE SELECT ON public.processing_results FROM anon;

-- Also revoke other default privileges granted to anon (if any) on these tables.
REVOKE INSERT, UPDATE, DELETE ON public.profiles FROM anon;
REVOKE INSERT, UPDATE, DELETE ON public.processing_jobs FROM anon;
REVOKE INSERT, UPDATE, DELETE ON public.processing_results FROM anon;
