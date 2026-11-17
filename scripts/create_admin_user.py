"""
VidhiChakshu (विधि-चक्षु) - Admin User Provisioning Script
Creates or updates the default system administrator account.
"""
import os
import sys
from dotenv import load_dotenv

# Search for .env
load_dotenv()
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    load_dotenv(env_path)

ADMIN_EMAIL = "admin@vidhichakshu.com"
ADMIN_PASSWORD = "Admin@VidhiChakshu2026"
ADMIN_NAME = "VidhiChakshu System Administrator"

def provision_admin():
    print("=" * 60)
    print("  VidhiChakshu (विधि-चक्षु) - Admin Account Provisioning")
    print("=" * 60)
    
    supabase_url = os.environ.get("VITE_SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

    if not supabase_url or not service_key:
        print("[ERROR] Missing VITE_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment.")
        print(f"Default Credentials:\n  Email: {ADMIN_EMAIL}\n  Password: {ADMIN_PASSWORD}")
        return

    try:
        from supabase import create_client
        sp = create_client(supabase_url, service_key)

        print(f"Connecting to Supabase at: {supabase_url}...")
        
        # Check if user exists using admin API
        try:
            user = sp.auth.admin.create_user({
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": ADMIN_NAME,
                    "role": "admin"
                }
            })
            print(f"[SUCCESS] Admin user created successfully with ID: {user.user.id}")
        except Exception as create_err:
            if "already exists" in str(create_err).lower() or "already registered" in str(create_err).lower():
                print(f"[NOTICE] Admin user already exists. Updating password & metadata...")
                # Search for user to update
                users_list = sp.auth.admin.list_users()
                target_user = next((u for u in users_list if u.email == ADMIN_EMAIL), None)
                if target_user:
                    sp.auth.admin.update_user_by_id(target_user.id, {
                        "password": ADMIN_PASSWORD,
                        "email_confirm": True,
                        "user_metadata": {
                            "full_name": ADMIN_NAME,
                            "role": "admin"
                        }
                    })
                    print(f"[SUCCESS] Admin user {ADMIN_EMAIL} updated successfully!")
            else:
                print(f"[NOTICE] Supabase Auth API response: {create_err}")
                print("Tip: Run the SQL migration in supabase/migrations/20261117000000_seed_admin_user.sql in the Supabase SQL Editor.")

    except Exception as e:
        print(f"[NOTICE] Could not complete direct API call ({e}).")
        print("Tip: Use the SQL Editor migration in supabase/migrations/20261117000000_seed_admin_user.sql")

    print("\n" + "=" * 60)
    print("  ADMIN CREDENTIALS:")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Role:     admin")
    print("=" * 60)

if __name__ == "__main__":
    provision_admin()
