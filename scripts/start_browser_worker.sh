#!/bin/sh

set -eu

export DISPLAY=:99

Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR >/tmp/xvfb.log 2>&1 &
fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -xkb >/tmp/x11vnc.log 2>&1 &

# Use solo pool for async code (SQLAlchemy async + asyncio + Playwright)
# This prevents "Event loop is closed" errors by ensuring single process/single event loop
exec python -m celery -A app.celery_app:celery_app worker --loglevel=info --pool=solo --concurrency=1 -Q scraping,apply