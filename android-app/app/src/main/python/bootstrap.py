import os
import sys

try:
    from com.chaquo.python import Python
    context = Python.getPlatform().getApplication()
    files_dir = str(context.getFilesDir().getAbsolutePath())
    os.chdir(files_dir)
    print(f"Android: changed working directory to {files_dir}")
except ImportError:
    print("Not running on Android / Chaquopy not available")

import threading
import main
import admin_panel

try:
    import uvicorn
except ImportError:
    uvicorn = None

def start_bot():
    try:
        print("Android Bot Thread starting...")
        main.main()
    except Exception as e:
        print(f"Android Bot Crash: {e}")

def start_admin():
    if uvicorn is None:
        print("Android: Uvicorn not available, skipping local HTTP server.")
        return
    try:
        print("Android Admin Panel Thread starting...")
        # Start uvicorn server on local loopback interface
        uvicorn.run(admin_panel.app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Android Admin Crash: {e}")

def run():
    print("Initializing eFootball Android Bootstrap...")
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    admin_thread = threading.Thread(target=start_admin, daemon=True)
    
    bot_thread.start()
    admin_thread.start()
    print("Android Bootstrap Threads started successfully.")
