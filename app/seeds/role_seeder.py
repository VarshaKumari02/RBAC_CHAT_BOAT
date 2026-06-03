from app.models.roles import Role

def seed_roles(db):
    roles = [
        {
            "name": "Super Admin",
            "description": "Has full access to all modules and system settings"
        },
        {
            "name": "Admin",
            "description": "Can manage users, roles, and business operations"
        },
        {
            "name": "Manager",
            "description": "Can manage team activities and view reports"
        },
        {
            "name": "User",
            "description": "Regular user with limited access permissions"
        }
    ]

    for role_data in roles:
        role = db.query(Role).filter(
            Role.name == role_data["name"]
        ).first()

        if not role:
            db.add(
                Role(
                    name=role_data["name"],
                    description=role_data["description"]
                )
            )

    db.commit()