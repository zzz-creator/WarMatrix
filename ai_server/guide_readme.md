# Backend Guide — model-backed SITREP server

This guide explains how to run the Python backend that serves your fine-tuned checkpoint and how to test it from a Next.js app.

**Quick note about `{"error":"Not found"}`**
- You got `{"error":"Not found"}` because you requested the server root (`/`). The backend exposes specific endpoints — use `/health` and `/api/sitrep`.
- If your browser opens Google search instead of your API, type the full URL including protocol, for example: `http://127.0.0.1:8000/health`.

**Endpoints**
- `GET /health` — returns JSON status (checks model loaded, device)
- `POST /api/echo` — echoes JSON request
- `POST /api/sitrep` — run model inference; accepts JSON body (see below)

**`/api/sitrep` request JSON**
- Required: `battlefield_data` (string)
- Optional: `instruction`, `max_new_tokens`, `temperature`, `top_p`

Example body:
```json
{
  "instruction": "Generate a comprehensive tactical SITREP based on the current battlefield variables.",
  "battlefield_data": "Location: Obsidian Gorge\nTerrain: Narrow volcanic canyon...",
  "max_new_tokens": 220,
  "temperature": 0.45,
  "top_p": 0.9
}
```

**Run the server (recommended: run outside the Next.js process)**
1. Place `backend_server.py` in a `server/` folder in your Next.js project (optional).
2. Do NOT commit the full checkpoint into your repo. Place the checkpoint on the host machine and update `MODEL_PATH`.
3. Create and activate a Python venv (or use conda):

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r server/requirements.txt
python server/backend_server.py
```

Linux / macOS:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
python server/backend_server.py
```

**Quick tests**
- Health (curl):
```bash
curl http://127.0.0.1:8000/health
```
- SITREP (curl):
```bash
curl -X POST http://127.0.0.1:8000/api/sitrep \
  -H "Content-Type: application/json" \
  -d '{"instruction":"Generate a SITREP","battlefield_data":"Location: ..."}'
```

**Why you saw `Not found`**
- The server returns 404 for unknown routes. Use `/health` or `/api/sitrep` instead of `/`.

**Requirements & notes**
- Create `server/requirements.txt` (example):
```
transformers>=5.0
peft>=0.8
bitsandbytes
sentencepiece
accelerate
```
- Install `torch` matching your CUDA. If `bitsandbytes` or 4-bit support is unavailable, set `LOAD_IN_4BIT = False` in `backend_server.py`.
- Keep the checkpoint outside git; add it to `.gitignore`.

**Next.js integration**
- You can call `http://127.0.0.1:8000/api/sitrep` from your Next.js server-side code or client-side code (CORS is enabled).
- Optionally add a Next.js API route that proxies requests so the frontend uses a relative path.

**Troubleshooting**
- If `/health` returns `model_loaded:false` wait for model to load or check logs for exceptions.
- If model load fails due to `bitsandbytes` or CUDA mismatch, install the proper `torch` and `bitsandbytes` versions or switch to CPU loading (`LOAD_IN_4BIT=False`).

If you want, I can now:
- Add `server/requirements.txt` and `.gitignore` to this repo,
- Move `backend_server.py` into a `server/` folder,
- Or create a Next.js proxy route for convenience.

File: `guide_readme.md`