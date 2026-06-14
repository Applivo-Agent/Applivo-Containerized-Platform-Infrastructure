#!/bin/sh

set -eu

export DISPLAY=:99

mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99

Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR >/tmp/xvfb.log 2>&1 &
fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -xkb >/tmp/x11vnc.log 2>&1 &

# Use solo pool for async code (SQLAlchemy async + asyncio + Playwright)
# This prevents "Event loop is closed" errors by ensuring single process/single event loop
LOGLEVEL="${LOG_LEVEL:-info}"
# Convert DEBUG/debug → info for Celery (debug is very noisy)
case "$LOGLEVEL" in
    DEBUG|debug) LOGLEVEL="info" ;;
esac
exec python -m celery -A app.celery_app:celery_app worker --loglevel="$LOGLEVEL" --pool=solo --concurrency=1 -Q scraping,apply