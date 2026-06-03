from app.models.permission import Permission


def seed_permissions(db):

    permissions = [
        {
            "id": 1,
            "permission_group_id": 1,
            "name": "View Booking Monitor",
            "description": "Allows access to the booking monitor.",
            "status": "active"
        },
        {
            "id": 2,
            "permission_group_id": 2,
            "name": "View Booking Report",
            "description": "Allows access to booking report access.",
            "status": "active"
        },
        {
            "id": 3,
            "permission_group_id": 3,
            "name": "View Credit Summary Report",
            "description": "Allows access to credit summary.",
            "status": "active"
        },
        {
            "id": 4,
            "permission_group_id": 4,
            "name": "View Cancellation Report",
            "description": "Allows viewing of all cancellation reports.",
            "status": "active"
        },
        {
            "id": 5,
            "permission_group_id": 4,
            "name": "Preview Refund",
            "description": "Allows previewing refund details before processing.",
            "status": "active"
        },
        {
            "id": 6,
            "permission_group_id": 4,
            "name": "Initiate Refund for Credit",
            "description": "Allows initiating refunds for wallet transactions.",
            "status": "active"
        },
        {
            "id": 7,
            "permission_group_id": 4,
            "name": "Initiate Refund for Direct Payment",
            "description": "Allows initiating refunds for direct payments.",
            "status": "active"
        },
        {
            "id": 8,
            "permission_group_id": 5,
            "name": "View Rescheduled Booking Report",
            "description": "Allows access to rescheduled booking report.",
            "status": "active"
        },
        {
            "id": 9,
            "permission_group_id": 6,
            "name": "View Distress Report",
            "description": "Allows access to distress report.",
            "status": "active"
        },
        {
            "id": 10,
            "permission_group_id": 7,
            "name": "View Ageing Report",
            "description": "Allows access to ageing report.",
            "status": "active"
        },
        {
            "id": 11,
            "permission_group_id": 8,
            "name": "Hold Booking Report",
            "description": "Allows access to Hold Booking Report.",
            "status": "active"
        },
        {
            "id": 12,
            "permission_group_id": 9,
            "name": "View Activity Logs",
            "description": "Allows access to activity logs.",
            "status": "active"
        },
        {
            "id": 13,
            "permission_group_id": 10,
            "name": "Cancellation Request",
            "description": "Allows access to Cancellation Request.",
            "status": "active"
        },
        {
            "id": 14,
            "permission_group_id": 10,
            "name": "View Cancellation Details",
            "description": "Allows viewing cancellation request details.",
            "status": "active"
        },
        {
            "id": 15,
            "permission_group_id": 10,
            "name": "Initiate Cancellation Request",
            "description": "Allows initiating cancellation requests.",
            "status": "active"
        },
        {
            "id": 16,
            "permission_group_id": 11,
            "name": "View LTC Users",
            "description": "View LTC application users.",
            "status": "active"
        },
        {
            "id": 17,
            "permission_group_id": 11,
            "name": "View B2C Users",
            "description": "View B2C application users.",
            "status": "active"
        },
        {
            "id": 18,
            "permission_group_id": 11,
            "name": "View B2G Users",
            "description": "View B2G application users.",
            "status": "active"
        },
        {
            "id": 19,
            "permission_group_id": 11,
            "name": "Create B2G Users",
            "description": "Create B2G application users.",
            "status": "active"
        },
        {
            "id": 20,
            "permission_group_id": 11,
            "name": "Update B2G Users",
            "description": "Update B2G application users.",
            "status": "active"
        },
        {
            "id": 21,
            "permission_group_id": 11,
            "name": "Delete B2G Users",
            "description": "Delete B2G application users.",
            "status": "active"
        },

        {
            "id": 22,
            "permission_group_id": 11,
            "name": "View ATT Users",
            "description": "View ATT (Travel Agent) users",
            "status": "active"
        },
        {
            "id": 23,
            "permission_group_id": 11,
            "name": "Create ATT Users",
            "description": "Create ATT (Travel Agent) users",
            "status": "active"
        },
        {
            "id": 24,
            "permission_group_id": 11,
            "name": "Update ATT Users",
            "description": "Update ATT (Travel Agent) users",
            "status": "active"
        },
        {
            "id": 25,
            "permission_group_id": 11,
            "name": "Delete ATT Users",
            "description": "Delete ATT (Travel Agent) users",
            "status": "active"
        },
        {
            "id":26,
            "permission_group_id":11,
            "name":"View CAPF Users",
            "description":"View CAPF users",
            "status":"active"
        },
        {
            "id":27,
            "permission_group_id":11,
            "name":"Create CAPF Users",
            "description":"Create CAPF users",
            "status":"active"
        },
        {
            "id":28,
            "permission_group_id":11,
            "name":"Update CAPF Users",
            "description":"Update CAPF users",
            "status":"active"
        },
        {
            "id":29,
            "permission_group_id":11,
            "name":"Delete CAPF Users",
            "description":"Delete CAPF users",
            "status":"active"
        },
        {
            "id":30,
            "permission_group_id":12,
            "name":"View Admin Users",
            "description":"Allows modification of View admin users.",
            "status":"active"
        },
        {
            "id":31,
            "permission_group_id":12,
            "name":"Create Admin Users",
            "description":"Allows modification of Create admin users.",
            "status":"active"
        },
        {
            "id":32,
            "permission_group_id":12,
            "name":"Update Admin Users",
            "description":"Allows modification of Update admin users.",
            "status":"active"
        },
        {
            "id":33,
            "permission_group_id":12,
            "name":"Delete Admin Users",
            "description":"Allows modification of Delete admin users.",
            "status":"active"
        },
        {
            "id":34,
            "permission_group_id":13,
            "name":"Change Status",
            "description":"Allows access to manage user request.",
            "status":"active"
        },
        {
            "id":35,
            "permission_group_id":14,
            "name":"View Organizations",
            "description":"Allows access to view organizations.",
            "status":"active"
        },
        {
            "id":36,
            "permission_group_id":14,
            "name":"Create Organizations",
            "description":"Allows access to create organization.",
            "status":"active"
        },
        {
            "id":37,
            "permission_group_id":14,
            "name":"Update Organizations",
            "description":"Allows access to update organization.",
            "status":"active"
        },
        {
            "id":38,
            "permission_group_id":14,
            "name":"Delete Organizations",
            "description":"Allows access to delete organization.",
            "status":"active"
        },
        {
            "id":39,
            "permission_group_id":15,
            "name":"View Agents",
            "description":"Allows access to view agents list.",
            "status":"active"
        },
        {
            "id":40,
            "permission_group_id":15,
            "name":"Create Agent",
            "description":"Allows access to create agent.",
            "status":"active"
        },
        {
            "id":41,
            "permission_group_id":15,
            "name":"Update Agent",
            "description":"Allows access to update agent.",
            "status":"active"
        },
        {
            "id":42,
            "permission_group_id":15,
            "name":"Delete Agent",
            "description":"Allows access to delete agent.",
            "status":"active"
        },
        {
            "id":43,
            "permission_group_id":16,
            "name":"TopUp Wallets",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":44,
            "permission_group_id":16,
            "name":"Debit Wallets",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":45,
            "permission_group_id":16,
            "name":"View Wallets",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":46,
            "permission_group_id":16,
            "name":"Make Payment Against Invoice",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":47,
            "permission_group_id":16,
            "name":"Make Advance Payment",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":48,
            "permission_group_id":16,
            "name":"Make Payment Against Deductions",
            "description":"Allows access to Manage Credit.",
            "status":"active"
        },
        {
            "id":49,
            "permission_group_id":17,
            "name":"View Domain",
            "description":"Allows access to manage domain.",
            "status":"active"
        },
        {
            "id":50,
            "permission_group_id":17,
            "name":"Create Domain",
            "description":"Allows access to manage domain.",
            "status":"active"
        },
        {
            "id":51,
            "permission_group_id":17,
            "name":"Update Domain",
            "description":"Allows access to manage domain.",
            "status":"active"
        },
        {
            "id":52,
            "permission_group_id":18,
            "name":"Create Processing Fee",
            "description":"Allows access to create processing fee.",
            "status":"active"
        },
        {
            "id":53,
            "permission_group_id":18,
            "name":"Update Processing Fee",
            "description":"Allows access to update processing fee.",
            "status":"active"
        },
        {
            "id":54,
            "permission_group_id":18,
            "name":"View Processing Fee",
            "description":"Allows access to view processing fee.",
            "status":"active"
        },
        {
            "id":55,
            "permission_group_id":19,
            "name":"View Invoice Details",
            "description":"Allow access to view the invoice details",
            "status":"active"
        },
        {
            "id":56,
            "permission_group_id":20,
            "name":"View Roles",
            "description":"Allows access to manage roles.",
            "status":"active"
        },
        {
            "id":57,
            "permission_group_id":20,
            "name":"Create Roles",
            "description":"Allows access to manage roles.",
            "status":"active"
        },
        {
            "id":58,
            "permission_group_id":20,
            "name":"Update Roles",
            "description":"Allows access to manage roles.",
            "status":"active"
        },
        {
            "id":59,
            "permission_group_id":20,
            "name":"Delete Roles",
            "description":"Allows access to manage roles.",
            "status":"active"
        },
        {
            "id":60,
            "permission_group_id":20,
            "name":"Assign Permissions",
            "description":"Allows access to Assign Permissions",
            "status":"active"
        },
        {
            "id":61,
            "permission_group_id":11,
            "name":"Resend Create Password Email",
            "description":"Allows access to resend create password email.",
            "status":"active"
        },
        {
            "id":62,
            "permission_group_id":3,
            "name":"View Credit History Report",
            "description":"Allows access to Credit History.",
            "status":"active"
        },
        {
            "id":63,
            "permission_group_id":3,
            "name":"View Wallet Payments Report",
            "description":"Allows access to Wallet History.",
            "status":"active"
        },
        {
            "id":64,
            "permission_group_id":3,
            "name":"Credit Summary Report Download",
            "description":"Allows download of credit summary report.",
            "status":"active"
        },
        {
            "id":65,
            "permission_group_id":3,
            "name":"Credit History Report Download",
            "description":"Allows download of credit history report.",
            "status":"active"
        },
        {
            "id":66,
            "permission_group_id":3,
            "name":"Wallet Payments Report Download",
            "description":"Allows download of wallet payments report.",
            "status":"active"
        },
        {
            "id":67,
            "permission_group_id":2,
            "name":"Airline Bookings Report Download",
            "description":"Allows download of airline booking report.",
            "status":"active"
        },
        {
            "id":68,
            "permission_group_id":4,
            "name":"Cancellation Bookings Report Download",
            "description":"Allows download of cancellation report.",
            "status":"active"
        },
        {
            "id":69,
            "permission_group_id":6,
            "name":"Distress Report Download",
            "description":"Allows download of distress report.",
            "status":"active"
        },
        {
            "id":70,
            "permission_group_id":7,
            "name":"Ageing Report Download",
            "description":"Allows download of ageing report.",
            "status":"active"
        },
        {
            "id":71,
            "permission_group_id":21,
            "name":"Client Wise Report Download",
            "description":"Allows download of client wise report.",
            "status":"active"
        },
        {
            "id":72,
            "permission_group_id":21,
            "name":"View Client Wise Report",
            "description":"Allows access to client wise report.",
            "status":"active"
        },
        {
            "id":73,
            "permission_group_id":22,
            "name":"PNR Mismatch",
            "description":"Allows access to PNR mismatch report.",
            "status":"active"
        },
        {
            "id":74,
            "permission_group_id":4,
            "name":"Download Credit Note",
            "description":"Allows download of credit note.",
            "status":"active"
        },
        {
            "id":75,
            "permission_group_id":23,
            "name":"Processing LCC Reconciliation",
            "description":"Allows access to LCC reconciliation report.",
            "status":"active"
        },
        {
            "id":76,
            "permission_group_id":24,
            "name":"Manage PNR",
            "description":"Allows access to manage pnr.",
            "status":"active"
        },
        {
            "id":77,
            "permission_group_id":20,
            "name":"View Permissions",
            "description":"Allows viewing of permissions and permission groups.",
            "status":"active"
        },
        {
            "id":78,
            "permission_group_id":20,
            "name":"Create Permissions",
            "description":"Allows creating new permissions and permission groups.",
            "status":"active"
        },
        {
            "id":79,
            "permission_group_id":20,
            "name":"Update Permissions",
            "description":"Allows updating permissions and permission groups.",
            "status":"active"
        },
        {
            "id":80,
            "permission_group_id":20,
            "name":"Delete Permissions",
            "description":"Allows deleting permissions and permission groups.",
            "status":"active"
        }
    ]

    for permission_data in permissions:

        existing_permission = (
            db.query(Permission)
            .filter(Permission.id == permission_data["id"])
            .first()
        )

        if not existing_permission:
            db.add(
                Permission(**permission_data)
            )

    db.commit()