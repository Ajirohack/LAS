#!/bin/bash

# LAS Startup Script
# Run both backend and frontend servers

echo "🚀 Starting Local Agent System..."

# Kill any existing processes on ports 7777 and 3000
echo "Cleaning up existing processes..."
lsof -ti:7777 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start backend server
echo "📡 Starting backend server on port 7777..."
cd "$(dirname "$0")/las_core"
python3 -m uvicorn api:app --host 0.0.0.0 --port 7777 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server on port 3000..."
cd "$(dirname "$0")/las_core/frontend/las-ui-v2"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ LAS is starting up!"
echo "Backend API: http://localhost:7777"
echo "API Docs: http://localhost:7777/docs"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped'; exit" INT
wait
