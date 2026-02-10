# 🚀 Quick Start Guide

Get up and running with Intelligent Rate Limiter in 5 minutes!

## Prerequisites

- Python 3.11+
- Redis OR Docker & Docker Compose

## Option 1: Docker Compose (Easiest) ⭐

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd intelligent-rate-limiter

# 2. Start everything with one command
docker-compose up -d

# 3. View logs
docker-compose logs -f api

# 4. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

That's it! Your intelligent rate limiter is running.

## Option 2: Local Development

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd intelligent-rate-limiter

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Start Redis (in a separate terminal)
redis-server

# 4. Activate virtual environment
source venv/bin/activate

# 5. Start the application
python app.py
```

## Try It Out!

### 1. Test with cURL

```bash
# Make a normal request
curl http://localhost:8000/api/data

# Check headers for rate limit info
curl -I http://localhost:8000/api/data

# You'll see:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 45
```

### 2. Run the Interactive Demo

In a new terminal:

```bash
# Activate virtual environment (if local setup)
source venv/bin/activate

# Run the demo
python test_traffic.py
```

This will:
- ✅ Simulate normal traffic
- 🔴 Simulate anomalous traffic
- 📊 Show statistics
- 🤖 Display ML model info

### 3. Monitor in Real-Time

In another terminal:

```bash
# Activate virtual environment (if local setup)
source venv/bin/activate

# Start the monitor
python monitor.py
```

You'll see a live dashboard updating every 2 seconds!

### 4. Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## What Happens During Demo?

1. **Normal Traffic (20 requests)**
   - Regular intervals
   - ML learns this is normal behavior
   - Full rate limits apply

2. **Burst Traffic (50 rapid requests)**
   - Tests system under load
   - Some requests may be rate limited

3. **Anomalous Traffic (rapid fire)**
   - ML detects unusual pattern
   - Rate limits automatically reduced to 30%
   - Attack mitigated! 🛡️

## Check the Results

```bash
# View statistics
curl http://localhost:8000/admin/stats

# View current limits
curl http://localhost:8000/admin/limits

# View ML model info
curl http://localhost:8000/admin/model-info
```

## Common Commands

```bash
# Stop Docker services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View API logs
docker-compose logs -f api

# View Redis logs
docker-compose logs -f redis

# Rebuild after code changes
docker-compose up -d --build
```

## Verify Everything Works

Run this health check:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "redis": "connected",
  "timestamp": "2024-02-09T10:30:00"
}
```

## Next Steps

1. **Customize Configuration**
   - Edit `.env` file
   - Adjust rate limits
   - Configure ML parameters

2. **Explore Admin Endpoints**
   - `/admin/stats` - Traffic statistics
   - `/admin/limits` - Current limits
   - `/admin/model-info` - ML model status
   - `/admin/client/{client_id}` - Client info

3. **Integrate with Your API**
   - Copy rate limiting logic
   - Adapt to your endpoints
   - Customize limits per endpoint

4. **Deploy to Production**
   - Use Redis cluster
   - Set up monitoring
   - Configure HTTPS
   - Add authentication

## Troubleshooting

### "Connection refused" errors
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server
# OR
docker-compose up -d redis
```

### "Port already in use"
```bash
# Change port in .env or docker-compose.yml
API_PORT=8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt

# Or rebuild Docker
docker-compose up -d --build
```

## Learn More

- 📖 [Full Documentation](README.md)
- 🏗️ [Project Structure](STRUCTURE.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

## Support

- 🐛 [Report a bug](https://github.com/yourusername/intelligent-rate-limiter/issues)
- 💡 [Request a feature](https://github.com/yourusername/intelligent-rate-limiter/issues)
- ❓ [Ask a question](https://github.com/yourusername/intelligent-rate-limiter/discussions)

---

**Happy rate limiting! 🚦**
