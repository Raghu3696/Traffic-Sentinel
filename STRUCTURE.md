# Project Structure

```
intelligent-rate-limiter/
│
├── app.py                      # Main FastAPI application
├── rate_limiter.py            # Core rate limiting logic with ML
├── models.py                  # Pydantic models for API
├── config.py                  # Configuration settings
│
├── test_traffic.py            # Traffic simulation & testing
├── monitor.py                 # Real-time monitoring dashboard
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── setup.sh                   # Setup script
│
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
│
├── README.md                 # Main documentation
├── CONTRIBUTING.md           # Contribution guidelines
└── LICENSE                   # MIT License
```

## File Descriptions

### Core Application Files

#### `app.py`
Main FastAPI application with:
- API endpoints (public + admin)
- Rate limiting middleware
- Health checks
- Request/response handling

#### `rate_limiter.py`
The heart of the system:
- `IntelligentRateLimiter` class
- ML model (Isolation Forest)
- Feature extraction
- Anomaly detection
- Dynamic limit adjustment
- Redis integration
- Background training

#### `models.py`
Pydantic models for:
- API request/response validation
- Data serialization
- Type safety

#### `config.py`
Centralized configuration:
- Environment variables
- Default settings
- Endpoint-specific limits

### Testing & Monitoring

#### `test_traffic.py`
Interactive testing:
- Normal traffic simulation
- Anomalous traffic patterns
- Burst testing
- Statistics display

#### `monitor.py`
Real-time dashboard:
- Live traffic stats
- ML model status
- Endpoint distribution
- Visual monitoring

### Deployment

#### `Dockerfile`
Container definition:
- Python 3.11 base
- Dependencies installation
- Application setup

#### `docker-compose.yml`
Multi-container setup:
- API service
- Redis service
- Networking
- Volumes

#### `setup.sh`
Development setup:
- Environment creation
- Dependency installation
- Configuration setup

## Data Flow

```
1. Request Arrives
   ↓
2. FastAPI Middleware
   ↓
3. Rate Limiter Check
   ↓
   ├── Extract Features (hour, day, count, endpoint, rate)
   │   ↓
   ├── Detect Anomaly (ML Model - Isolation Forest)
   │   ↓
   └── Get Dynamic Limit (adjust based on anomaly)
       ↓
4. Check Redis Counter
   ↓
5. Decision: Allow or Block
   ↓
   ├── If Allowed → Process Request
   │   └── Return Response + Headers
   │
   └── If Blocked → Return 429
       └── Return Error + Retry Info
```

## ML Pipeline

```
Traffic Data Collection
   ↓
Feature Extraction
   ├── Temporal: hour, weekday
   ├── Volume: request count
   ├── Pattern: request intervals
   └── Context: endpoint
   ↓
Feature Normalization
   ↓
Isolation Forest Training
   ↓
Model Persistence (Redis)
   ↓
Anomaly Detection
   └── Score < Threshold → Anomalous
```

## Redis Data Structure

```
Keys Used:

1. rate_limit:{client_id}:{endpoint}:{window}
   - Counter for requests in current window
   - TTL: 2x window_seconds

2. traffic:{client_id}
   - List of recent requests (JSON)
   - TTL: 24 hours
   - Max size: 1000 entries

3. ml_model
   - Pickled ML model + scaler
   - Persistent storage
```

## Configuration Flow

```
Environment Variables (.env)
   ↓
config.py (Settings class)
   ↓
rate_limiter.py (IntelligentRateLimiter)
   ↓
app.py (FastAPI application)
```

## Testing Strategy

```
1. Unit Tests (Future)
   - Test individual functions
   - Mock Redis/ML components
   - Validate logic

2. Integration Tests
   - test_traffic.py
   - End-to-end scenarios
   - Traffic patterns

3. Load Tests (Future)
   - Locust/Artillery
   - Performance benchmarks
   - Scalability tests

4. Monitoring
   - monitor.py
   - Real-time validation
   - Visual feedback
```
