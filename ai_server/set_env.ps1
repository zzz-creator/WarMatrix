<#
PowerShell helper to apply recommended environment variables for the AI server.
Dot-source this script to set variables in your current session (do not run normally).
Usage (PowerShell):
  . .\set_env.ps1

This script does NOT start the server; it only sets env vars for you to run later.
#>

# Recommended safe defaults for 6GB GPU
$env:MODEL_PATH = "..\ai_server\wargaming_llm\wargame_final_outputs\checkpoint-125"
$env:LOAD_IN_4BIT = "true"
$env:USE_8BIT = "false"
$env:CPU_OFFLOAD = "true"
$env:MAX_GPU_MEMORY_GB = "4.0"
$env:COMPUTE_DTYPE = "float16"
$env:INFERENCE_USE_CACHE = "false"
$env:EMPTY_CUDA_CACHE_AFTER_REQUEST = "true"

Write-Host "Environment variables applied to current session."
Write-Host "To keep them, add these to your shell profile or dot-source this file before running the server."
Write-Host "Note: this script does not start the AI server."
