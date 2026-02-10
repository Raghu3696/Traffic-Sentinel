import redis.asyncio as redis
from datetime import datetime, timedelta
import json
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import asyncio
from typing import Dict, Tuple, List, Optional
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentRateLimiter:
    """
    ML-powered rate limiter that adapts to traffic patterns
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        base_limit: int = 100,
        window_seconds: int = 60,
        anomaly_threshold: float = -0.5,
        training_interval_minutes: int = 5
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Rate limiting configuration
        self.base_limit = base_limit
        self.window_seconds = window_seconds
        self.anomaly_threshold = anomaly_threshold
        self.training_interval = training_interval_minutes * 60
        
        # ML model
        self.model: Optional[IsolationForest] = None
        self.feature_scaler = {"mean": None, "std": None}
        
        # Traffic pattern tracking
        self.traffic_buffer = defaultdict(list)
        self.max_buffer_size = 1000
        
        # Dynamic limits per endpoint
        self.endpoint_limits = {}
        
    async def initialize(self):
        """Initialize Redis connection and load model if exists"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis")
            
            # Try to load existing model
            await self._load_model()
            
            # Initialize model if not loaded
            if self.model is None:
                self._initialize_model()
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _initialize_model(self):
        """Initialize the Isolation Forest model"""
        self.model = IsolationForest(
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42,
            n_estimators=100
        )
        logger.info("🤖 Initialized ML model")
    
    async def _load_model(self):
        """Load model from Redis"""
        try:
            model_data = await self.redis_client.get("ml_model")
            if model_data:
                model_dict = pickle.loads(model_data.encode('latin1'))
                self.model = model_dict['model']
                self.feature_scaler = model_dict['scaler']
                logger.info("📥 Loaded existing ML model from Redis")
        except Exception as e:
            logger.warning(f"⚠️ Could not load model: {e}")
    
    async def _save_model(self):
        """Save model to Redis"""
        try:
            model_dict = {
                'model': self.model,
                'scaler': self.feature_scaler
            }
            model_data = pickle.dumps(model_dict).decode('latin1')
            await self.redis_client.set("ml_model", model_data)
            logger.info("💾 Saved ML model to Redis")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    def _extract_features(self, client_id: str, endpoint: str, timestamp: float) -> np.ndarray:
        """Extract features for anomaly detection"""
        current_time = datetime.fromtimestamp(timestamp)
        
        features = [
            current_time.hour,  # Hour of day
            current_time.weekday(),  # Day of week
            len(self.traffic_buffer.get(client_id, [])),  # Request count
            hash(endpoint) % 100,  # Endpoint hash (simple encoding)
        ]
        
        # Add request rate features
        recent_requests = self.traffic_buffer.get(client_id, [])
        if len(recent_requests) > 1:
            time_diffs = np.diff([r['timestamp'] for r in recent_requests[-10:]])
            features.append(np.mean(time_diffs) if len(time_diffs) > 0 else 0)
            features.append(np.std(time_diffs) if len(time_diffs) > 0 else 0)
        else:
            features.extend([0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features using stored scaler"""
        if self.feature_scaler['mean'] is None:
            return features
        
        return (features - self.feature_scaler['mean']) / (self.feature_scaler['std'] + 1e-8)
    
    async def check_request(self, client_id: str, endpoint: str) -> Tuple[bool, Dict]:
        """
        Check if request is allowed and detect anomalies
        Returns: (allowed, info_dict)
        """
        current_time = time.time()
        
        # Track request
        await self._track_request(client_id, endpoint, current_time)
        
        # Get current window key
        window_key = f"rate_limit:{client_id}:{endpoint}:{int(current_time // self.window_seconds)}"
        
        # Increment counter
        count = await self.redis_client.incr(window_key)
        if count == 1:
            await self.redis_client.expire(window_key, self.window_seconds * 2)
        
        # Detect anomaly
        is_anomalous = await self._detect_anomaly(client_id, endpoint, current_time)
        
        # Get dynamic limit
        current_limit = await self._get_dynamic_limit(endpoint, is_anomalous)
        
        # Check if allowed
        allowed = count <= current_limit
        remaining = max(0, current_limit - count)
        
        info = {
            "current_limit": current_limit,
            "remaining": remaining,
            "reset_in": self.window_seconds - (int(current_time) % self.window_seconds),
            "is_anomalous": is_anomalous,
            "request_count": count
        }
        
        # Log if anomalous
        if is_anomalous:
            logger.warning(f"🚨 Anomalous traffic detected from {client_id} on {endpoint}")
        
        return allowed, info
    
    async def _track_request(self, client_id: str, endpoint: str, timestamp: float):
        """Track request for ML training"""
        request_data = {
            "endpoint": endpoint,
            "timestamp": timestamp,
            "hour": datetime.fromtimestamp(timestamp).hour,
            "weekday": datetime.fromtimestamp(timestamp).weekday()
        }
        
        self.traffic_buffer[client_id].append(request_data)
        
        # Limit buffer size
        if len(self.traffic_buffer[client_id]) > self.max_buffer_size:
            self.traffic_buffer[client_id] = self.traffic_buffer[client_id][-self.max_buffer_size:]
        
        # Also store in Redis for persistence
        await self.redis_client.lpush(
            f"traffic:{client_id}",
            json.dumps(request_data)
        )
        await self.redis_client.ltrim(f"traffic:{client_id}", 0, self.max_buffer_size - 1)
        await self.redis_client.expire(f"traffic:{client_id}", 86400)  # 24 hours
    
    async def _detect_anomaly(self, client_id: str, endpoint: str, timestamp: float) -> bool:
        """Detect if current request is anomalous"""
        if self.model is None or not hasattr(self.model, 'estimators_'):
            return False
        
        try:
            features = self._extract_features(client_id, endpoint, timestamp)
            features_normalized = self._normalize_features(features)
            
            score = self.model.score_samples(features_normalized)[0]
            return score < self.anomaly_threshold
            
        except Exception as e:
            logger.error(f"❌ Error detecting anomaly: {e}")
            return False
    
    async def _get_dynamic_limit(self, endpoint: str, is_anomalous: bool) -> int:
        """Get dynamic rate limit based on endpoint and anomaly status"""
        # Base limit for endpoint
        base = self.endpoint_limits.get(endpoint, self.base_limit)
        
        # Reduce limit if anomalous traffic detected
        if is_anomalous:
            return max(10, int(base * 0.3))  # Reduce to 30% of base
        
        return base
    
    async def train_model(self):
        """Train the ML model on collected traffic data"""
        logger.info("🎓 Starting model training...")
        
        try:
            # Collect training data
            all_features = []
            
            for client_id, requests in self.traffic_buffer.items():
                for req in requests:
                    features = self._extract_features(
                        client_id,
                        req['endpoint'],
                        req['timestamp']
                    )
                    all_features.append(features[0])
            
            if len(all_features) < 50:
                logger.warning("⚠️ Not enough data for training (need at least 50 samples)")
                return
            
            X = np.array(all_features)
            
            # Calculate scaler
            self.feature_scaler = {
                'mean': np.mean(X, axis=0),
                'std': np.std(X, axis=0)
            }
            
            # Normalize
            X_normalized = self._normalize_features(X)
            
            # Train model
            self.model.fit(X_normalized)
            
            # Save model
            await self._save_model()
            
            logger.info(f"✅ Model trained on {len(all_features)} samples")
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
    
    async def train_model_periodically(self):
        """Background task to train model periodically"""
        while True:
            try:
                await asyncio.sleep(self.training_interval)
                await self.train_model()
            except Exception as e:
                logger.error(f"❌ Periodic training error: {e}")
    
    async def cleanup_old_data(self):
        """Background task to cleanup old data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Cleanup old traffic buffers
                current_time = time.time()
                cutoff = current_time - 86400  # 24 hours
                
                for client_id in list(self.traffic_buffer.keys()):
                    self.traffic_buffer[client_id] = [
                        r for r in self.traffic_buffer[client_id]
                        if r['timestamp'] > cutoff
                    ]
                    
                    if not self.traffic_buffer[client_id]:
                        del self.traffic_buffer[client_id]
                
                logger.info("🧹 Cleaned up old traffic data")
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
    
    async def get_traffic_stats(self) -> Dict:
        """Get current traffic statistics"""
        total_requests = sum(len(reqs) for reqs in self.traffic_buffer.values())
        unique_clients = len(self.traffic_buffer)
        
        # Get endpoint distribution
        endpoint_counts = defaultdict(int)
        for requests in self.traffic_buffer.values():
            for req in requests:
                endpoint_counts[req['endpoint']] += 1
        
        return {
            "total_requests": total_requests,
            "unique_clients": unique_clients,
            "endpoints": dict(endpoint_counts),
            "model_trained": self.model is not None and hasattr(self.model, 'estimators_'),
            "buffer_size": {client: len(reqs) for client, reqs in self.traffic_buffer.items()}
        }
    
    async def get_current_limits(self) -> Dict:
        """Get current rate limits for all endpoints"""
        return {
            "base_limit": self.base_limit,
            "window_seconds": self.window_seconds,
            "endpoint_limits": self.endpoint_limits or {"default": self.base_limit}
        }
    
    async def get_client_info(self, client_id: str) -> Dict:
        """Get information about a specific client"""
        requests = self.traffic_buffer.get(client_id, [])
        
        if not requests:
            return {"error": "Client not found"}
        
        return {
            "client_id": client_id,
            "total_requests": len(requests),
            "first_seen": min(r['timestamp'] for r in requests),
            "last_seen": max(r['timestamp'] for r in requests),
            "endpoints_accessed": list(set(r['endpoint'] for r in requests))
        }
    
    async def reset_client(self, client_id: str):
        """Reset rate limits for a client"""
        # Clear from buffer
        if client_id in self.traffic_buffer:
            del self.traffic_buffer[client_id]
        
        # Clear from Redis
        pattern = f"rate_limit:{client_id}:*"
        cursor = 0
        while True:
            cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                await self.redis_client.delete(*keys)
            if cursor == 0:
                break
    
    async def get_model_info(self) -> Dict:
        """Get ML model information"""
        if self.model is None:
            return {"status": "not_initialized"}
        
        is_trained = hasattr(self.model, 'estimators_')
        
        return {
            "status": "trained" if is_trained else "initialized",
            "contamination": self.model.contamination,
            "n_estimators": self.model.n_estimators,
            "anomaly_threshold": self.anomaly_threshold,
            "features": ["hour", "weekday", "request_count", "endpoint_hash", "mean_interval", "std_interval"]
        }
    
    async def check_redis_connection(self) -> bool:
        """Check if Redis is connected"""
        try:
            await self.redis_client.ping()
            return True
        except:
            return False


import time
