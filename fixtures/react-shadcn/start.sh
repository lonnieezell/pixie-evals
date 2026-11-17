#!/usr/bin/env bash
# Install, build and serve this fixture at http://localhost:${PORT:-5173}.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-5173}"
npm install --no-audit --no-fund
npm run build
exec npx vite --port "$PORT" --strictPort
