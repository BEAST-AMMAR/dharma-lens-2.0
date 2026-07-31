
-- Hide these tables from the pg_graphql schema for both anon and authenticated,
-- without revoking SELECT (which would break RLS-based Data API access).
COMMENT ON TABLE public.profiles IS E'@graphql({"visible": false})';
COMMENT ON TABLE public.processing_jobs IS E'@graphql({"visible": false})';
COMMENT ON TABLE public.processing_results IS E'@graphql({"visible": false})';
