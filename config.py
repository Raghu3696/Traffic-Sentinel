"""
Configuration settings for the Intelligent Rate Limiter
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Intelligent Rate Limiter API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Rate Limiting Settings
    BASE_LIMIT: int = int(os.getenv("BASE_LIMIT", "100"))
    WINDOW_SECONDS: int = int(os.getenv("WINDOW_SECONDS", "60"))
    
    # ML Model Settings
    ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "-0.5"))
    CONTAMINATION: float = float(os.getenv("CONTAMINATION", "0.1"))
    N_ESTIMATORS: int = int(os.getenv("N_ESTIMATORS", "100"))
    
    # Training Settings
    TRAINING_INTERVAL_MINUTES: int = int(os.getenv("TRAINING_INTERVAL_MINUTES", "5"))
    MIN_SAMPLES_FOR_TRAINING: int = int(os.getenv("MIN_SAMPLES_FOR_TRAINING", "50"))
    
    # Buffer Settings
    MAX_BUFFER_SIZE: int = int(os.getenv("MAX_BUFFER_SIZE", "1000"))
    DATA_RETENTION_HOURS: int = int(os.getenv("DATA_RETENTION_HOURS", "24"))
    
    # Endpoint-specific limits (can be customized)
    ENDPOINT_LIMITS = {
        "/api/heavy-operation": 20,
        "/api/data": 150,
        "/api/process": 100,
    }
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis URL with password if configured"""
        url = cls.REDIS_URL
        if cls.REDIS_PASSWORD:
            # Insert password into URL
            url = url.replace("redis://", f"redis://:{cls.REDIS_PASSWORD}@")
        return f"{url}/{cls.REDIS_DB}"


settings = Settings()
