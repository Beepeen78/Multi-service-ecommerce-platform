"""
Payment Service - Python/FastAPI Implementation
Handles payment processing using Stripe and PayPal
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
from jose import jwt
import httpx
from datetime import datetime

app = FastAPI(
    title="Payment Service",
    description="Payment processing service for e-commerce platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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
PORT = int(os.getenv("PORT", "3004"))
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/ecommerce_payments")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# Database connection (using asyncpg or psycopg2)
# For this example, we'll use a simple in-memory store
# In production, use asyncpg for async PostgreSQL access

# Pydantic Models
class PaymentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str = "USD"
    payment_method: str  # "stripe" or "paypal"
    payment_method_id: str  # Stripe payment method ID or PayPal order ID

class PaymentResponse(BaseModel):
    payment_id: str
    order_id: int
    amount: float
    status: str  # "pending", "completed", "failed", "refunded"
    transaction_id: Optional[str] = None
    created_at: datetime

class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # If None, full refund

# JWT Authentication Dependency
def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# In-memory storage (replace with database in production)
payments_db = {}

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "payment-service",
        "language": "Python",
        "framework": "FastAPI"
    }

# Create Payment
@app.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_request: PaymentRequest,
    user: dict = Depends(verify_token)
):
    """
    Process a payment for an order
    Requires JWT authentication
    """
    try:
        # Validate payment method
        if payment_request.payment_method not in ["stripe", "paypal"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment method. Use 'stripe' or 'paypal'"
            )
        
        # Process payment (mock implementation)
        # In production, integrate with actual Stripe/PayPal APIs
        payment_id = f"pay_{datetime.now().timestamp()}"
        transaction_id = f"txn_{payment_request.order_id}_{datetime.now().timestamp()}"
        
        # Simulate payment processing
        # In production:
        # - For Stripe: Use stripe.PaymentIntent.create()
        # - For PayPal: Use PayPal SDK
        
        payment = PaymentResponse(
            payment_id=payment_id,
            order_id=payment_request.order_id,
            amount=payment_request.amount,
            status="completed",  # In production, check actual payment status
            transaction_id=transaction_id,
            created_at=datetime.now()
        )
        
        # Store payment (replace with database)
        payments_db[payment_id] = payment.dict()
        
        return payment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

# Get Payment by ID
@app.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    user: dict = Depends(verify_token)
):
    """Get payment details by payment ID"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_data = payments_db[payment_id]
    return PaymentResponse(**payment_data)

# Refund Payment
@app.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    refund_request: RefundRequest,
    user: dict = Depends(verify_token)
):
    """Process a refund for a payment"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_data = payments_db[payment_id]
    
    # Calculate refund amount
    refund_amount = refund_request.amount or payment_data["amount"]
    
    # In production, call Stripe/PayPal refund API
    # For now, just update status
    payment_data["status"] = "refunded"
    payments_db[payment_id] = payment_data
    
    return {
        "payment_id": payment_id,
        "refund_amount": refund_amount,
        "status": "refunded",
        "refunded_at": datetime.now().isoformat()
    }

# Get Payments by Order ID
@app.get("/order/{order_id}", response_model=List[PaymentResponse])
async def get_payments_by_order(
    order_id: int,
    user: dict = Depends(verify_token)
):
    """Get all payments for a specific order"""
    payments = [
        PaymentResponse(**p) 
        for p in payments_db.values() 
        if p["order_id"] == order_id
    ]
    return payments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

