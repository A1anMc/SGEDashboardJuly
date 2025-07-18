#!/bin/bash

# Test gunicorn configuration for Render deployment
set -e

echo "🔍 Testing gunicorn configuration..."

# Check if uvicorn workers are available
echo "Checking uvicorn workers..."
python -c "
try:
    import uvicorn.workers
    print('✅ uvicorn.workers available')
except ImportError as e:
    print(f'❌ uvicorn.workers not available: {e}')
    exit(1)
"

# Test gunicorn startup (short test)
echo "Testing gunicorn startup..."
export DATABASE_URL="sqlite:///test.db"
export SECRET_KEY="test-secret-key"
export JWT_SECRET_KEY="test-jwt-secret"
export ENVIRONMENT="development"
export DEBUG="false"

timeout 10 gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --keep-alive 120 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --preload \
  --log-level info \
  --error-logfile - \
  --access-logfile - \
  --capture-output &

GUNICORN_PID=$!

# Wait a moment for startup
sleep 3

# Test if server is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Gunicorn configuration working correctly"
else
    echo "❌ Gunicorn test failed"
    kill $GUNICORN_PID 2>/dev/null || true
    exit 1
fi

# Clean up
kill $GUNICORN_PID 2>/dev/null || true
rm -f test.db

echo "✅ Gunicorn configuration test passed!"