from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.users import User
from app.services.llm_service import generate_llm_response
from app.schemas.chat import ChatResponse
from decimal import Decimal
import json
import re

# Permissions that allow viewing booking data globally (ITDC admin only)
BOOKING_VIEW_PERMISSIONS = {
    "View Booking Monitor",
    "View Booking Report",
    "View Rescheduled Booking Report",
    "Hold Booking Report",
    "View Cancellation Report",
    "Cancellation Request",
    "View Cancellation Details",
    "Initiate Cancellation Request",
    "View Distress Report",
    "View Ageing Report",
    "Airline Bookings Report Download",
    "Cancellation Bookings Report Download",
    "Distress Report Download",
    "Ageing Report Download",
    "Client Wise Report Download",
    "View Client Wise Report",
    "PNR Mismatch",
    "Manage PNR",
    "Preview Refund",
    "Initiate Refund for Credit",
    "Initiate Refund for Direct Payment",
    "Download Credit Note",
    "Processing LCC Reconciliation",
}

# Permissions that allow viewing wallet/credit data globally (ITDC admin only)
WALLET_VIEW_PERMISSIONS = {
    "View Wallets",
    "TopUp Wallets",
    "Debit Wallets",
    "Make Payment Against Invoice",
    "Make Advance Payment",
    "Make Payment Against Deductions",
    "View Credit Summary Report",
    "View Credit History Report",
    "View Wallet Payments Report",
    "Credit Summary Report Download",
    "Credit History Report Download",
    "Wallet Payments Report Download",
    "View Invoice Details",
}

# Permissions that allow viewing user records globally (ITDC admin only)
USER_VIEW_PERMISSIONS = {
    "View LTC Users",
    "View B2C Users",
    "View B2G Users",
    "Create B2G Users",
    "Update B2G Users",
    "Delete B2G Users",
    "View ATT Users",
    "Create ATT Users",
    "Update ATT Users",
    "Delete ATT Users",
    "View CAPF Users",
    "Create CAPF Users",
    "Update CAPF Users",
    "Delete CAPF Users",
    "View Admin Users",
    "Create Admin Users",
    "Update Admin Users",
    "Delete Admin Users",
    "Change Status",
    "Resend Create Password Email",
}

# Permissions that allow viewing roles/permissions tables (ITDC admin only)
ROLE_PERMISSION_VIEW_PERMISSIONS = {
    "View Roles",
    "Create Roles",
    "Update Roles",
    "Delete Roles",
    "Assign Permissions",
    "View Permissions",
    "Create Permissions",
    "Update Permissions",
    "Delete Permissions",
}

