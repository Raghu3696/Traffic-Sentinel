# 🚦 Intelligent Rate Limiter

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![ML](https://img.shields.io/badge/ML-Isolation%20Forest-orange.svg)

An ML-powered adaptive rate limiting system that learns from traffic patterns and dynamically adjusts limits based on anomaly detection.

## 🌟 Features

- **Machine Learning Based**: Uses Isolation Forest for anomaly detection
- **Dynamic Rate Limiting**: Automatically adjusts limits based on traffic patterns
- **Real-time Adaptation**: Learns from ongoing traffic to detect abnormal behavior
- **Redis-Backed**: Fast, distributed rate limiting with Redis
- **FastAPI**: High-performance async API framework
- **Admin Dashboard**: Monitor traffic, view statistics, and manage limits
- **Docker Support**: Easy deployment with Docker Compose

## 🎯 Why This Project Stands Out

Traditional rate limiters are **static** - they apply the same limits regardless of traffic patterns. This intelligent rate limiter:

1. **Learns Normal Behavior**: Builds a profile of normal traffic patterns
2. **Detects Anomalies**: Identifies suspicious traffic (DDoS, scraping, abuse)
3. **Adapts Dynamically**: Reduces limits for anomalous traffic, maintains higher limits for normal users
4. **Continuous Learning**: Retrains periodically to adapt to changing patterns

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │   Rate Limiter Middleware     │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Intelligent Rate Limiter     │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Feature Extraction     │  │  │
│  │  └────────┬────────────────┘  │  │
│  │           │                   │  │
│  │  ┌────────▼────────────────┐  │  │
│  │  │  Isolation Forest       │  │  │
│  │  │  Anomaly Detection      │  │  │
│  │  └────────┬────────────────┘  │  │
│  │           │                   │  │
│  │  ┌────────▼────────────────┐  │  │
│  │  │  Dynamic Limit Engine   │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────┬───────────────────┘  │
└──────────────┼──────────────────────┘
               │
               ▼
         ┌──────────┐
         │  Redis   │
         └──────────┘
```

## 📊 How It Works

### 1. Feature Extraction
For each request, the system extracts features:
- Hour of day
- Day of week
- Request count in window
- Endpoint identifier
- Request rate statistics (mean/std of intervals)

### 2. Anomaly Detection
Uses **Isolation Forest** algorithm:
- Trained on historical traffic patterns
- Scores each request for anomalousness
- Flags suspicious patterns (rapid requests, unusual timing, etc.)

### 3. Dynamic Rate Limiting
- **Normal Traffic**: Full rate limit (default: 100 req/min)
- **Anomalous Traffic**: Reduced limit (30% of base limit)
- **Per-Endpoint**: Different limits for different endpoints

### 4. Continuous Learning
- Retrains model every 5 minutes
- Adapts to evolving traffic patterns
- Persists model in Redis for reliability

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis (or use Docker Compose)
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd intelligent-rate-limiter

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# The API will be available at http://localhost:8000
```

### Option 2: Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (in another terminal)
redis-server

# Run the application
python app.py
```

## 📖 Usage

### Basic API Request

```bash
# Make a request
curl http://localhost:8000/api/data

# Response headers include rate limit info:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 45
```

### Running the Demo

```bash
# Run the interactive demo
python test_traffic.py

# Or run continuous traffic simulation
python test_traffic.py continuous
```

The demo simulates:
- ✅ Normal traffic patterns
- 🔴 Anomalous traffic (rapid requests)
- 🟡 Burst traffic
- 📊 Statistics and ML model info

### Admin Endpoints

```bash
# Get traffic statistics
curl http://localhost:8000/admin/stats

# Get current rate limits
curl http://localhost:8000/admin/limits

# Get ML model information
curl http://localhost:8000/admin/model-info

# Get client information
curl http://localhost:8000/admin/client/127.0.0.1

# Reset client limits
curl -X POST http://localhost:8000/admin/reset/127.0.0.1

# Manually trigger model training
curl -X POST http://localhost:8000/admin/train

# Health check
curl http://localhost:8000/health
```

## 📡 API Endpoints

### Public Endpoints (Rate Limited)
- `GET /` - Root endpoint
- `GET /api/data` - Sample data endpoint
- `POST /api/process` - Sample processing endpoint
- `GET /api/heavy-operation` - Heavy operation endpoint

### Admin Endpoints (Monitoring)
- `GET /admin/stats` - Traffic statistics
- `GET /admin/limits` - Current rate limits
- `GET /admin/client/{client_id}` - Client information
- `POST /admin/reset/{client_id}` - Reset client limits
- `POST /admin/train` - Trigger ML training
- `GET /admin/model-info` - ML model details
- `GET /health` - Health check

## 🎨 Response Examples

### Normal Request (200 OK)
```json
{
  "data": "This endpoint is protected by intelligent rate limiting",
  "timestamp": "2024-02-09T10:30:00"
}
```

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 45
```

### Rate Limited (429 Too Many Requests)
```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 30,
    "remaining": 0,
    "reset_in": 23,
    "is_anomalous": true
  }
}
```

Headers:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 23
Retry-After: 23
```

### Traffic Statistics
```json
{
  "total_requests": 1523,
  "unique_clients": 15,
  "endpoints": {
    "/api/data": 892,
    "/api/process": 421,
    "/": 210
  },
  "model_trained": true,
  "buffer_size": {
    "127.0.0.1": 245,
    "192.168.1.100": 89
  }
}
```

## ⚙️ Configuration

Edit `rate_limiter.py` to customize:

```python
IntelligentRateLimiter(
    redis_url="redis://localhost:6379",
    base_limit=100,              # Base requests per window
    window_seconds=60,           # Time window in seconds
    anomaly_threshold=-0.5,      # Anomaly detection sensitivity
    training_interval_minutes=5  # Model retraining interval
)
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_limit` | 100 | Base number of requests per window |
| `window_seconds` | 60 | Time window for rate limiting (seconds) |
| `anomaly_threshold` | -0.5 | Threshold for anomaly detection (lower = stricter) |
| `training_interval_minutes` | 5 | How often to retrain the ML model |

## 🧪 Testing

### Unit Tests (Future)
```bash
pytest tests/
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f load_test.py --host=http://localhost:8000
```

## 📈 Monitoring

### Key Metrics to Monitor
- Request count per client
- Anomaly detection rate
- Average response time
- Rate limit hit rate
- Model training frequency

### Logging
The application logs:
- ✅ Normal requests
- 🚨 Anomalous traffic detection
- 🎓 Model training events
- 💾 Model persistence
- 🧹 Data cleanup operations

## 🔒 Security Considerations

1. **DDoS Protection**: Reduces limits for suspicious traffic
2. **Scraper Detection**: Identifies automated access patterns
3. **Brute Force Prevention**: Detects rapid authentication attempts
4. **Adaptive Response**: Automatically adjusts to new attack patterns

## 🚀 Deployment

### Production Recommendations

1. **Use Redis Cluster** for high availability
2. **Enable Redis Persistence** (AOF or RDB)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure logging** (centralized logging solution)
5. **Add authentication** for admin endpoints
6. **Use HTTPS** in production
7. **Set rate limits** per your needs

### Environment Variables

```bash
REDIS_URL=redis://localhost:6379
BASE_LIMIT=100
WINDOW_SECONDS=60
ANOMALY_THRESHOLD=-0.5
TRAINING_INTERVAL=5
```

## 🔧 Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server

# Or with Docker
docker-compose up -d redis
```

### Model Not Training
- Ensure at least 50 requests have been made
- Check logs for training errors
- Verify Redis connection
- Manually trigger training: `POST /admin/train`

### Rate Limits Not Working
- Check Redis connectivity
- Verify client IP is being captured correctly
- Check rate limit configuration
- Review application logs

## 📚 Technologies Used

- **FastAPI**: Modern, fast web framework
- **Redis**: In-memory data store for rate limiting
- **scikit-learn**: ML library (Isolation Forest)
- **NumPy**: Numerical computations
- **Pydantic**: Data validation
- **aiohttp**: Async HTTP client (for testing)
- **Docker**: Containerization
- **Uvicorn**: ASGI server

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - feel free to use this project for learning or production!

## 🌟 Future Enhancements

- [ ] Multiple ML models (Random Forest, LSTM for time series)
- [ ] Per-user rate limits
- [ ] Geographic-based rate limiting
- [ ] WebSocket support
- [ ] Grafana dashboard
- [ ] API key management
- [ ] User reputation system
- [ ] Advanced analytics
- [ ] Multi-tenant support

## 📧 Contact

Questions or suggestions? Open an issue!

---

**Made with ❤️ using FastAPI, Redis, and Machine Learning**

⭐ Star this repo if you find it useful!
