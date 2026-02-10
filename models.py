from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class RateLimitInfo(BaseModel):
    """Rate limit information response"""
    current_limit: int = Field(..., description="Current rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_in: int = Field(..., description="Seconds until reset")
    is_anomalous: bool = Field(..., description="Whether traffic is anomalous")
    request_count: int = Field(..., description="Current request count")

class TrafficStats(BaseModel):
    """Traffic statistics"""
    total_requests: int = Field(..., description="Total requests tracked")
    unique_clients: int = Field(..., description="Number of unique clients")
    endpoints: Dict[str, int] = Field(..., description="Endpoint access counts")
    model_trained: bool = Field(..., description="Whether ML model is trained")
    buffer_size: Dict[str, int] = Field(..., description="Buffer size per client")

class ClientInfo(BaseModel):
    """Information about a specific client"""
    client_id: str
    total_requests: int
    first_seen: float
    last_seen: float
    endpoints_accessed: List[str]

class ModelInfo(BaseModel):
    """ML model information"""
    status: str
    contamination: Optional[float] = None
    n_estimators: Optional[int] = None
    anomaly_threshold: Optional[float] = None
    features: Optional[List[str]] = None
