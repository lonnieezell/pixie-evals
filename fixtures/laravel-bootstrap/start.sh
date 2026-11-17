#!/usr/bin/env bash
# Install, build, seed and serve this fixture at http://localhost:${PORT:-8000}.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
composer install --no-interaction --no-progress
[ -f .env ] || cp .env.example .env
grep -q '^APP_KEY=base64:' .env || php artisan key:generate --no-interaction
touch database/database.sqlite
php artisan migrate:fresh --seed --force --no-interaction
npm install --no-audit --no-fund
npm run build
exec php artisan serve --port="$PORT" --no-reload
