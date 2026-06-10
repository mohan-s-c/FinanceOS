# Finance OS / APAR — single-service container (deploy Route A).
# Stage 1 builds the React SPA; stage 2 runs the FastAPI app, which serves BOTH
# the JSON API (/api, /health) and the built SPA (/app) from the same origin.

# ---- stage 1: build the front-end ----
FROM node:22-slim AS web
WORKDIR /repo
# Note: we intentionally do NOT copy package-lock.json. It is generated on the
# developer's OS and pins OS-specific native bindings (rolldown/lightningcss),
# which makes `npm ci` fail on Linux. `npm install` resolves the Linux binaries.
COPY package.json ./
COPY apps/web ./apps/web
COPY packages/shared ./packages/shared
RUN npm install --no-audit --no-fund
# Empty base URL => the SPA calls its own origin (one host serves /api and /app),
# so there is no cross-origin call and no CORS to configure.
RUN VITE_API_BASE_URL="" npm run build

# ---- stage 2: runtime (API + built SPA) ----
FROM python:3.11-slim AS app
WORKDIR /repo
COPY services/api/requirements.txt ./services/api/requirements.txt
RUN pip install --no-cache-dir -r services/api/requirements.txt
# Source for the API + agents + shared/connectors (added to sys.path at runtime).
COPY services ./services
COPY packages ./packages
# The built SPA — FastAPI's main.py serves ../../apps/web/dist at /app.
COPY --from=web /repo/apps/web/dist ./apps/web/dist
WORKDIR /repo/services/api
ENV PYTHONUNBUFFERED=1
# Bind the platform-provided $PORT (Render/Heroku style); default 8000 locally.
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
