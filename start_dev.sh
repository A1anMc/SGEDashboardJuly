#!/bin/bash

# SGE Dashboard Development Startup Script

echo "🚀 Starting SGE Dashboard Development Environment"
echo "=================================================="

# Check if required directories exist
if [ ! -d "app" ]; then
    echo "❌ Backend directory 'app' not found. Please run from the project root."
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory 'frontend' not found. Please run from the project root."
    exit 1
fi

# Function to kill processes on exit
cleanup() {
    echo "🛑 Stopping development servers..."
    jobs -p | xargs -r kill
    wait
    echo "✅ Development servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start backend server
echo "🐍 Starting FastAPI backend server..."
cd "$PWD"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "⚛️  Starting Next.js frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "🎉 Development servers started successfully!"
echo "=================================================="
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "=================================================="
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for all background processes
wait