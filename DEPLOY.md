# Deploying Finance OS / APAR (V2)

V1 was a static SPA, so Netlify alone was enough. **V2 has a real backend**
(FastAPI + the agent layer + SQLite), so it needs a Python-capable host.
The FastAPI app already serves the built SPA at `/app`, so the whole product
ships as **one** web service — no separate front-end host required.

## Route A — one free service on Render (recommended)

Files in this repo make it push-button:

- `Dockerfile` — builds the React SPA (calling its own origin, so no CORS) and
  runs the FastAPI app, which serves the API **and** the SPA.
- `render.yaml` — a Render Blueprint: one free Docker web service.
- `.dockerignore` — keeps the build context small.

### Steps

1. Push this repo to GitHub.
2. Go to **render.com → New → Blueprint**, pick the repo. Render reads
   `render.yaml` and creates the service (free plan, no credit card).
3. Wait for the first build/deploy (a few minutes).
4. Open the URLs:
   - App (UI): `https://<your-service>.onrender.com/app`
   - Health:   `https://<your-service>.onrender.com/health`
   - API docs: `https://<your-service>.onrender.com/docs`

That's it. The app re-seeds its mock data on boot, so it's live immediately.

### Notes / knobs (env vars on the Render dashboard)

- **AI explanations:** left unset, the app uses the offline deterministic
  narrator (no key, no GPU) — correct for a free host, since Ollama/Qwen can't
  run there. For live hosted AI, set `LLM_PROVIDER=anthropic` and `LLM_API_KEY`.
- **Database:** SQLite lives on the container's ephemeral disk on the free plan,
  so resolved items reset whenever the service restarts/spins down (it re-seeds
  the demo data each boot). To persist, upgrade to a paid instance with a disk
  and set `FINANCEOS_DB` to a path on it — or move to Postgres later (`repo.py`
  is the only swap point).
- **Idle spin-down:** free Render services sleep when idle and cold-start on the
  next request (a few seconds). Fine for demos.
- **Auth tokens** are in-memory and reset on restart — fine for a demo, not for
  real users.

## Other free/cheap hosts

Any host that runs a Docker container or a Python web service works the same way
(the `Dockerfile` is portable): e.g. **Railway** (auto-detects from GitHub; free
credit is small, ~$1/mo, so not 24/7). Fly.io no longer offers a free tier to new
signups.

## Run the container locally

```
docker build -t financeos-apar .
docker run -p 8000:8000 financeos-apar
# open http://localhost:8000/app
```
