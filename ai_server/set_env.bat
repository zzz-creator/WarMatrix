@echo off
:: Set environment variables for RTX 5090 configuration inside venv

set MODEL_PATH=..\ai_server\wargaming_llm\wargame_final_outputs\checkpoint-125
set LOAD_IN_4BIT=true               :: Enable 4-bit quantization
set USE_8BIT=false                  :: No 8-bit quantization (RTX 5090 can handle more)
set CPU_OFFLOAD=true                :: Offload computations to CPU where needed
set MAX_GPU_MEMORY_GB=24            :: Set GPU memory to 24GB (RTX 5090 has ample VRAM)
set COMPUTE_DTYPE=float16           :: Use float16 for faster performance
set INFERENCE_USE_CACHE=true       :: Enable KV cache for faster inference
set EMPTY_CUDA_CACHE_AFTER_REQUEST=true  :: Clear CUDA cache after request to save memory

echo Environment variables applied to current session.
pause