TABLE_SCHEMAS = {
    "users": """
Table: users
Columns:
  - id (Integer, Primary Key)
  - username (String)
  - email (String)
  - mobile (String)
  - name (String)
  - user_type (Enum: 'b2c', 'att', 'b2g', 'capf', 'ltc', 'itdc')
  - status (Enum: 'pending', 'active', 'blocked')
  - verified_at (DateTime)
  - created_at (DateTime)
    """,
    "roles": """
Table: roles
Columns:
  - id (Integer, Primary Key)
  - name (String)
  - description (String)
  - status (Enum: 'active', 'inactive')
    """,
    "permissions": """
Table: permissions
Columns:
  - id (Integer, Primary Key)
  - permission_group_id (Integer, ForeignKey to permission_groups.id)
  - name (String)
  - description (String)
  - status (String: 'active', 'deleted')
    """,
    "permission_groups": """
Table: permission_groups
Columns:
  - id (Integer, Primary Key)
  - name (String)
  - description (String)
  - status (Enum: 'active', 'inactive')
    """,
    "role_has_permissions": """
Table: role_has_permissions
Columns:
  - role_id (Integer, ForeignKey to roles.id)
  - permission_id (Integer, ForeignKey to permissions.id)
    """,
    "user_has_roles": """
Table: user_has_roles
Columns:
  - user_id (Integer, ForeignKey to users.id)
  - role_id (Integer, ForeignKey to roles.id)
  - organization_id (Integer, ForeignKey to organizations.id, Nullable)
    """,
    "bookings": """
Table: bookings
Columns:
  - id (BigInteger, Primary Key)
  - user_id (BigInteger, ForeignKey to users.id, nullable)
  - organization_id (BigInteger, nullable)
  - booking_reference (String)
  - booking_type (Enum: 'flight', 'hotel', 'train')
  - booking_status (Enum: 'pending', 'confirmed', 'cancelled', 'expired')
  - journey_type (Enum: 'one_way', 'round_trip', 'multi_cities', nullable)
  - base_amount (Decimal)
  - total_taxes (Decimal)
  - total_fees (Decimal, nullable)
  - total_amount (Decimal)
  - remark (Text, nullable)
  - issuing_authority (String, nullable)
  - booking_resource (String, nullable)
  - booking_expires_at (DateTime, nullable)
  - created_at (DateTime)
  - updated_at (DateTime)
    """,
    "flight_segments": """
Table: flight_segments (FlightSegment)
Columns:
  - id (BigInteger, Primary Key)
  - booking_id (BigInteger, ForeignKey to bookings.id)
  - flight_number (String)
  - governing_carrier (String, airline code)
  - departure_airport (String, IATA code)
  - departure_terminal (String, nullable)
  - arrival_airport (String, IATA code)
  - arrival_terminal (String, nullable)
  - departure_date (DateTime)
  - arrival_date (DateTime)
  - elapsed_time (Integer, flight duration in minutes)
  - seat_class (String)
  - ticket_price (Decimal)
  - brand_name (String, nullable)
  - pnr (String, nullable)
  - airline_pnr (String, nullable)
  - from_city (String)
  - to_city (String)
  - is_layover (Enum: 'yes', 'no')
  - trip_type (Enum: 'international', 'domestic')
  - journey_type (String, nullable)
  - status (Enum: 'scheduled', 'cancelled', 'completed', 'failed')
  - created_at (DateTime)
    """,
    "booking_travellers": """
Table: booking_travellers (BookingTraveller)
Columns:
  - id (BigInteger, Primary Key)
  - bookings_id (BigInteger, ForeignKey to bookings.id)   -- NOTE: column is 'bookings_id'
  - booking_flights_id (BigInteger, ForeignKey to flight_segments.id)  -- NOTE: column is 'booking_flights_id'
  - firstname (String)
  - middlename (String, nullable)
  - lastname (String)
  - email (String)
  - dob (Date, nullable)
  - mobile (String)
  - age (Integer, nullable)
  - gender (Enum: 'M', 'F', 'U')
  - traveller_type (Enum: 'ADT', 'CNN', 'INF', 'STU', 'SCP')
  - passport_number (String, nullable)
  - seat_number (String, nullable)
  - ticket_number (String, nullable)
  - pnr (String, nullable)
  - airline_pnr (String, nullable)
  - status (Enum: 'pending', 'confirmed', 'cancelled', 'failed')
  - organization_id (BigInteger, nullable)
  - created_at (DateTime)
    """,
    "wallets": """
Table: wallets
Columns:
  - id (BigInteger, Primary Key)
  - wallet_code (String, unique)
  - organization_id (BigInteger, ForeignKey to organizations.id)
  - balance (Decimal)
  - currency_code (String, default 'INR')
  - wallet_type (Enum: 'limited', 'unlimited')
  - wallet_limit_value (Decimal, nullable)
  - status (Enum: 'active', 'pending', 'blocked', 'inactive')
  - last_transaction_at (DateTime, nullable)
  - created_at (DateTime)
    """,
    "wallet_transactions": """
Table: wallet_transactions
Columns:
  - id (BigInteger, Primary Key)
  - transaction_code (String, unique)
  - wallet_id (BigInteger, ForeignKey to wallets.id)
  - transaction_by (BigInteger, ForeignKey to users.id)
  - transaction_method (Enum: 'bank transfer', 'card', 'manual adjustment')
  - transaction_type (Enum: 'credit', 'debit', 'refund', 'adjustment')
  - credit_source (Enum: 'credit card', 'net banking', 'debit card', 'wallet', 'upi', nullable)
  - amount (Decimal)
  - previous_balance (Decimal, nullable)
  - current_balance (Decimal, nullable)
  - description (String)
  - status (Enum: 'pending', 'completed', 'failed', 'reversed')
  - transaction_utr (String, nullable)
  - created_at (DateTime)
    """,
    "payment_transactions": """
Table: payment_transactions
Columns:
  - id (BigInteger, Primary Key)
  - transaction_code (String, unique)
  - bookings_id (BigInteger, ForeignKey to bookings.id)
  - wallet_transactions_id (BigInteger, ForeignKey to wallet_transactions.id, nullable)
  - initiated_by (BigInteger, ForeignKey to users.id)
  - transaction_type (Enum: 'payment', 'refund')
  - amount (Decimal)
  - gateway_transaction_id (String, nullable)
  - parent_payment_transaction_id (String, nullable)
  - remarks (Text, nullable)
  - payment_status (String)
  - payment_method_code (String, nullable)
  - transaction_mode (Enum: 'online', 'offline')
  - created_at (DateTime)
    """,
    "ltc_users": """
Table: ltc_users (LtcUser)
Columns:
  - user_id (BigInteger, Primary Key, ForeignKey to users.id)  -- NOTE: PK is user_id, not id
  - firstname (String)
  - middlename (String, nullable)
  - lastname (String)
  - gender (Enum: 'm', 'f', 'o')
  - organization_id (BigInteger, ForeignKey to organizations.id, nullable)
  - department_id (BigInteger, nullable)
  - ltc_organization_name (String, nullable)
  - ltc_department_name (String, nullable)
  - identification_number (String, nullable)
  - wallet_access (Enum: 'yes', 'no')
  - created_at (DateTime)
    """,
    "organizations": """
Table: organizations
Columns:
  - id (Integer, Primary Key)
  - name (String, unique)
  - description (String, nullable)
  - organization_type (Enum: 'government', 'psu')  -- NOTE: only government and psu types exist
  - wallet_access (Boolean, true/false)             -- NOTE: Boolean, not enum
  - status (Enum: 'active', 'blocked')
  - created_at (DateTime)
    """
}

