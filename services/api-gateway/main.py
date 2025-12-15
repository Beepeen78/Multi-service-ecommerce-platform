"""
API Gateway - Python/FastAPI Implementation
Single entry point for all client requests, routes to microservices
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import os
from typing import Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="API Gateway for E-Commerce Platform - Routes requests to microservices",
    version="1.0.0"
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
PORT = int(os.getenv("PORT", "8080"))
TIMEOUT = 60.0  # 60 seconds timeout

# Service URLs
USER_SERVICE = os.getenv("USER_SERVICE_URL", "http://user-service:3001")
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:3002")
ORDER_SERVICE = os.getenv("ORDER_SERVICE_URL", "http://order-service:3003")
PAYMENT_SERVICE = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:3004")

# HTTP client for proxying
client = httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True)


async def proxy_request(
    request: Request,
    service_url: str,
    path_rewrite: Optional[str] = None
):
    """
    Proxy request to a microservice
    """
    # Rewrite path if needed (remove /api/{service} prefix)
    target_path = request.url.path
    if path_rewrite:
        target_path = target_path.replace(path_rewrite, "", 1)
        if not target_path.startswith("/"):
            target_path = "/" + target_path
    
    target_url = f"{service_url}{target_path}"
    
    # Build query string
    if request.url.query:
        target_url += f"?{request.url.query}"
    
    logger.info(f"[{datetime.now().isoformat()}] Proxying {request.method} {request.url.path} to {target_url}")
    
    try:
        # Prepare headers (exclude host and connection)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("connection", None)
        
        # Get request body
        body = await request.body()
        
        # Make request to target service
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            cookies=request.cookies
        )
        
        logger.info(f"[{datetime.now().isoformat()}] Response from {request.url.path}: {response.status_code}")
        
        # Return response
        return StreamingResponse(
            iter([response.content]),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    
    except httpx.TimeoutException:
        logger.error(f"[{datetime.now().isoformat()}] Timeout for {request.url.path}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.ConnectError:
        logger.error(f"[{datetime.now().isoformat()}] Connection error for {target_url}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"[{datetime.now().isoformat()}] Proxy error for {request.url.path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal gateway error: {str(e)}")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "api-gateway"}


# API Info endpoint
@app.get("/")
async def api_info():
    """API Gateway information"""
    return {
        "service": "API Gateway",
        "status": "running",
        "version": "1.0.0",
        "language": "Python",
        "framework": "FastAPI",
        "endpoints": {
            "health": "/health",
            "api": {
                "users": "/api/users",
                "products": "/api/products",
                "orders": "/api/orders",
                "payments": "/api/payments"
            }
        },
        "documentation": {
            "note": "API Gateway is a proxy service. Access Swagger docs directly on each service:",
            "user_service": "http://localhost:3001/docs",
            "product_service": "http://localhost:3002/docs",
            "order_service": "http://localhost:3003/docs",
            "payment_service": "http://localhost:3004/docs"
        },
        "message": "API Gateway is running. Use /api/{service} to access microservices."
    }


# Route proxying - Users Service
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_users(request: Request, path: str):
    """Proxy requests to User Service"""
    return await proxy_request(request, USER_SERVICE, "/api/users")


# Route proxying - Products Service
@app.api_route("/api/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_products(request: Request, path: str):
    """Proxy requests to Product Service"""
    return await proxy_request(request, PRODUCT_SERVICE, "/api/products")


# Route proxying - Orders Service
@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_orders(request: Request, path: str):
    """Proxy requests to Order Service"""
    return await proxy_request(request, ORDER_SERVICE, "/api/orders")


# Route proxying - Payments Service
@app.api_route("/api/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_payments(request: Request, path: str):
    """Proxy requests to Payment Service"""
    return await proxy_request(request, PAYMENT_SERVICE, "/api/payments")


# 404 handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def not_found(request: Request, path: str):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Route {request.method} {request.url.path} not found",
            "availableEndpoints": [
                "/",
                "/health",
                "/api/users",
                "/api/products",
                "/api/orders",
                "/api/payments"
            ]
        }
    )


@app.on_event("startup")
async def startup_event():
    """Log service URLs on startup"""
    logger.info(f"API Gateway listening on port {PORT}")
    logger.info(f"Proxying to services:")
    logger.info(f"  - Users: {USER_SERVICE}")
    logger.info(f"  - Products: {PRODUCT_SERVICE}")
    logger.info(f"  - Orders: {ORDER_SERVICE}")
    logger.info(f"  - Payments: {PAYMENT_SERVICE}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP client on shutdown"""
    await client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

