#!/usr/bin/env python3
# keepalive.py — auto-restart on crash + dummy HTTP server for Render
import subprocess, time, logging, threading, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

RESTART_DELAY = 5
MAX_RESTARTS  = 9999

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, format, *args):
        pass  # HTTP log বন্ধ রাখো

def start_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), PingHandler)
    logger.info(f"🌐 HTTP server started on port {port}")
    server.serve_forever()

def run():
    attempts = 0
    while attempts < MAX_RESTARTS:
        logger.info(f"🚀 Starting bot (attempt #{attempts + 1})")
        start = time.time()
        try:
            subprocess.run(['python3', 'main.py'])
        except KeyboardInterrupt:
            logger.info("⛔ Stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
        uptime = time.time() - start
        logger.warning(f"⚠️ Bot stopped (ran {uptime:.0f}s). Restarting in {RESTART_DELAY}s...")
        attempts += 1
        time.sleep(RESTART_DELAY)

if __name__ == '__main__':
    logger.info("=" * 40)
    logger.info(f"eFootball Bot Keepalive — {datetime.now():%Y-%m-%d %H:%M}")
    logger.info("=" * 40)
    # HTTP server আলাদা thread এ চালাও
    t = threading.Thread(target=start_http_server, daemon=True)
    t.start()
    run()
