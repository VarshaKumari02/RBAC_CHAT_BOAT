"""
main.py — FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Database engine + Base ────────────────────────────────────────────────────
from app.database.database import engine, Base

# ── Import ALL models so SQLAlchemy / Alembic knows about every table ─────────
from app.models import (
    users,
    roles,
    permission,
    permission_groups,
    role_has_permissions,
    user_has_role,
    organizations,
    bookings,
    booking_flights,
    booking_travellers,
    booking_payments,
    wallets,
    wallet_transaction,
    ltc_user,
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import auth, roles, permissions, organizations, bookings, chat



# ── Lifespan: runs once on startup & shutdown ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created / verified.")
    yield


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="RBAC RAG Chatbot API",
    description="Role-Based Access Control + RAG powered chatbot backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS (allow all origins in development) ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(organizations.router)
app.include_router(bookings.router)
app.include_router(chat.router)



# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "RBAC RAG Chatbot API is running"}
