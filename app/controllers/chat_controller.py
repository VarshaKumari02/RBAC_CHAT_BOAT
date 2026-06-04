from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.users import User
from app.services.llm_service import generate_llm_response
from app.schemas.chat import ChatResponse
import json
import re

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
    "organizations": """
Table: organizations
Columns:
  - id (Integer, Primary Key)
  - name (String)
  - description (String)
  - organization_type (Enum: 'government', 'private', 'travel_agent')
  - wallet_access (Enum: 'yes', 'no')
  - status (Enum: 'active', 'inactive')
    """,
    "bookings": """
Table: bookings
Columns:
  - id (Integer, Primary Key)
  - user_id (Integer, ForeignKey to users.id)
  - organization_id (Integer, ForeignKey to organizations.id)
  - booking_reference (String)
  - booking_type (String)
  - booking_status (String)
  - base_amount (Decimal)
  - total_taxes (Decimal)
  - total_fees (Decimal)
  - total_amount (Decimal)
  - created_at (DateTime)
    """,
    "flight_segments": """
Table: flight_segments (FlightSegment)
Columns:
  - id (Integer, Primary Key)
  - booking_id (Integer, ForeignKey to bookings.id)
  - flight_number (String)
  - departure_airport (String)
  - arrival_airport (String)
  - departure_date (DateTime)
  - arrival_date (DateTime)
  - seat_class (String)
  - ticket_price (Decimal)
  - pnr (String)
  - airline_pnr (String)
    """,
    "booking_travellers": """
Table: booking_travellers (BookingTraveller)
Columns:
  - id (Integer, Primary Key)
  - bookings_id (Integer, ForeignKey to bookings.id)
  - flight_segment_id (Integer, ForeignKey to flight_segments.id)
  - firstname (String)
  - lastname (String)
  - email (String)
  - mobile (String)
  - passport_number (String)
  - seat_number (String)
  - status (String)
    """,
    "wallets": """
Table: wallets
Columns:
  - id (Integer, Primary Key)
  - wallet_code (String)
  - organization_id (Integer, ForeignKey to organizations.id)
  - balance (Decimal)
  - currency_code (String)
  - wallet_type (Enum: 'limited', 'unlimited')
  - status (Enum: 'active', 'inactive')
    """,
    "wallet_transactions": """
Table: wallet_transactions
Columns:
  - id (Integer, Primary Key)
  - wallet_id (Integer, ForeignKey to wallets.id)
  - transaction_by (Integer, ForeignKey to users.id)
  - transaction_type (Enum: 'credit', 'debit')
  - amount (Decimal)
  - status (Enum: 'pending', 'completed', 'failed')
  - created_at (DateTime)
    """,
    "ltc_users": """
Table: ltc_users (LtcUser)
Columns:
  - id (Integer, Primary Key)
  - user_id (Integer, ForeignKey to users.id)
  - firstname (String)
  - lastname (String)
  - organization_id (Integer, ForeignKey to organizations.id)
    """
}

def select_schemas(query: str) -> str:
    selected = ["users"] # Always include users
    
    role_kw = ["role", "permission", "group", "privilege", "access"]
    booking_kw = ["booking", "flight", "traveller", "passenger", "pnr", "ticket", "segment"]
    wallet_kw = ["wallet", "transaction", "balance", "money", "credit", "debit", "funds"]
    org_kw = ["org", "organization", "company", "department"]
    
    if any(k in query for k in role_kw):
        selected.extend(["roles", "permissions", "permission_groups", "role_has_permissions", "user_has_roles"])
    if any(k in query for k in booking_kw):
        selected.extend(["bookings", "flight_segments", "booking_travellers"])
    if any(k in query for k in wallet_kw):
        selected.extend(["wallets", "wallet_transactions"])
    if any(k in query for k in org_kw):
        selected.extend(["organizations", "ltc_users"])
        
    unique_selected = []
    for s in selected:
        if s not in unique_selected and s in TABLE_SCHEMAS:
            unique_selected.append(s)
            
    # Default to sending all schemas if it doesn't clearly match a keyword to remain flexible
    if len(unique_selected) <= 1:
        unique_selected = list(TABLE_SCHEMAS.keys())
        
    return "\n".join([TABLE_SCHEMAS[name] for name in unique_selected])

