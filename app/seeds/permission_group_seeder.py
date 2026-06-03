from app.models.permission_groups import PermissionGroup


def seed_permission_groups(db):

    permission_groups = [
        {
            "id": 1,
            "name": "Booking Monitor",
            "description": "Permissions related to monitoring and managing bookings.",
            "status": "active"
        },
        {
            "id": 2,
            "name": "Booking Report Access",
            "description": "Permissions to view and manage booking reports.",
            "status": "active"
        },
        {
            "id": 3,
            "name": "Credit Summary",
            "description": "Permissions to access and manage credit summary reports.",
            "status": "active"
        },
        {
            "id": 4,
            "name": "Cancellation Report",
            "description": "Permissions to view and manage flight cancellation reports.",
            "status": "active"
        },
        {
            "id": 5,
            "name": "Rescheduled Booking Report",
            "description": "Permissions to access reports for rescheduled bookings.",
            "status": "active"
        },
        {
            "id": 6,
            "name": "Distress Report",
            "description": "Permissions to access and manage distress flight reports.",
            "status": "active"
        },
        {
            "id": 7,
            "name": "Ageing Report",
            "description": "Permissions to access and manage ageing reports.",
            "status": "active"
        },
        {
            "id": 8,
            "name": "Hold Booking Report",
            "description": "Permissions to access and manage hold booking PNR reports.",
            "status": "active"
        },
        {
            "id": 9,
            "name": "Activity Logs",
            "description": "Permissions to view and manage system activity logs.",
            "status": "active"
        },
        {
            "id": 10,
            "name": "Cancellation Request",
            "description": "Permissions to manage offline flight cancellation requests.",
            "status": "active"
        },
        {
            "id": 11,
            "name": "Manage Application Users",
            "description": "Permissions to create, update, and delete application users.",
            "status": "active"
        },
        {
            "id": 12,
            "name": "Manage Admin Users",
            "description": "Permissions to manage admin-level users and access controls.",
            "status": "active"
        },
        {
            "id": 13,
            "name": "Manage User Request",
            "description": "Permissions to handle and resolve user-generated requests.",
            "status": "active"
        },
        {
            "id": 14,
            "name": "Manage Organization",
            "description": "Permissions to configure and manage organization details.",
            "status": "active"
        },
        {
            "id": 15,
            "name": "Manage Agent",
            "description": "Permissions to configure and manage agent details.",
            "status": "active"
        },
        {
            "id": 16,
            "name": "Manage Credit",
            "description": "Permissions to manage user credit limits and transactions.",
            "status": "active"
        },
        {
            "id": 17,
            "name": "Manage Domain",
            "description": "Permissions to configure and maintain domain-level settings.",
            "status": "active"
        },
        {
            "id": 18,
            "name": "Manage Processing Fee",
            "description": "Permissions to set and manage processing fees.",
            "status": "active"
        },
        {
            "id": 19,
            "name": "View Invoice Details",
            "description": "Permissions to view and manage invoice details.",
            "status": "active"
        },
        {
            "id": 20,
            "name": "Manage Roles",
            "description": "Permissions to create and manage user roles.",
            "status": "active"
        },
        {
            "id": 21,
            "name": "Client Wise Report",
            "description": "Permissions to view and manage client-wise reports.",
            "status": "active"
        },
        {
            "id": 22,
            "name": "PNR Mismatch",
            "description": "Permissions to manage PNR mismatch issues.",
            "status": "active"
        },
        {
            "id": 23,
            "name": "LCC Reconciliation",
            "description": "Permissions to access and manage LCC reconciliation reports.",
            "status": "active"
        },
        {
            "id": 24,
            "name": "Manage PNR",
            "description": "Permissions to manage PNR.",
            "status": "active"
        }
    ]

    for group_data in permission_groups:

        existing_group = (
            db.query(PermissionGroup)
            .filter(PermissionGroup.id == group_data["id"])
            .first()
        )

        if not existing_group:
            db.add(PermissionGroup(**group_data))

    db.commit()