#!/usr/bin/env python3
# keepalive.py — auto-restart on crash
import subprocess, time, logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

RESTART_DELAY = 5
MAX_RESTARTS  = 9999

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
    run()
