from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import time
import asyncio
from datetime import datetime
from typing import Optional
import uvicorn

from rate_limiter import IntelligentRateLimiter
from models import RateLimitInfo, TrafficStats

app = FastAPI(
    title="Intelligent Rate Limiter API",
    description="ML-powered adaptive rate limiting system",
    version="1.0.0"
)

# Initialize the intelligent rate limiter
rate_limiter = IntelligentRateLimiter()

@app.on_event("startup")
async def startup_event():
    """Initialize rate limiter on startup"""
    await rate_limiter.initialize()
    # Start background tasks
    asyncio.create_task(rate_limiter.train_model_periodically())
    asyncio.create_task(rate_limiter.cleanup_old_data())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await rate_limiter.close()

async def check_rate_limit(request: Request):
    """Dependency to check rate limits"""
    client_id = request.client.host
    endpoint = request.url.path
    
    allowed, info = await rate_limiter.check_request(client_id, endpoint)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": info["current_limit"],
                "remaining": info["remaining"],
                "reset_in": info["reset_in"],
                "is_anomalous": info["is_anomalous"]
            },
            headers={
                "X-RateLimit-Limit": str(info["current_limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_in"]),
                "Retry-After": str(info["reset_in"])
            }
        )
    
    # Add rate limit headers to response
    request.state.rate_limit_info = info

@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit headers to all responses"""
    response = await call_next(request)
    
    if hasattr(request.state, "rate_limit_info"):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["current_limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset_in"])
    
    return response

# ==================== API Endpoints ====================

@app.get("/", dependencies=[Depends(check_rate_limit)])
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Rate Limiter API",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/data", dependencies=[Depends(check_rate_limit)])
async def get_data():
    """Sample protected endpoint"""
    return {
        "data": "This endpoint is protected by intelligent rate limiting",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/process", dependencies=[Depends(check_rate_limit)])
async def process_data(data: dict):
    """Sample POST endpoint"""
    return {
        "message": "Data processed successfully",
        "received": data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/heavy-operation", dependencies=[Depends(check_rate_limit)])
async def heavy_operation():
    """Simulated heavy operation endpoint"""
    await asyncio.sleep(0.1)  # Simulate processing
    return {
        "message": "Heavy operation completed",
        "timestamp": datetime.now().isoformat()
    }

# ==================== Admin Endpoints ====================

@app.get("/admin/stats", response_model=TrafficStats)
async def get_traffic_stats():
    """Get current traffic statistics"""
    stats = await rate_limiter.get_traffic_stats()
    return stats

@app.get("/admin/limits")
async def get_current_limits():
    """Get current rate limits for all endpoints"""
    limits = await rate_limiter.get_current_limits()
    return limits

@app.get("/admin/client/{client_id}")
async def get_client_info(client_id: str):
    """Get information about a specific client"""
    info = await rate_limiter.get_client_info(client_id)
    return info

@app.post("/admin/reset/{client_id}")
async def reset_client_limits(client_id: str):
    """Reset rate limits for a specific client"""
    await rate_limiter.reset_client(client_id)
    return {"message": f"Limits reset for client {client_id}"}

@app.post("/admin/train")
async def trigger_training():
    """Manually trigger ML model training"""
    await rate_limiter.train_model()
    return {"message": "Model training initiated"}

@app.get("/admin/model-info")
async def get_model_info():
    """Get ML model information"""
    info = await rate_limiter.get_model_info()
    return info

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = await rate_limiter.check_redis_connection()
    return {
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
