# Performance Optimization - Setup Guide

## Quick Start

### 1. Install Redis (Optional but Recommended)

**macOS:**

```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker:**

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### 2. Install PostgreSQL (For Production)

**macOS:**

```bash
brew install postgresql
brew services start postgresql
createdb las_db
```

**Linux:**

```bash
sudo apt-get install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb las_db
```

### 3. Update Environment Variables

Add to your `.env`:

```bash
# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# PostgreSQL (for production)
DATABASE_URL=postgresql://user:password@localhost/las_db

# Or keep SQLite for development
DATABASE_URL=sqlite:///./las.db
```

### 4. Install Python Dependencies

```bash
pip install httpx redis psycopg2-binary
```

## Using the New Services

### Connection Pooling

```python
from services.connection_pool import get_connection_pool

# Get pooled client
pool = get_connection_pool()
client = pool.get_sync_client("https://api.example.com")

# Make requests (connection is reused)
response = client.get("/endpoint")
```

### Redis Caching

```python
from services.redis_cache import cached, get_redis_cache

# Use decorator for automatic caching
@cached(ttl=1800, prefix="user")
def get_user(user_id: int):
    # This will be cached for 30 minutes
    return db.query(User).get(user_id)

# Direct cache usage
cache = get_redis_cache()
cache.set("key", {"data": "value"}, ttl=3600)
value = cache.get("key")

# Get cache stats
stats = cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']}%")
```

### Database Indexes

Indexes are automatically created when you run:

```bash
python -c "from database.models import init_db; init_db()"
```

## Performance Improvements

**Expected Results:**

- ✅ Response time: -30% (connection reuse)
- ✅ Cache hit rate: 70%+ (Redis)
- ✅ Database queries: -50% time (indexes)
- ✅ Concurrent requests: 100+ req/s

## Monitoring

Check Redis cache performance:

```python
from services.redis_cache import get_redis_cache

cache = get_redis_cache()
stats = cache.get_stats()
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
print(f"Hit Rate: {stats['hit_rate']}%")
```

## Migration Path

**Phase 1: Development (Current)**

- SQLite database
- Redis optional
- Connection pooling active

**Phase 2: Staging**

- PostgreSQL database
- Redis enabled
- Full optimization stack

**Phase 3: Production**

- PostgreSQL with replicas
- Redis cluster
- Load balancing
