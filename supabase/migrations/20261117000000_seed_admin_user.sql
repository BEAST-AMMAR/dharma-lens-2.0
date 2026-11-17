-- ============================================================================
-- VidhiChakshu (विधि-चक्षु) - Admin User Seed & Role Configuration Migration
-- ============================================================================

-- Ensure pgcrypto extension is active for password encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
DECLARE
  admin_id UUID := 'a0000000-0000-0000-0000-000000000001';
  admin_email TEXT := 'admin@vidhichakshu.com';
  admin_password TEXT := 'Admin@VidhiChakshu2026';
BEGIN
  -- 1. Create or update user in auth.users
  IF NOT EXISTS (SELECT 1 FROM auth.users WHERE email = admin_email) THEN
    INSERT INTO auth.users (
      instance_id,
      id,
      aud,
      role,
      email,
      encrypted_password,
      email_confirmed_at,
      raw_app_meta_data,
      raw_user_meta_data,
      created_at,
      updated_at
    ) VALUES (
      '00000000-0000-0000-0000-000000000000',
      admin_id,
      'authenticated',
      'authenticated',
      admin_email,
      crypt(admin_password, gen_salt('bf')),
      NOW(),
      '{"provider":"email","providers":["email"]}'::jsonb,
      '{"full_name":"VidhiChakshu System Administrator","role":"admin"}'::jsonb,
      NOW(),
      NOW()
    );
  ELSE
    UPDATE auth.users
    SET encrypted_password = crypt(admin_password, gen_salt('bf')),
        email_confirmed_at = NOW(),
        raw_user_meta_data = '{"full_name":"VidhiChakshu System Administrator","role":"admin"}'::jsonb,
        updated_at = NOW()
    WHERE email = admin_email;
  END IF;

  -- 2. Create or update profile in public.profiles
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'profiles') THEN
    INSERT INTO public.profiles (id, full_name, role, created_at, updated_at)
    VALUES (
      admin_id,
      'VidhiChakshu System Administrator',
      'admin',
      NOW(),
      NOW()
    )
    ON CONFLICT (id) DO UPDATE
    SET full_name = EXCLUDED.full_name,
        role = 'admin',
        updated_at = NOW();
  END IF;

END $$;
