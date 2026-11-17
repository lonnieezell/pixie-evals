---
type: llm
focus: trace
weight: 1
---

The preview route is registered only in the local environment: `php artisan route:list --path=__preview` lists it with APP_ENV=local, and not with APP_ENV=production
