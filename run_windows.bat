@echo off
chcp 65001 >nul
title eFootball Bot Setup and Launcher
echo ===================================================
echo eFootball Telegram Bot and Admin Panel Setup (Windows)
echo ===================================================
echo.

:: Check if Python is installed (check python first, then py)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto py_ok
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=py
    goto py_ok
)

echo [ERROR] Python is not installed or not in PATH!
echo Please install Python (version 3.8+) and check "Add Python to PATH".
echo.
pause
exit /b

:py_ok
echo [INFO] Using Python command: %PY_CMD%
echo.

echo [INFO] Installing/updating dependencies...
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install fastapi uvicorn pydantic python-telegram-bot aiosqlite

if %errorlevel% neq 0 (
    echo [WARNING] Dependency installation encountered some issues, trying to run anyway...
) else (
    echo [OK] Dependencies installed successfully!
)
echo.

echo [INFO] Starting Telegram Bot in a new window...
start "eFootball Bot" %PY_CMD% main.py

echo [INFO] Starting FastAPI Admin Web Panel in a new window...
start "eFootball Admin Panel" %PY_CMD% admin_panel.py

echo.
echo ===================================================
echo Both the Bot and Admin Panel are running!
echo Open http://localhost:8000 in your browser to access the Admin Panel.
echo ===================================================
echo.
pause
