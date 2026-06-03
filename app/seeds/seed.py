import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database.database import SessionLocal
from app.seeds.role_seeder import seed_roles
from app.seeds.permission_group_seeder import seed_permission_groups
from app.seeds.permission_seeder import seed_permissions
from app.seeds.permission_role_seeder import seed_role_permissions

def main():
    print("Initializing Database Seeding...")
    db = SessionLocal()
    try:
        print("Seeding Roles...")
        seed_roles(db)
        print("Roles seeded successfully.")

        print("Seeding Permission Groups...")
        seed_permission_groups(db)
        print("Permission Groups seeded successfully.")

        print("Seeding Permissions...")
        seed_permissions(db)
        print("Permissions seeded successfully.")

        print("Seeding Role Permissions (mapping)...")
        seed_role_permissions(db)
        print("Role Permissions seeded successfully.")

        print("\nDatabase seeding completed successfully!")
    except Exception as e:
        print(f"\nError seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()
