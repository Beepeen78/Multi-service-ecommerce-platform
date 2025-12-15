"""
User Service - Python/FastAPI Implementation
Handles user registration, authentication, and profile management
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import asyncpg
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Service",
    description="User management and authentication service for e-commerce platform",
    version="1.0.0",
    docs_url="/docs",  # Explicitly enable Swagger UI
    redoc_url="/redoc",  # Explicitly enable ReDoc
    openapi_url="/openapi.json"  # Explicitly enable OpenAPI schema
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PORT = int(os.getenv("PORT", "3001"))
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN", "24h")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/ecommerce_users")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None


# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: datetime


class TokenResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


# Database initialization
async def init_db():
    """Initialize database tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: int, email: str) -> str:
    """Create a JWT token"""
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "userId": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def verify_token(authorization: str = Header(None)) -> dict:
    """Verify JWT token from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()
    logger.info(f"User Service listening on port {PORT}")


@app.on_event("shutdown")
async def shutdown():
    """Close database pool on shutdown"""
    if db_pool:
        await db_pool.close()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "user-service", "language": "Python", "framework": "FastAPI"}


# Register new user
@app.post("/register", response_model=TokenResponse, status_code=201)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            # Check if user exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", user_data.email
            )
            if existing:
                raise HTTPException(status_code=409, detail="User already exists")
            
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user
            user = await conn.fetchrow(
                """
                INSERT INTO users (email, password, name)
                VALUES ($1, $2, $3)
                RETURNING id, email, name, created_at
                """,
                user_data.email, hashed_password, user_data.name
            )
            
            # Generate JWT token
            token = create_jwt_token(user["id"], user["email"])
            
            return TokenResponse(
                message="User created successfully",
                user=UserResponse(
                    id=user["id"],
                    email=user["email"],
                    name=user["name"],
                    created_at=user["created_at"]
                ),
                token=token
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Login
@app.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """Login user and return JWT token"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            # Find user
            user = await conn.fetchrow(
                "SELECT id, email, password, name FROM users WHERE email = $1",
                credentials.email
            )
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            if not verify_password(credentials.password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Generate JWT token
            token = create_jwt_token(user["id"], user["email"])
            
            return TokenResponse(
                message="Login successful",
                user=UserResponse(
                    id=user["id"],
                    email=user["email"],
                    name=user["name"],
                    created_at=datetime.utcnow()
                ),
                token=token
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Get user profile (protected route)
@app.get("/profile", response_model=dict)
async def get_profile(payload: dict = Depends(verify_token)):
    """Get current user profile"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        user_id = payload.get("userId")
        
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id, email, name, created_at FROM users WHERE id = $1",
                user_id
            )
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "created_at": user["created_at"].isoformat()
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Get all users (for testing - should be protected in production)
@app.get("/users", response_model=dict)
async def get_all_users():
    """Get all users (testing endpoint)"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT id, email, name, created_at FROM users ORDER BY created_at DESC"
            )
            
            return {
                "users": [
                    {
                        "id": u["id"],
                        "email": u["email"],
                        "name": u["name"],
                        "created_at": u["created_at"].isoformat()
                    }
                    for u in users
                ]
            }
    
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

