#!/bin/bash
echo "==================================================="
echo "🚀 eFootball Telegram Bot & Admin Panel Setup (Linux)"
echo "==================================================="
echo ""

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ python3 is not installed!"
    echo "Please install python3 first (e.g., sudo apt install python3 python3-pip)"
    exit 1
fi

echo "⏳ Installing/updating dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install fastapi uvicorn pydantic python-telegram-bot aiosqlite

if [ $? -ne 0 ]; then
    echo "⚠️ Dependency installation had some issues, trying to run anyway..."
else
    echo "✅ Dependencies installed successfully!"
fi
echo ""

# Function to clean up background processes on exit (Ctrl+C)
cleanup() {
    echo ""
    echo "🛑 Stopping Bot and Admin Panel..."
    kill $BOT_PID $ADMIN_PID 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Telegram Bot..."
python3 main.py &
BOT_PID=$!

echo "🚀 Starting FastAPI Admin Web Panel..."
python3 admin_panel.py &
ADMIN_PID=$!

echo ""
echo "==================================================="
echo "🎉 Both the Bot and Admin Panel are running!"
echo "💻 Open http://localhost:8000 in your browser to access the Admin Panel."
echo "👉 Press Ctrl+C to stop both processes cleanly."
echo "==================================================="
echo ""

# Wait for background jobs to finish
wait
