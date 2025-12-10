#!/bin/bash
# Kong Configuration Script

echo "🔧 Configuring Kong API Gateway..."

# Wait for Kong to be ready
echo "Waiting for Kong..."
until curl -s http://localhost:8001/ > /dev/null; do
    sleep 2
done

echo "✓ Kong is ready"

# Add LAS API Service
echo "Adding LAS API service..."
curl -i -X POST http://localhost:8001/services/ \
  --data 'name=las-api' \
  --data 'url=http://las-backend:8080'

# Add routes
echo "Adding routes..."
curl -i -X POST http://localhost:8001/services/las-api/routes \
  --data 'paths[]=/api' \
  --data 'name=las-api-route'

# Add JWT Plugin
echo "Adding JWT authentication plugin..."
curl -i -X POST http://localhost:8001/services/las-api/plugins \
  --data 'name=jwt'

# Add Rate Limiting Plugin
echo "Adding rate limiting plugin..."
curl -i -X POST http://localhost:8001/services/las-api/plugins \
  --data 'name=rate-limiting' \
  --data 'config.minute=100' \
  --data 'config.policy=local'

# Add CORS Plugin
echo "Adding CORS plugin..."
curl -i -X POST http://localhost:8001/services/las-api/plugins \
  --data 'name=cors' \
  --data 'config.origins=*' \
  --data 'config.methods=GET,POST,PUT,DELETE,OPTIONS' \
  --data 'config.headers=Authorization,Content-Type'

# Add Response Transformer (add custom headers)
echo "Adding response transformer..."
curl -i -X POST http://localhost:8001/services/las-api/plugins \
  --data 'name=response-transformer' \
  --data 'config.add.headers=X-Powered-By:LAS-API'

echo "✅ Kong configuration complete!"
echo "🌐 Access Kong Admin UI at: http://localhost:1337"
echo "🔌 API Gateway URL: http://localhost:8000/api"
