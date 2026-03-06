ai_server environment setup

This folder contains helper files to set recommended environment variables for running the AI backend with constrained VRAM (6 GB GPUs).

Files:
- `.env.example` — Example env file (for other shells / dotenv loaders).
- `set_env.ps1` — PowerShell helper to apply the vars to your current session.

Quick usage (PowerShell)

- Open your virtualenv and workspace (you already have that):

```powershell
& .\.venv\Scripts\Activate.ps1
```

- Apply env vars to current shell (dot-source):

```powershell
. .\ai_server\set_env.ps1
```

- Verify variables (optional):

```powershell
Get-ChildItem Env:MAX_GPU_MEMORY_GB,Env:LOAD_IN_4BIT,Env:COMPUTE_DTYPE
```

- When ready, run the server yourself (example):

```powershell
python .\ai_server\backend_server.py
```

Notes:
- Adjust `MAX_GPU_MEMORY_GB` down if you still see high usage in `nvidia-smi`.
- If `LOAD_IN_4BIT` causes issues on your card, try `USE_8BIT=true` and `LOAD_IN_4BIT=false`.
- This setup does NOT start the server; you control when to run it.
