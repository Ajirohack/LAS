# LAS Infrastructure Deployment Guide

## P3 Infrastructure Stack

Complete enterprise-grade infrastructure for production deployment.

---

## Quick Start

### 1. Start Kong API Gateway

```bash
cd infrastructure/kong
docker-compose up -d

# Wait for services to start
sleep 30

# Configure Kong
chmod +x configure-kong.sh
./configure-kong.sh
```

**Access:**

- API Gateway: <http://localhost:8000/api>
- Kong Admin UI: <http://localhost:1337>
- Kong Admin API: <http://localhost:8001>

### 2. Start ELK Stack

```bash
cd infrastructure/elk
docker-compose up -d
```

**Access:**

- Kibana: <http://localhost:5601>
- Elasticsearch: <http://localhost:9200>

### 3. Start Monitoring Stack

```bash
cd infrastructure/prometheus
docker-compose up -d
```

**Access:**

- Grafana: <http://localhost:3001> (admin/admin)
- Prometheus: <http://localhost:9090>
- AlertManager: <http://localhost:9093>

---

## Kong API Gateway

### Features

- ✅ JWT Authentication
- ✅ Rate Limiting (100 req/min)
- ✅ CORS Support
- ✅ Request/Response Transformation
- ✅ Load Balancing
- ✅ Admin UI (Konga)

### Configuration

Kong is pre-configured with:

1. **Service:** `las-api` → `http://las-backend:8080`
2. **Route:** `/api` → forwards to LAS backend
3. **Plugins:**
   - JWT authentication
   - Rate limiting
   - CORS
   - Response transformer

### Making Requests Through Kong

```bash
# Instead of:
curl http://localhost:8080/api/v1/health

# Use:
curl http://localhost:8000/api/v1/health
```

### Managing Kong

**Add New Service:**

```bash
curl -i -X POST http://localhost:8001/services/ \
  --data 'name=new-service' \
  --data 'url=http://service-url:port'
```

**Add Plugin:**

```bash
curl -i -X POST http://localhost:8001/services/las-api/plugins \
  --data 'name=plugin-name' \
  --data 'config.param=value'
```

---

## ELK Stack (Logging)

### Components

1. **Elasticsearch** - Log storage and indexing
2. **Logstash** - Log processing and transformation
3. **Kibana** - Visualization and analysis
4. **Filebeat** - Log shipping from Docker containers

### Log Viewing

1. Open Kibana: <http://localhost:5601>
2. Go to **Discover**
3. Create index pattern: `las-logs-*`
4. View real-time logs from all services

### Custom Log Shipping

Add to your application:

```python
import logging
import json

logger = logging.getLogger(__name__)

# JSON formatted logs (auto-parsed by Logstash)
log_data = {
    "level": "INFO",
    "message": "User logged in",
    "user_id": 123,
    "timestamp": datetime.utcnow().isoformat()
}
logger.info(json.dumps(log_data))
```

### Kibana Dashboards

Pre-configured views:

- Application logs by service
- Error rate trends
- Request volumes
- Performance metrics

---

## Prometheus & Grafana (Monitoring)

### What's Monitored

1. **LAS API** - Request rates, response times, errors
2. **System** - CPU, memory, disk (via node-exporter)
3. **Redis** - Cache hit rate, memory usage
4. **PostgreSQL** - Connections, query performance
5. **Kong** - API Gateway metrics

### Alerting Rules

9 pre-configured alerts:

1. High Response Time (>2s for 5min)
2. High Error Rate (>5%)
3. Low Cache Hit Rate (<50%)
4. High Memory Usage (<10% available)
5. High CPU Usage (>80%)
6. Service Down
7. Database Connection Issues
8. High Request Rate (>1000 req/s)

### Grafana Dashboards

**Access:** <http://localhost:3001> (admin/admin)

**Create Custom Dashboard:**

1. Click "+" → Dashboard
2. Add Panel → Select Prometheus datasource
3. Query: `rate(las_requests_total[5m])`
4. Visualize!

**Recommended Queries:**

```promql
# Request rate
rate(las_requests_total[5m])

# P95 response time
histogram_quantile(0.95, rate(las_request_duration_seconds_bucket[5m]))

# Error rate
rate(las_errors_total[5m])

# Cache hit rate
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)
```

---

## Complete Stack Deployment

```bash
# 1. Start all infrastructure
cd infrastructure

# Kong
cd kong && docker-compose up -d && cd ..

# ELK
cd elk && docker-compose up -d && cd ..

# Prometheus
cd prometheus && docker-compose up -d && cd ..

# 2. Configure Kong
cd kong && ./configure-kong.sh && cd ..

# 3. Verify all services
docker ps
```

---

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| Kong Gateway | 8000 | <http://localhost:8000> |
| Kong Admin | 8001 | <http://localhost:8001> |
| Konga UI | 1337 | <http://localhost:1337> |
| Elasticsearch | 9200 | <http://localhost:9200> |
| Kibana | 5601 | <http://localhost:5601> |
| Logstash | 5044 | - |
| Prometheus | 9090 | <http://localhost:9090> |
| Grafana | 3001 | <http://localhost:3001> |
| AlertManager | 9093 | <http://localhost:9093> |
| LAS Backend | 8080 | <http://localhost:8080> |

---

## Troubleshooting

### Kong Won't Start

```bash
# Check logs
docker logs kong-gateway

# Reset database
docker-compose down -v
docker-compose up -d
```

### ELK Memory Issues

```bash
# Increase Docker memory to 4GB+
# Edit docker-compose.yml ES_JAVA_OPTS if needed
```

### Prometheus Not Scraping

```bash
# Verify targets
curl http://localhost:9090/api/v1/targets

# Check network connectivity
docker network inspect infrastructure_monitoring
```

---

## Production Recommendations

### Kong

- Enable SSL with Let's Encrypt
- Configure database backups
- Set up multi-node cluster
- Enable request caching

### ELK

- Use dedicated Elasticsearch cluster
- Configure index lifecycle management
- Set up backup snapshots
- Enable authentication

### Monitoring

- Configure persistent storage
- Set up email/Slack alerts
- Create custom dashboards
- Enable retention policies

---

## Maintenance

### Cleanup Old Logs

```bash
# Delete old Elasticsearch indices
curl -X DELETE "localhost:9200/las-logs-2024.01.*"
```

### Backup

```bash
# Export Grafana dashboards
curl http://admin:admin@localhost:3001/api/dashboards/db/dashboard-name

# Backup Prometheus data
docker cp las-prometheus:/prometheus ./prometheus-backup
```

---

## Next Steps

1. ✅ Infrastructure deployed
2. ⚙️ Configure custom dashboards
3. 📧 Set up alert notifications
4. 🔒 Enable SSL/TLS
5. 📊 Monitor and optimize

**Infrastructure is ready for production!** 🚀
