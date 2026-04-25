#!/bin/bash

# Frontend Development Server Script
# This script starts a simple HTTP server for the frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=${1:-3000}

echo "🚀 Starting ChatRoom Frontend"
echo "=============================="
echo ""
echo "📁 Directory: $SCRIPT_DIR"
echo "🌐 Port: $PORT"
echo "🔗 URL: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "Using Python 3..."
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    echo "Using Python..."
    python -m http.server $PORT
elif command -v npx &> /dev/null; then
    echo "Using Node.js serve..."
    npx serve . -l $PORT
else
    echo "❌ Error: No suitable server found."
    echo "Please install Python 3 or Node.js"
    exit 1
fi
