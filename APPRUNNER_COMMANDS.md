# App Runner Build and Start Commands

## Option 1: Using Dockerfile (Recommended - Your Current Setup)

**If you have a Dockerfile (which you do), App Runner automatically uses it.**

### Build Command
**No build command needed!** App Runner automatically runs:
```bash
docker build -t <service-name> .
```

The Dockerfile handles:
- Installing Poetry
- Installing dependencies (`poetry install --no-dev`)
- Copying application code
- Setting up the environment

### Start Command
**No start command needed!** App Runner uses the `CMD` instruction from your Dockerfile:
```bash
poetry run uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Configuration in AWS Console
When creating the service:
- **Build configuration**: Select **"Automatic"** or **"Use a configuration file"**
  - If Automatic: App Runner auto-detects Dockerfile
  - If config file: Point to `apprunner.yaml` (optional)
- **Port**: Set to `8000`
- **Start command**: Leave empty (Dockerfile CMD is used)

---

## Option 2: Source-Based Without Dockerfile

If you want to deploy without Dockerfile (not recommended for your setup):

### Build Command
```bash
poetry install --no-dev
```

### Start Command
```bash
poetry run uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Configuration
In AWS Console:
- **Build configuration**: Select **"Use a configuration file"**
- **Build command**: `poetry install --no-dev`
- **Start command**: `poetry run uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Port**: `8000`

---

## Recommended Setup (Your Current Configuration)

Since you have a Dockerfile, use **Option 1**:

### In AWS App Runner Console:

1. **Source**: Connect your GitHub/Bitbucket repository
2. **Build configuration**: 
   - Choose **"Automatic"** (recommended)
   - OR choose **"Use a configuration file"** and select `apprunner.yaml`
3. **Service configuration**:
   - Port: `8000`
   - Start command: **Leave empty** (Dockerfile CMD is used)
4. **Environment variables**: Add your Supabase/Database variables

### What Happens:
1. App Runner clones your repo
2. Detects `Dockerfile` in root
3. Runs: `docker build -t deal-deck-api .`
4. Runs container with: `docker run <image>` (uses Dockerfile CMD)
5. Routes traffic to port 8000

---

## Summary

**For your setup with Dockerfile:**

| Setting | Value |
|---------|-------|
| **Build command** | Leave empty (Dockerfile handles it) |
| **Start command** | Leave empty (Dockerfile CMD handles it) |
| **Port** | `8000` |
| **Build config** | "Automatic" (auto-detects Dockerfile) |

The Dockerfile already contains:
- ✅ Build steps (installing Poetry, dependencies)
- ✅ Start command (`CMD poetry run uvicorn...`)

So you don't need to specify build/start commands in App Runner!

