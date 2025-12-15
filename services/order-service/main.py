"""
Order Service - Python/FastAPI Implementation
Handles order processing and management
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import asyncpg
import httpx
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Order Service",
    description="Order processing and management service for e-commerce platform",
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
PORT = int(os.getenv("PORT", "3003"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/ecommerce_orders")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:3002")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:3001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:3004")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:3005")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# HTTP client for service-to-service communication
http_client = httpx.AsyncClient(timeout=30.0)


# Pydantic Models
class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str


# Database initialization
async def init_db():
    """Initialize database tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    total_amount DECIMAL(10, 2) NOT NULL,
                    shipping_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


async def verify_user_token(authorization: str) -> Dict:
    """Verify user token by calling User Service"""
    try:
        headers = {"Authorization": authorization}
        response = await http_client.get(f"{USER_SERVICE_URL}/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "userId": data["user"]["id"],
                "email": data["user"]["email"]
            }
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()
    logger.info(f"Order Service listening on port {PORT}")


@app.on_event("shutdown")
async def shutdown():
    """Close database pool and HTTP client on shutdown"""
    if db_pool:
        await db_pool.close()
    await http_client.aclose()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "order-service", "language": "Python", "framework": "FastAPI"}


# Get all orders for a user
@app.get("/", response_model=dict)
async def get_orders(authorization: str = Header(None)):
    """Get all orders for the authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    user = await verify_user_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        async with db_pool.acquire() as conn:
            orders = await conn.fetch("""
                SELECT o.*, 
                       COALESCE(
                           json_agg(
                               json_build_object(
                                   'id', oi.id,
                                   'product_id', oi.product_id,
                                   'quantity', oi.quantity,
                                   'price', oi.price
                               )
                           ) FILTER (WHERE oi.id IS NOT NULL),
                           '[]'
                       ) as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = $1
                GROUP BY o.id
                ORDER BY o.created_at DESC
            """, user["userId"])
            
            return {
                "orders": [
                    {
                        "id": o["id"],
                        "user_id": o["user_id"],
                        "status": o["status"],
                        "total_amount": float(o["total_amount"]),
                        "shipping_address": o["shipping_address"],
                        "items": o["items"],
                        "created_at": o["created_at"].isoformat(),
                        "updated_at": o["updated_at"].isoformat()
                    }
                    for o in orders
                ]
            }
    
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Get order by ID
@app.get("/{order_id}", response_model=dict)
async def get_order(order_id: int, authorization: str = Header(None)):
    """Get a specific order by ID"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    user = await verify_user_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        async with db_pool.acquire() as conn:
            order = await conn.fetchrow(
                "SELECT * FROM orders WHERE id = $1 AND user_id = $2",
                order_id, user["userId"]
            )
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            items = await conn.fetch(
                "SELECT * FROM order_items WHERE order_id = $1",
                order_id
            )
            
            return {
                "order": {
                    "id": order["id"],
                    "user_id": order["user_id"],
                    "status": order["status"],
                    "total_amount": float(order["total_amount"]),
                    "shipping_address": order["shipping_address"],
                    "items": [
                        {
                            "id": item["id"],
                            "product_id": item["product_id"],
                            "quantity": item["quantity"],
                            "price": float(item["price"])
                        }
                        for item in items
                    ],
                    "created_at": order["created_at"].isoformat(),
                    "updated_at": order["updated_at"].isoformat()
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get order error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Create new order
@app.post("/", response_model=dict, status_code=201)
async def create_order(order_data: OrderCreate, authorization: str = Header(None)):
    """Create a new order"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    user = await verify_user_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not order_data.items or len(order_data.items) == 0:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
    
    try:
        # Validate and fetch product details
        total_amount = 0.0
        validated_items = []
        
        for item in order_data.items:
            if item.quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
            
            # Fetch product from Product Service
            try:
                product_response = await http_client.get(
                    f"{PRODUCT_SERVICE_URL}/{item.product_id}"
                )
                
                if product_response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found"
                    )
                
                product_data = product_response.json()
                product = product_data["product"]
                
                if product["stock_quantity"] < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {product['name']}. Available: {product['stock_quantity']}"
                    )
                
                item_total = float(product["price"]) * item.quantity
                total_amount += item_total
                
                validated_items.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": float(product["price"])
                })
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching product {item.product_id}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error validating product {item.product_id}: {str(e)}"
                )
        
        # Create order in database (transaction)
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                # Create order
                order = await conn.fetchrow("""
                    INSERT INTO orders (user_id, total_amount, shipping_address, status)
                    VALUES ($1, $2, $3, 'pending')
                    RETURNING *
                """, user["userId"], total_amount, order_data.shipping_address)
                
                # Insert order items
                for item in validated_items:
                    await conn.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES ($1, $2, $3, $4)
                    """, order["id"], item["product_id"], item["quantity"], item["price"])
                
                # Fetch order items
                items = await conn.fetch(
                    "SELECT * FROM order_items WHERE order_id = $1",
                    order["id"]
                )
                
                return {
                    "message": "Order created successfully",
                    "order": {
                        "id": order["id"],
                        "user_id": order["user_id"],
                        "status": order["status"],
                        "total_amount": float(order["total_amount"]),
                        "shipping_address": order["shipping_address"],
                        "items": [
                            {
                                "id": item["id"],
                                "product_id": item["product_id"],
                                "quantity": item["quantity"],
                                "price": float(item["price"])
                            }
                            for item in items
                        ],
                        "created_at": order["created_at"].isoformat(),
                        "updated_at": order["updated_at"].isoformat()
                    }
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create order error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Update order status
@app.patch("/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    authorization: str = Header(None)
):
    """Update order status"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    user = await verify_user_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        async with db_pool.acquire() as conn:
            order = await conn.fetchrow("""
                UPDATE orders 
                SET status = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2 AND user_id = $3
                RETURNING *
            """, status_update.status, order_id, user["userId"])
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return {
                "order": {
                    "id": order["id"],
                    "user_id": order["user_id"],
                    "status": order["status"],
                    "total_amount": float(order["total_amount"]),
                    "shipping_address": order["shipping_address"],
                    "created_at": order["created_at"].isoformat(),
                    "updated_at": order["updated_at"].isoformat()
                },
                "message": "Order status updated successfully"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update order status error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

