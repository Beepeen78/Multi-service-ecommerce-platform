"""
Product Service - Python/FastAPI Implementation
Handles product catalog management
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncpg
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Service",
    description="Product catalog management service for e-commerce platform",
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
PORT = int(os.getenv("PORT", "3002"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/ecommerce_products")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None


# Pydantic Models
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    image_url: Optional[str]
    stock_quantity: int
    created_at: datetime
    updated_at: datetime


# Database initialization
async def init_db():
    """Initialize database tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(100),
                    image_url VARCHAR(500),
                    stock_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()
    logger.info(f"Product Service listening on port {PORT}")


@app.on_event("shutdown")
async def shutdown():
    """Close database pool on shutdown"""
    if db_pool:
        await db_pool.close()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "product-service", "language": "Python", "framework": "FastAPI"}


# Get all products (with optional search and filter)
@app.get("/", response_model=dict)
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description")
):
    """Get all products with optional filtering"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        param_count = 0
        
        if category:
            param_count += 1
            query += f" AND category = ${param_count}"
            params.append(category)
        
        if search:
            param_count += 1
            query += f" AND (name ILIKE ${param_count} OR description ILIKE ${param_count})"
            params.append(f"%{search}%")
        
        query += " ORDER BY created_at DESC"
        
        async with db_pool.acquire() as conn:
            products = await conn.fetch(query, *params)
            
            return {
                "products": [
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "description": p["description"],
                        "price": float(p["price"]),
                        "category": p["category"],
                        "image_url": p["image_url"],
                        "stock_quantity": p["stock_quantity"],
                        "created_at": p["created_at"].isoformat(),
                        "updated_at": p["updated_at"].isoformat()
                    }
                    for p in products
                ]
            }
    
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Get product by ID
@app.get("/{product_id}", response_model=dict)
async def get_product(product_id: int):
    """Get a specific product by ID"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            product = await conn.fetchrow(
                "SELECT * FROM products WHERE id = $1", product_id
            )
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {
                "product": {
                    "id": product["id"],
                    "name": product["name"],
                    "description": product["description"],
                    "price": float(product["price"]),
                    "category": product["category"],
                    "image_url": product["image_url"],
                    "stock_quantity": product["stock_quantity"],
                    "created_at": product["created_at"].isoformat(),
                    "updated_at": product["updated_at"].isoformat()
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Create product
@app.post("/", response_model=dict, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            new_product = await conn.fetchrow(
                """
                INSERT INTO products (name, description, price, category, image_url, stock_quantity)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                product.name,
                product.description,
                product.price,
                product.category,
                product.image_url,
                product.stock_quantity
            )
            
            return {
                "product": {
                    "id": new_product["id"],
                    "name": new_product["name"],
                    "description": new_product["description"],
                    "price": float(new_product["price"]),
                    "category": new_product["category"],
                    "image_url": new_product["image_url"],
                    "stock_quantity": new_product["stock_quantity"],
                    "created_at": new_product["created_at"].isoformat(),
                    "updated_at": new_product["updated_at"].isoformat()
                },
                "message": "Product created successfully"
            }
    
    except Exception as e:
        logger.error(f"Create product error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Update product
@app.put("/{product_id}", response_model=dict)
async def update_product(product_id: int, product_update: ProductUpdate):
    """Update an existing product"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            # Build update query dynamically
            updates = []
            params = []
            param_count = 0
            
            if product_update.name is not None:
                param_count += 1
                updates.append(f"name = ${param_count}")
                params.append(product_update.name)
            
            if product_update.description is not None:
                param_count += 1
                updates.append(f"description = ${param_count}")
                params.append(product_update.description)
            
            if product_update.price is not None:
                param_count += 1
                updates.append(f"price = ${param_count}")
                params.append(product_update.price)
            
            if product_update.category is not None:
                param_count += 1
                updates.append(f"category = ${param_count}")
                params.append(product_update.category)
            
            if product_update.image_url is not None:
                param_count += 1
                updates.append(f"image_url = ${param_count}")
                params.append(product_update.image_url)
            
            if product_update.stock_quantity is not None:
                param_count += 1
                updates.append(f"stock_quantity = ${param_count}")
                params.append(product_update.stock_quantity)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            param_count += 1
            updates.append(f"updated_at = CURRENT_TIMESTAMP")
            updates.append(f"id = ${param_count}")
            params.append(product_id)
            
            query = f"UPDATE products SET {', '.join(updates[:-1])} WHERE {updates[-1]} RETURNING *"
            
            updated_product = await conn.fetchrow(query, *params)
            
            if not updated_product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {
                "product": {
                    "id": updated_product["id"],
                    "name": updated_product["name"],
                    "description": updated_product["description"],
                    "price": float(updated_product["price"]),
                    "category": updated_product["category"],
                    "image_url": updated_product["image_url"],
                    "stock_quantity": updated_product["stock_quantity"],
                    "created_at": updated_product["created_at"].isoformat(),
                    "updated_at": updated_product["updated_at"].isoformat()
                },
                "message": "Product updated successfully"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Delete product
@app.delete("/{product_id}", response_model=dict)
async def delete_product(product_id: int):
    """Delete a product"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM products WHERE id = $1 RETURNING id", product_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {"message": "Product deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete product error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