def select_schemas(query: str) -> tuple[str, list[str]]:
    selected = ["users"]
    
    role_kw   = ["role", "permission", "privilege"]
    booking_kw = ["booking", "flight", "traveller", "passenger", "pnr", "ticket", "segment",
                  "cancellation", "refund", "rescheduled", "distress", "ageing", "hold"]
    wallet_kw  = ["wallet", "balance", "credit", "debit", "funds", "invoice", "payment", "topup"]
    org_kw     = ["org", "organization", "company", "department", "agent"]
    
    if any(k in query for k in role_kw):
        selected.extend(["roles", "permissions", "permission_groups", "role_has_permissions", "user_has_roles"])
    if any(k in query for k in booking_kw):
        selected.extend(["bookings", "flight_segments", "booking_travellers", "payment_transactions"])
    if any(k in query for k in wallet_kw):
        selected.extend(["wallets", "wallet_transactions", "payment_transactions"])
    if any(k in query for k in org_kw):
        selected.extend(["organizations", "ltc_users"])
        
    unique_selected = []
    for s in selected:
        if s not in unique_selected and s in TABLE_SCHEMAS:
            unique_selected.append(s)
            
    # If nothing matched, only send the user-safe schemas (not everything)
    if len(unique_selected) <= 1:
        unique_selected = ["users", "bookings", "flight_segments", "booking_travellers", "payment_transactions"]
        
    return "\n".join([TABLE_SCHEMAS[name] for name in unique_selected]), unique_selected

