# WarMatrix Local Setup Guide

WarMatrix is a multi-component system consisting of a Next.js frontend, Python FastAPI backend simulation engine, and a local LLM-powered AI server. This guide covers setting up all components on your local machine.

## System Requirements

- **OS**: Windows, macOS, or Linux
- **Node.js**: v18+ (for Next.js frontend)
- **Python**: 3.10+
- **GPU**: Recommended (NVIDIA with CUDA 12.1+ for AI server; 6GB+ VRAM)
- **RAM**: 16GB+ total system memory
- **Disk Space**: 20GB+ (primarily for model checkpoints)

## Project Structure Overview

```
WarMatrix/
├── src/                 # Next.js frontend (React + Three.js)
├── backend/            # FastAPI simulation engine
├── ai_server/          # Local LLM backend server
│   └── wargaming_llm/  # Model training & fine-tuning
├── package.json        # Node.js dependencies
└── scripts/            # Development utilities
```

---

## Part 1: Frontend Setup (Next.js)

### 1.1 Install Node.js Dependencies

```bash
# From project root
npm install
```

This installs dependencies for the Next.js frontend including React, Tailwind CSS, Three.js, and UI components.

### 1.2 Verify TypeScript Setup

```bash
npm run typecheck
```

This checks for TypeScript compilation errors without building.

### 1.3 Understanding Frontend Structure

- **`src/app/`**: Next.js pages and API routes
  - `page.tsx`: Main landing page
  - `console/page.tsx`: Command console interface
  - `final-report/page.tsx`: After-action review display
  - `api/generate-scenario/route.ts`: Scenario generation endpoint
  - `api/sitrep/route.ts`: SITREP endpoint (communicates with backend)

- **`src/components/`**: React components for UI and 3D visualization
  - `TacticalMap3D.tsx`: Three.js 3D map renderer
  - `CommandConsole.tsx`: Command input interface
  - `StrategicAnalysisPanel.tsx`: Strategic analysis display
  - `AITerminalConsole.tsx`: AI response rendering

---

## Part 2: Backend Setup (FastAPI Simulation Engine)

### 2.1 Create Python Virtual Environment

```bash
# Navigate to project root
cd /path/to/WarMatrix

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2.2 Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Expected dependencies:
# - numpy
# - fastapi
# - uvicorn
# - pydantic
```

### 2.3 Understanding Backend Structure

- **`main.py`**: FastAPI application entry point
  - Hosts simulation API endpoints
  - Connects to AI server for SITREP generation
  - Default port: `8001`
  - AI server URL: `http://127.0.0.1:8000/api/sitrep`

- **`engine/`**: Core simulation logic
  - `game_state.py`: Manages battlefield state
  - `mcts.py`: Monte Carlo Tree Search algorithm
  - `monte_carlo.py`: Monte Carlo simulation
  - `actions.py`: Unit action definitions
  - `strategy.py`: Strategic decision logic
  - `probability.py`: Combat probability calculations
  - `enemy_model.py`: Enemy AI behavior

### 2.4 Run Backend Locally

```bash
# From backend directory (with venv activated)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001

# The backend will start at:
# http://127.0.0.1:8001
# API docs available at:
# http://127.0.0.1:8001/docs
```

---

## Part 3: AI Server Setup (Local LLM Backend)

### 3.1 Install AI Server Dependencies

```bash
# Activate the same virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Navigate to ai_server directory
cd ai_server

# Install dependencies
pip install -r requirements.txt

# Expected dependencies:
# - transformers>=5.0
# - peft>=0.8
# - bitsandbytes
# - sentencepiece
# - accelerate
```

### 3.2 GPU Memory Optimization (Optional but Recommended)

The AI server includes environment variable controls for VRAM-constrained GPUs (6GB+):