def handle_chat(message: str, current_user: User, db: Session) -> ChatResponse:
    query = message.lower()
    
    # 1. Select relevant table schemas based on query keywords
    schemas = select_schemas(query)
    
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
    
    # 2. Prompt LLM to write a SQL query or reply generally
    sql_prompt = (
        "You are an expert PostgreSQL database analyst.\n"
        "Given these database schemas:\n"
        f"{schemas}\n\n"
        f"Context details of the logged-in user:\n"
        f"  - user_id = {current_user.id}\n"
        f"  - user_type = '{user_type_str}'\n"
        f"  - user_permissions = {user_permissions_list}\n\n"
        "IMPORTANT RULES:\n"
        f"1. STRICT PERMISSIONS & DATA ACCESS:\n"
        f"   - Normal Users (user_type != 'itdc'): Can ONLY see their own data. For any query, you MUST append `WHERE user_id = {current_user.id}`. If they ask for global tables that do not have a user_id (e.g., 'roles', 'permissions', 'all users'), you MUST REFUSE by returning a plain text message: 'You do not have permission to view this.' DO NOT write SQL.\n"
        f"   - Admin Users (user_type == 'itdc'): To query global or system-wide data (e.g. ALL bookings, ALL users), they MUST possess a logically relevant permission in their `user_permissions` list. If they have the permission, DO NOT append `WHERE user_id = {current_user.id}` to the query; you must query the entire table globally. If they lack an appropriate permission, you MUST REFUSE by returning a plain text message. DO NOT write SQL.\n"
        "2. If the user has permission and asks about database contents, you MUST generate a valid SQL query. Do NOT guess or write plain text, because you do not know the values in the database until you query them.\n"
        "3. If the user's message is a simple greeting (e.g. 'hi', 'hello'), respond with plain text directly (do NOT write SQL).\n"
        "4. Wrap the generated SQL inside a ```sql and ``` code block.\n"
        "5. Limit query results to 10 rows maximum.\n"
        "6. Do NOT write any INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.\n\n"
        "EXAMPLES:\n"
        "User: hi -> Output: Hello! How can I help you today?\n"
        "User: what are the roles in my db (if user_type='itdc' and 'view_roles' in permissions) -> Output: ```sql\\nSELECT name FROM roles;\\n```\n"
        "User: what are the roles in my db (if user lacks permission) -> Output: You do not have permission to view the roles.\n"
        f"User: show my bookings and flight details -> Output: ```sql\\nSELECT b.booking_reference, b.booking_status, fs.flight_number, fs.departure_airport, fs.arrival_airport FROM bookings b JOIN flight_segments fs ON b.id = fs.booking_id WHERE b.user_id = {current_user.id};\\n```\n"
        "User: what are the total bookings? (if user_type='itdc' and 'view_bookings' in permissions) -> Output: ```sql\\nSELECT COUNT(*) FROM bookings;\\n```\n"
        "User: what is the total revenue? (if user_type='itdc' and 'view_bookings' in permissions) -> Output: ```sql\\nSELECT SUM(total_amount) FROM bookings;\\n```\n\n"
        f"User Message: {message}\n"
        "Answer:"
    )

    try:
        sql_response = generate_llm_response(sql_prompt)
        
        # 3. Check if LLM output contains a SQL block
        sql_match = re.search(r'```sql\s*(.*?)\s*```', sql_response, re.DOTALL | re.IGNORECASE)
        
        if not sql_match:
            # It's a general text response or greeting. Sanitize and return directly.
            clean_response = sql_response.replace('\n', ' ').replace('\r', ' ').replace('**', '').replace('*', '')
            clean_response = re.sub(r'\s+', ' ', clean_response).strip()
            return ChatResponse(response=clean_response, intent_detected="General")
            
        sql_query = sql_match.group(1).strip()
        
        # 4. Safe SQL validation checks
        sql_upper = sql_query.upper()
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE"]
        is_safe = sql_upper.startswith("SELECT") and not any(f in sql_upper for f in forbidden)
        
        if not is_safe:
            return ChatResponse(
                response="For security reasons, I can only execute read-only queries. Please rephrase your request.",
                intent_detected="Blocked"
            )
            
        # 4.5. Python-level RBAC Table Restrictions
        # Check if the query is attempting to view global data (no user_id or organization_id filter)
        is_global_query = not re.search(r'(user_id|organization_id|users\.id)\s*(=|IN|IS)', sql_query, re.IGNORECASE)
        tables_requested = sql_query.lower()
        
        # 1. Strict System Tables (Roles & Permissions)
        sys_tables = ["roles", "permissions", "permission_groups", "role_has_permissions", "user_has_roles"]
        if any(re.search(rf'\b{t}\b', tables_requested) for t in sys_tables):
            if user_type_str != 'itdc':
                return ChatResponse(response="You do not have permission to view global system data like roles or permissions.", intent_detected="Blocked")
            if not any("role" in p.lower() or "permission" in p.lower() for p in user_permissions_list):
                return ChatResponse(response="You do not have the required admin permission to view roles or permissions.", intent_detected="Blocked")

        # 2. Global Data Queries (Bookings, Wallets, Users)
        if is_global_query:
            if user_type_str != 'itdc':
                # Normal users must always have a user_id or organization_id filter
                return ChatResponse(response="You do not have permission to view global system data. Please ask about your own data.", intent_detected="Blocked")
                
            # For ITDC users, check specific permissions for the requested global data
            # Check Bookings
            if any(re.search(rf'\b{t}\b', tables_requested) for t in ["bookings", "flight_segments", "booking_travellers"]):
                if not any("booking" in p.lower() or "flight" in p.lower() for p in user_permissions_list):
                    return ChatResponse(response="You do not have the required admin permission to view system-wide bookings.", intent_detected="Blocked")
                    
            # Check Wallets
            if any(re.search(rf'\b{t}\b', tables_requested) for t in ["wallets", "wallet_transactions"]):
                if not any("wallet" in p.lower() or "transaction" in p.lower() for p in user_permissions_list):
                    return ChatResponse(response="You do not have the required admin permission to view system-wide wallets.", intent_detected="Blocked")
                    
            # Check Users
            if re.search(r'\busers\b', tables_requested):
                if not any("user" in p.lower() for p in user_permissions_list):
                    return ChatResponse(response="You do not have the required admin permission to view system-wide users.", intent_detected="Blocked")

        # 5. Execute the SQL query on the database
        result = db.execute(text(sql_query))
        columns = list(result.keys())
        rows = result.fetchall()
        
        # Format the query dataset rows, safely converting types to string
        formatted_results = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                if hasattr(val, "isoformat"):
                    row_dict[col] = val.isoformat()
                elif hasattr(val, "to_eng_string") or hasattr(val, "real"):
                    row_dict[col] = str(val)
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
