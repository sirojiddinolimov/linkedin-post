#!/usr/bin/env bash
# Runs the daily Telegram -> RSS digest locally and pushes the result to
# GitHub, so LinkedIn's RSS source can pick it up. Schedule this with cron.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
source .env
set +a

git pull --ff-only

(cd src && python3 main.py)

git add docs/feed.xml docs/history.json state/last_post.json
if ! git diff --cached --quiet; then
  git commit -m "chore: publish daily digest entry"
  git push
else
  echo "Nothing new to publish."
fi
