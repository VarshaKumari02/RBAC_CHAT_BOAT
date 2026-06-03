import sys
import os
from sqlalchemy import text

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.database import engine

def main():
    print("WARNING: This will drop all tables and enums in the 'public' schema.")
    confirm = input("Are you sure you want to refresh the database? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    print("Dropping schema 'public'...")
    with engine.connect() as conn:
        # Drop the public schema and cascade to drop all tables, enums, and types
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        # Recreate the public schema
        conn.execute(text("CREATE SCHEMA public;"))
        # Grant standard permissions (necessary in some PostgreSQL versions)
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        conn.commit()
        
    print("Database schema dropped and recreated successfully! 🎉")
    print("Restart your FastAPI server or run your seeders, and all tables and enums will be created with the new structure.")

if __name__ == "__main__":
    main()