```bash
# ENVIRONMENT VARIABLES for BitsAndBytes quantization:
# MAX_GPU_MEMORY_GB  (default: 4.5) - GPU memory cap in GB
# LOAD_IN_4BIT       (default: true) - Enable 4-bit NF4 quantization
# COMPUTE_DTYPE      (default: float16) - Computation dtype: bfloat16|float16|float32
# MAX_NEW_TOKENS     (default: 150) - Maximum output tokens
# USE_CACHE          (default: true) - Enable KV cache (speeds up inference)
# DO_SAMPLE          (default: false) - Use sampling (true) or greedy decode (false)
# TEMPERATURE        (default: 0.7) - Sampling temperature
# TOP_P              (default: 0.9) - Nucleus sampling parameter

# Example: Set environment variables on Linux/macOS
export MAX_GPU_MEMORY_GB=4.5
export LOAD_IN_4BIT=true
export COMPUTE_DTYPE=float16

# Example: Set environment variables on Windows PowerShell
$env:MAX_GPU_MEMORY_GB = 4.5
$env:LOAD_IN_4BIT = $true
$env:COMPUTE_DTYPE = "float16"

# Or use the helper script (PowerShell only):
. .\ai_server\set_env.ps1
```

### 3.3 Model Checkpoint Setup

The AI server loads a fine-tuned Qwen model with LoRA adapters. You have three options:

#### Option A: Use Pre-trained Checkpoint (Recommended)

If you already have the trained checkpoint:

```bash
# Set the MODEL_PATH environment variable
# Example on Linux/macOS:
export MODEL_PATH="/path/to/wargame_final_outputs/checkpoint-125"

# Example on Windows PowerShell:
$env:MODEL_PATH = 'C:\path\to\wargame_final_outputs\checkpoint-125'

# The checkpoint folder must contain:
# - adapter_config.json
# - adapter_model.bin
# - training_args.bin
```

#### Option B: Download Base Model Only (First Run)

The server will automatically download the base Qwen model on first run:

```bash
# The model will be cached in your Hugging Face cache directory
# (~25-30GB download)
```

#### Option C: Train Your Own Model (See Part 4)

### 3.4 Verify AI Server Setup

```bash
# From ai_server directory
python backend_server.py

# The server will start at:
# http://127.0.0.1:8000
# Health check endpoint:
# GET http://127.0.0.1:8000/health
# Returns: { "status": "ok", "model_path": "..." }
```

---

## Part 4: Wargaming LLM Training (Optional)

This component fine-tunes a Qwen model using the Unsloth framework for tactical scenario generation and SITREP analysis.

### 4.1 Install Wargaming LLM Dependencies

```bash
# Activate virtual environment
# From project root:
source .venv/bin/activate  # Linux/macOS
# or
.\.venv\Scripts\activate  # Windows

# Navigate to wargaming_llm directory
cd ai_server/wargaming_llm

# Install training dependencies
pip install -r ../requirements.txt
pip install unsloth
pip install trl datasets
```

### 4.2 Prepare Training Data

The training script expects a JSONL dataset file:

```bash
# Location: ai_server/wargaming_llm/wargame_dataset.jsonl
# Format: One JSON object per line
# Example:
# {"text": "SITREP: 1st Battalion positioned at coordinates..."}
# {"text": "SITREP: Enemy movement detected in sector..."}
```

If you don't have the dataset:

```bash
# Use the dataset builder script
cd ai_server/wargaming_llm
python wargame_dataset_builder.py

# This will generate or augment wargame_dataset.jsonl
```

### 4.3 Train the Model

```bash
# From ai_server/wargaming_llm directory
python wargame_unsloth.py

# Training parameters:
# - Model: unsloth/Qwen3.5-4B
# - Max sequence length: 1024
# - LoRA rank (r): 32
# - Batch size: auto-optimized for available GPU
# - Output: checkpoints/ directory

# The script will:
# 1. Load and prepare the base Qwen model
# 2. Apply LoRA adapters for efficient fine-tuning
# 3. Run training on your dataset
# 4. Save checkpoints to wargame_final_outputs/
```

### 4.4 Use Trained Checkpoint

After training, point the AI server to your checkpoint:

```bash
# Set MODEL_PATH to the latest checkpoint
export MODEL_PATH="/path/to/wargame_final_outputs/checkpoint-125"

# Then run the AI server
python backend_server.py
```

---

## Part 5: Running Everything Together

### 5.1 Development Mode (All Services)

You can run all services with the provided orchestration script:

```bash
# From project root, with .venv activated
npm run dev

# This runs:
# - Next.js frontend on port 9002 (with Turbopack)
# - Python backend on port 8001
# - (Note: AI server must be started separately if needed)
```

### 5.2 Manual Full Stack Setup

