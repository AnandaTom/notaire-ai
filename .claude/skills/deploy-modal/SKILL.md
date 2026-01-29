---
name: deploy-modal
description: Deploy or serve the Notomai application on Modal. Use when user says "deploy", "deploy modal", "mise en production", "deployer", "serve local".
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
---

# Deploy to Modal - Notomai

Deploy or test the Notomai FastAPI application on Modal serverless platform.

## Arguments
- `$ARGUMENTS` - "prod" for production deploy, "local" or "test" for local serve, empty defaults to showing status

## Workflow

### Step 1: Pre-deploy checks
```bash
# Check Modal CLI is available
modal --version

# Run quick test suite
python -m pytest tests/ -x -q 2>&1

# Check .env has required vars
python -c "
from dotenv import load_dotenv; import os; load_dotenv()
required = ['SUPABASE_URL', 'SUPABASE_KEY']
missing = [k for k in required if not os.getenv(k)]
print('Missing vars:', missing if missing else 'None - all good')
"
```

### Step 2: Deploy or Serve

**Production deploy** (if $ARGUMENTS contains "prod"):
```bash
modal deploy modal/modal_app.py
```
Endpoint: `https://notaire-ai--fastapi-app.modal.run/`

**Local test** (if $ARGUMENTS contains "local" or "test"):
```bash
modal serve modal/modal_app.py
```

**Status only** (default):
```bash
# Show current deployment info
modal app list 2>&1 | head -20
```

### Step 3: Post-deploy verification
After production deploy:
```bash
# Health check
curl -s https://notaire-ai--fastapi-app.modal.run/health | python -m json.tool

# Status endpoint
curl -s https://notaire-ai--fastapi-app.modal.run/status | python -m json.tool
```

### Step 4: Report
```
## Deployment Report
- Mode: production/local
- Tests: PASS (X passed)
- Deploy: SUCCESS/FAILED
- Endpoint: <url>
- Health: OK/ERROR
```

## Critical Rules
- ALWAYS run tests before production deploy
- If tests fail, DO NOT deploy - report failures instead
- Check modal/modal_app.py for current configuration
- Do not modify modal_app.py secrets or memory settings without explicit approval
