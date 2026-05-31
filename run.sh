#!/data/data/com.termux/files/usr/bin/bash
echo "======================================"
echo "  eFootball Bot v8 — Termux Setup"
echo "======================================"
command -v python3 &>/dev/null || pkg install python -y
pip3 install -q python-telegram-bot aiosqlite --upgrade 2>/dev/null || \
    pip3 install python-telegram-bot aiosqlite
echo "✅ Dependencies ready."
echo "🚀 Starting bot..."
python3 keepalive.py
