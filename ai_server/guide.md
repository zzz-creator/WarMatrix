# Integration Guide for Copilot AI — Move backend to Next.js project

Purpose
- Instruct an automated agent (Copilot / script) exactly how to copy the *required* files from the source workspace at `C:\Users\FIDO\wargaming_llm` into a Next.js project root, placing the Python backend server into a separate folder `ai_server` inside the Next.js root.
- Preserve model checkpoint files outside the web repo (do NOT copy `wargame_final_outputs` into the git repo).

Assumptions
- Source folder (current workspace) is: `C:\Users\FIDO\wargaming_llm`
- Destination Next.js project root (variable): `NEXTJS_ROOT` — the AI operator will supply this path when invoking the script/agent.
- The agent running these instructions has filesystem permission to read the source and write the destination and can run PowerShell commands on Windows.

High-level steps the agent must perform (exact order)
1. Validate both paths exist and are accessible.
2. Create a folder `ai_server` in the Next.js root.
3. Copy only the required source code files (listed below) into `ai_server`.
4. Create `requirements.txt` and `.gitignore` inside `ai_server`.
5. Ensure the model checkpoint is NOT copied into the git repo. Instead configure `MODEL_PATH` in `ai_server/backend_server.py` to reference a path outside the web repo (relative or absolute) and document where to place the checkpoint.
6. Optionally create a Next.js API proxy route that forwards `/api/sitrep` to `http://127.0.0.1:8000/api/sitrep` (recommended but optional).
7. Report success/failure and list files copied and any modifications made.

Files to copy (source → destination `NEXTJS_ROOT/ai_server`)
- `backend_server.py`            — Python backend (core server)
- `guide_readme.md`             — Usage notes and instructions (kept with server)
- `test_tactical_brain.py`      — optional test script (copy only if requested)
- `guide.md`                    — this integration guide (copy for record)

Do NOT copy
- `wargame_final_outputs/`      — model checkpoints and weights (very large)
- `unsloth_compiled_cache/`     — compiled large artifacts
- `unsloth_outputs/`            — training outputs
- Any `*.safetensors`, `*.pt`, `*.pth` weight files unless explicitly requested and authorized

Exact PowerShell commands the agent should run
(Agent will replace `NEXTJS_ROOT` with provided destination path.)

1) Validate source and destination paths
```powershell
$SRC = 'C:\Users\FIDO\wargaming_llm'
$DST = 'C:\path\to\your\nextjs_root'  # REPLACE with NEXTJS_ROOT provided by operator
if (-not (Test-Path $SRC)) { Write-Error "Source path $SRC does not exist"; exit 1 }
if (-not (Test-Path $DST)) { Write-Error "Destination path $DST does not exist"; exit 1 }
```

2) Create `ai_server` folder and copy required files
```powershell
$AI = Join-Path $DST 'ai_server'
New-Item -ItemType Directory -Force -Path $AI | Out-Null

# Copy the minimal files
$files = @('backend_server.py','guide_readme.md','test_tactical_brain.py','guide.md')
foreach ($f in $files) {
  $srcf = Join-Path $SRC $f
  if (Test-Path $srcf) { Copy-Item -Path $srcf -Destination $AI -Force }
}
```

3) Create `requirements.txt` and `.gitignore` in `ai_server`
```powershell
$req = @(
  'transformers>=5.0',
  'peft>=0.8',
  'bitsandbytes',
  'sentencepiece',
  'accelerate'
)
$req | Out-File -FilePath (Join-Path $AI 'requirements.txt') -Encoding utf8

$gitignore = @(
  '# Python envs',
  '.venv/',
  'env/',
  '# Model checkpoints (do not commit)',
  'wargame_final_outputs/',
  '*.safetensors',
  '*.pt',
  '*.pth'
)
$gitignore | Out-File -FilePath (Join-Path $AI '.gitignore') -Encoding utf8
```

4) Configure `MODEL_PATH` inside `ai_server/backend_server.py`
- The agent must not hard-copy model checkpoints into the repo. The recommended setting is a path outside the Next.js project, for example: `C:\models\wargame_final_outputs\checkpoint-125` or `..\wargame_final_outputs\checkpoint-125` (a sibling folder).
- Modify `MODEL_PATH` with a reliable absolute or relative path and leave a human-friendly comment.

Exact PowerShell edit pattern (simple replace)
```powershell
$backend = Join-Path $AI 'backend_server.py'
(Get-Content $backend) -replace "MODEL_PATH = \"wargame_final_outputs/checkpoint-125\"", "MODEL_PATH = \"../wargame_final_outputs/checkpoint-125\"  # update if needed" | Set-Content $backend -Encoding utf8
```

5) (Optional) Create a Next.js API proxy (recommended)
- If your Next.js project uses the `app` router, create file `NEXTJS_ROOT/app/api/sitrep/route.ts` with a single POST proxy handler that forwards requests to `http://127.0.0.1:8000/api/sitrep`.
- Minimal example (TypeScript):
```ts
import { NextResponse } from 'next/server'
export async function POST(req: Request) {
  const body = await req.text()
  const res = await fetch('http://127.0.0.1:8000/api/sitrep', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body,
  })
  const text = await res.text()
  return new NextResponse(text, { status: res.status })
}
```

6) Start instructions to run server on target machine (PowerShell)
```powershell
# in NEXTJS_ROOT\ai_server
cd $AI
# (recommended) create venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# ensure torch is installed matching CUDA, for example (adjust as needed):
# pip install torch --index-url https://download.pytorch.org/whl/cu124
python backend_server.py
```

7) Test endpoints (PowerShell)
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health -Method Get | ConvertTo-Json -Compress
$b = @{ battlefield_data = 'Location: Test`nTerrain: Urban'; max_new_tokens = 128 } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/sitrep -Method Post -ContentType 'application/json' -Body $b | ConvertTo-Json -Compress
```

8) Post-copy reporting the agent must provide (JSON output)
- `copied_files`: list of files copied
- `ai_server_path`: destination path
- `model_path_set_to`: the `MODEL_PATH` value written into `backend_server.py`
- `notes`: any missing files from source or manual actions required (e.g., place checkpoint at X)

Important safety and size notes for the agent
- Do NOT copy `wargame_final_outputs` into the web project. Always keep model checkpoints out of the code repo.
- If the destination machine has limited memory, set `LOAD_IN_4BIT=False` in `backend_server.py` before launching, or add instructions to increase Windows page file size if Windows error 1455 occurs.

If the operator asks for a fully automated run, the agent should request the following values first
- `NEXTJS_ROOT` — path to copy into (required)
- `MODEL_STORAGE_PATH` — where the model will be placed on the host (recommended; can be external to repo)
- `COPY_TEST_SCRIPT` — boolean: whether to copy `test_tactical_brain.py` (optional)

End of guide

--
File created: `guide.md`