def handle_chat(message: str, current_user: User, db: Session) -> ChatResponse:
    if not message or not message.strip():
        return ChatResponse(response="Please type a message before sending.", intent_detected="General")
    if len(message) > 500:
        return ChatResponse(response="Your message is too long. Please keep it under 500 characters.", intent_detected="General")

    query = message.lower()
    
    # 1. Select relevant table schemas based on query keywords
    schemas, selected_tables = select_schemas(query)
    
    # Get current user details for context
    user_type_str = current_user.user_type.value if hasattr(current_user.user_type, "value") else current_user.user_type
    
    # Fetch user permissions for strict RBAC enforcement
    permissions_query = text("""
        SELECT p.name 
        FROM permissions p
        JOIN role_has_permissions rhp ON p.id = rhp.permission_id
        JOIN user_has_roles uhr ON rhp.role_id = uhr.role_id
        WHERE uhr.user_id = :user_id AND p.status = 'active'
    """)
    perm_result = db.execute(permissions_query, {"user_id": current_user.id}).fetchall()
    user_permissions_list = [row[0] for row in perm_result]
    
    # Optimize tokens by filtering permissions to only those relevant to the selected tables
    filtered_permissions = []
    selected_tables_set = set(selected_tables)
    if selected_tables_set.intersection({"bookings", "flight_segments", "booking_travellers", "payment_transactions"}):
        filtered_permissions.extend([p for p in user_permissions_list if p in BOOKING_VIEW_PERMISSIONS])
    if selected_tables_set.intersection({"wallets", "wallet_transactions", "payment_transactions"}):
        filtered_permissions.extend([p for p in user_permissions_list if p in WALLET_VIEW_PERMISSIONS])
    if "users" in selected_tables_set:
        filtered_permissions.extend([p for p in user_permissions_list if p in USER_VIEW_PERMISSIONS])
    if selected_tables_set.intersection({"roles", "permissions", "permission_groups", "role_has_permissions", "user_has_roles"}):
        filtered_permissions.extend([p for p in user_permissions_list if p in ROLE_PERMISSION_VIEW_PERMISSIONS])
    filtered_permissions = list(set(filtered_permissions))
    
    # 2. Prompt LLM to write a SQL query or reply generally
    sql_prompt = (
        "You are an expert PostgreSQL database analyst.\n"
        "Given these database schemas:\n"
        f"{schemas}\n\n"
        f"Context details of the logged-in user:\n"
        f"  - user_id = {current_user.id}\n"
        f"  - user_type = '{user_type_str}'\n"
        f"  - user_permissions = {filtered_permissions}\n\n"
        "IMPORTANT RULES:\n"
        f"1. STRICT PERMISSIONS & DATA ACCESS:\n"
        f"   - Normal Users (user_type != 'itdc'): Can ONLY see their own data. For any query, you MUST append `WHERE user_id = {current_user.id}`. If they ask for global tables that do not have a user_id (e.g., 'roles', 'permissions', 'all users'), you MUST REFUSE by returning a plain text message: 'You do not have permission to view this.' DO NOT write SQL.\n"
        f"   - Admin Users (user_type == 'itdc'): To query global or system-wide data (e.g. ALL bookings, ALL users), they MUST possess a logically relevant permission in their `user_permissions` list. If they have the permission, DO NOT append `WHERE user_id = {current_user.id}` to the query; you must query the entire table globally. If they lack an appropriate permission, you MUST REFUSE by returning a plain text message. DO NOT write SQL.\n"
        "2. If the user has permission and asks about database contents, you MUST generate a valid SQL query. Do NOT guess or write plain text, because you do not know the values in the database until you query them.\n"
        "3. If the user's message is a simple greeting (e.g. 'hi', 'hello'), respond with plain text directly (do NOT write SQL).\n"
        "4. Wrap the generated SQL inside a ```sql and ``` code block.\n"
        "5. Limit query results to 10 rows maximum.\n"
        "6. Do NOT write any INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.\n\n"
        "IMPORTANT SCHEMA NOTES:\n"
        "- In 'booking_travellers', the FK to bookings is 'bookings_id' (not 'booking_id').\n"
        "- In 'booking_travellers', the FK to flight_segments is 'booking_flights_id' (not 'flight_segment_id').\n\n"
        "EXAMPLES:\n"
        "User: hi -> Output: Hello! How can I help you today?\n"
        "User: what are the roles? (if user_type='itdc' and has 'View Roles' permission) -> Output: ```sql\\nSELECT name, description FROM roles;\\n```\n"
        "User: what are the roles? (if user lacks permission) -> Output: You do not have permission to view the roles.\n"
        f"User: what is my roles? -> Output: ```sql\\nSELECT r.name, r.description FROM roles r JOIN user_has_roles uhr ON r.id = uhr.role_id WHERE uhr.user_id = {current_user.id};\\n```\n"
        f"User: show my bookings and flight details -> Output: ```sql\\nSELECT b.booking_reference, b.booking_status, fs.flight_number, fs.from_city, fs.to_city, fs.departure_date FROM bookings b JOIN flight_segments fs ON b.id = fs.booking_id WHERE b.user_id = {current_user.id};\\n```\n"
        "User: total bookings? (if user_type='itdc' and has 'View Booking Monitor' permission) -> Output: ```sql\\nSELECT COUNT(*) FROM bookings;\\n```\n"
        "User: total revenue? (if user_type='itdc' and has 'View Booking Report' permission) -> Output: ```sql\\nSELECT SUM(total_amount) FROM bookings;\\n```\n\n"
        f"User Message: {message}\n"
        "Answer:"
    )

    try:
        sql_response = generate_llm_response(sql_prompt)
        
        # 3. Check if LLM output contains a SQL block
        sql_match = re.search(r'```sql\s*(.*?)\s*```', sql_response, re.DOTALL | re.IGNORECASE)
        
        if not sql_match:
            clean_response = sql_response.replace('\n', ' ').replace('\r', ' ').replace('**', '').replace('*', '')
            clean_response = re.sub(r'\s+', ' ', clean_response).strip()
            return ChatResponse(response=clean_response, intent_detected="General")
            
        sql_query = sql_match.group(1).strip()
        
        # 4. Safe SQL validation checks
        sql_upper = sql_query.upper()
        # Use regex word boundaries to prevent matching substrings (like 'created_at' matching 'CREATE')
        is_safe = sql_upper.startswith("SELECT") and not bool(
            re.search(r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|UNION)\b', sql_upper)
        )
        
        if not is_safe:
            return ChatResponse(
                response="For security reasons, I can only execute read-only queries. Please rephrase your request.",
                intent_detected="Blocked"
            )
            
        # 4.5. Python-level RBAC Table Restrictions (uses EXACT permission name sets)
        user_perm_set = set(user_permissions_list)
        tables_requested = sql_query.lower()

        # Check if the SQL has a filter scoped to THIS specific user
        has_own_user_filter = bool(
            re.search(rf'(user_id|users\.id)\s*=\s*{current_user.id}\b', sql_query, re.IGNORECASE)
        )

        if not has_own_user_filter and re.search(r'\bfrom\s+users\b', sql_query, re.IGNORECASE):
            has_own_user_filter = bool(
                re.search(rf'\bid\s*=\s*{current_user.id}\b', sql_query, re.IGNORECASE)
            )

        # A query is global if it has no user-specific filter
        is_global_query = not has_own_user_filter

        # 1. Strict System Tables (Roles & Permissions) — ITDC only with exact permission
        sys_tables = ["roles", "permissions", "permission_groups", "role_has_permissions", "user_has_roles"]
        if any(re.search(rf'\b{t}\b', tables_requested) for t in sys_tables):
            if is_global_query:
                if user_type_str != 'itdc':
                    return ChatResponse(response="You do not have permission to view system data like roles or permissions.", intent_detected="Blocked")
                if not user_perm_set.intersection(ROLE_PERMISSION_VIEW_PERMISSIONS):
                    return ChatResponse(response="You do not have the required permission to view roles or permissions.", intent_detected="Blocked")

        # 2. For normal (non-itdc) users — must always query only their own data
        if user_type_str != 'itdc' and is_global_query:
            return ChatResponse(
                response="You can only view your own data. Please ask about your own bookings or profile.",
                intent_detected="Blocked"
            )

        # 3. For ITDC users querying global data — check exact permissions per table
        if user_type_str == 'itdc' and is_global_query:
            if any(re.search(rf'\b{t}\b', tables_requested) for t in ["bookings", "flight_segments", "booking_travellers", "payment_transactions"]):
                if not user_perm_set.intersection(BOOKING_VIEW_PERMISSIONS):
                    return ChatResponse(response="You do not have the required permission to view system-wide booking data.", intent_detected="Blocked")

            # Check Wallets / Transactions / Payment Transactions
            if any(re.search(rf'\b{t}\b', tables_requested) for t in ["wallets", "wallet_transactions", "payment_transactions"]):
                if not user_perm_set.intersection(WALLET_VIEW_PERMISSIONS):
                    return ChatResponse(response="You do not have the required permission to view system-wide wallet data.", intent_detected="Blocked")

            # Check Users table globally
            if re.search(r'\busers\b', tables_requested):
                if not user_perm_set.intersection(USER_VIEW_PERMISSIONS):
                    return ChatResponse(response="You do not have the required permission to view system-wide user data.", intent_detected="Blocked")

        # 5. Enforce LIMIT 10 at Python level (LLM may forget)
        if "limit" not in sql_query.lower():
            sql_query = sql_query.rstrip(";")
            sql_query = sql_query + " LIMIT 10"

        # Execute the SQL query on the database
        result = db.execute(text(sql_query))
        columns = list(result.keys())
        rows = result.fetchall()
        
        # Format the query dataset rows, safely converting types to string
        formatted_results = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                if val is None:
                    row_dict[col] = None
                elif hasattr(val, "isoformat"):
                    row_dict[col] = val.isoformat()
                elif isinstance(val, Decimal):
                    row_dict[col] = float(val)
                else:
                    row_dict[col] = val
            formatted_results.append(row_dict)
            
        # 6. Ask the LLM to format the query results into a nice paragraph response
        final_prompt = (
            "You are an intelligent customer support chatbot assistant for the ITDC Portal.\n"
            f"The user asked: \"{message}\"\n\n"
            "We queried the PostgreSQL database and retrieved these results:\n"
            f"{json.dumps(formatted_results)}\n\n"
            "Guidelines:\n"
            "1. Answer the user's question using the retrieved query results.\n"
            "2. Respond ONLY with a single continuous plain text paragraph. Do NOT use newlines, carriage returns, or line breaks in your output.\n"
            "3. Do NOT use any markdown formatting (like asterisks **, bullet points, lists, or headers).\n"
            "4. ALWAYS use the currency code or symbol from the database (e.g., INR or Rupees). Do NOT output amounts in USD or dollars ($) unless the database records explicitly state it.\n"
            "5. If the database results contain 'null' or 'None' for a sum, count, or total, interpret and state it as 0 (zero) rather than saying 'null' or 'not recorded'.\n"
            "6. Be helpful, professional, friendly, and keep it concise.\n"
            "Answer:"
        )
        
        final_response = generate_llm_response(final_prompt)
        
        # Final sanitization pass
        clean_response = final_response.replace('\n', ' ').replace('\r', ' ').replace('**', '').replace('*', '')
        clean_response = re.sub(r'\s+', ' ', clean_response).strip()
        
        return ChatResponse(
            response=clean_response,
            intent_detected="DatabaseQuery"
        )
        
    except Exception as e:
        print(f"[SQL Chatbot Error]: {str(e)}")
        
        # Fail-safe: Return a static conversational response to prevent LLM hallucinations on error
        return ChatResponse(
            response="I'm sorry, I encountered an error while processing your request. You may not have the necessary permissions, or the query was invalid.",
            intent_detected="ErrorFallback"
        )