Run each service in a separate terminal:

**Terminal 1 - Frontend:**
```bash
npm run dev:next
# Runs on http://localhost:9002
```

**Terminal 2 - Backend:**
```bash
npm run dev:backend
# Runs on http://127.0.0.1:8001
```

**Terminal 3 - AI Server:**
```bash
# From ai_server directory (with venv activated)
python backend_server.py
# Runs on http://127.0.0.1:8000
```

### 5.3 Verify All Services

Once running:

1. **Frontend**: http://localhost:9002
2. **Backend API Docs**: http://127.0.0.1:8001/docs
3. **AI Server Health**: `curl http://127.0.0.1:8000/health`

---

## Troubleshooting

### Issues with Backend

**Error: Address already in use (port 8001)**
```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process and retry
```

**Error: Module not found (numpy, fastapi, etc.)**
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install -r backend/requirements.txt
```

### Issues with AI Server

**Error: CUDA out of memory**
```bash
# Reduce GPU memory allocation
export MAX_GPU_MEMORY_GB=3.0  # or lower
# Try 8-bit quantization instead of 4-bit
export LOAD_IN_4BIT=false
export USE_8BIT=true
```

**Error: Model not found**
```bash
# Verify MODEL_PATH is set correctly
echo $MODEL_PATH  # Linux/macOS
echo $env:MODEL_PATH  # Windows PowerShell

# Verify adapter_config.json exists in checkpoint folder
ls /path/to/checkpoint/adapter_config.json
```

**Error: No CUDA device found**
```bash
# Check NVIDIA GPU availability
nvidia-smi

# If no GPU, the model still works on CPU (very slow)
# Or install CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issues with Frontend

**Error: Port 9002 already in use**
```bash
# Use a different port
npm run dev:next -- -p 3000
```

**Error: Module not found (React, Tailwind, etc.)**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Performance Tips

### Frontend
- Use Turbopack for faster development builds
- Enable SWC minification for faster production builds

### Backend
- Enable KV cache in AI server (USE_CACHE=true)
- Use greedy decoding instead of sampling (DO_SAMPLE=false)
- Reduce MAX_NEW_TOKENS if inference is slow

### AI Server
- Use 4-bit quantization on GPUs with <8GB VRAM
- Use float16 for better speed/accuracy tradeoff
- Set LOAD_IN_4BIT=false and USE_8BIT=true if 4-bit causes issues

### Wargaming LLM Training
- Use gradient checkpointing (enabled in wargame_unsloth.py)
- Reduce batch size if running out of memory
- Monitor training with the TRL Trainer dashboard

---

## Environment Variables Reference

### AI Server (.env file or shell export)

```
# Model loading
MODEL_PATH=

# VRAM optimization
MAX_GPU_MEMORY_GB=4.5
LOAD_IN_4BIT=true
COMPUTE_DTYPE=float16
USE_8BIT=false

# Inference parameters
MAX_NEW_TOKENS=150
USE_CACHE=true
DO_SAMPLE=false
TEMPERATURE=0.7
TOP_P=0.9

# Server
AI_SERVER_HOST=127.0.0.1
AI_SERVER_PORT=8000
```

### Backend

```
# FastAPI
DEBUG=false
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8001

# AI Server connection
AI_SERVER_URL=http://127.0.0.1:8000/api/sitrep
```

### Frontend

```
# API endpoints
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8001
NEXT_PUBLIC_AI_SERVER_URL=http://127.0.0.1:8000
```

---

## Next Steps

1. **Run the frontend**: `npm run dev:next`
2. **Start the backend**: `npm run dev:backend`
3. **Launch AI server**: `python ai_server/backend_server.py`
4. **Access the application**: http://localhost:9002
5. **Create a scenario**: Use the Scenario Builder interface
6. **Issue commands**: Use the Secure Comms Console for natural language commands
7. **Review results**: Check the Final Mission Report after scenario completion

---

## Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Unsloth Documentation**: https://github.com/unslothai/unsloth
- **Hugging Face Transformers**: https://huggingface.co/docs/transformers
- **Three.js Documentation**: https://threejs.org/docs
- **PEFT (LoRA) Documentation**: https://huggingface.co/docs/peft

---

## Support

For issues, check the troubleshooting section above or refer to the project's main README.md.
