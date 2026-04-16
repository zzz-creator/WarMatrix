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

Model checkpoints:
- The server loads a LoRA adapter checkpoint from the folder specified by the `MODEL_PATH` environment variable. If `MODEL_PATH` is not set, the server falls back to a relative default and also searches common locations (including your local clone layout).
- Common example path on this machine: `C:\Users\FIDO\wargaming_llm\wargame_final_outputs\checkpoint-125` — you can point the server to that folder explicitly:

```powershell
$env:MODEL_PATH = 'C:\Users\FIDO\wargaming_llm\wargame_final_outputs\checkpoint-125'
```

- The checkpoint folder must contain `adapter_config.json`. If it's missing the server will raise a FileNotFoundError and print the list of paths it searched.
- You can verify which path the server resolved by calling the health endpoint `GET /health` — the JSON includes a `model_path` field showing the resolved location.

LM Studio Proxy Mode (GGUF Support)

You can bypass the heavy local model loading (requiring ~4-6GB VRAM) by proxying requests to an external LM Studio instance (e.g., running a larger GGUF model on a different machine in your network).

- **`USE_LM_STUDIO`**: Set to `true` to enable proxy mode.
- **`LM_STUDIO_IP`**: The local network address of the LM Studio host (e.g., `192.168.1.15`).
- **`LM_STUDIO_PORT`**: The API port (default is `1234`).
- **`LM_STUDIO_API_KEY`**: Bearer token if your LM Studio setup requires authentication.

When `USE_LM_STUDIO` is active, the server starts almost instantly and forwards all tactical SITREP requests to the specified endpoint.
