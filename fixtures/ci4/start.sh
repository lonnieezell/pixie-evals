#!/usr/bin/env bash
# Install, seed and serve this fixture at http://localhost:${PORT:-8080}.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8080}"
composer install --no-interaction --no-progress
cat > .env <<EOF
CI_ENVIRONMENT = development
app.baseURL = 'http://localhost:${PORT}/'
database.default.DBDriver = SQLite3
database.default.database = fixture.db
EOF
rm -f writable/fixture.db
php spark migrate --all
php spark db:seed DatabaseSeeder
exec php spark serve --port "$PORT"
