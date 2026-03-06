import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

HOST = "127.0.0.1"
PORT = 8000
MODEL_PATH = os.environ.get("MODEL_PATH", "..\\wargame_final_outputs\\checkpoint-125")
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = os.environ.get("LOAD_IN_4BIT", "true").strip().lower() in {"1", "true", "yes", "on"}
USE_8BIT = os.environ.get("USE_8BIT", "false").strip().lower() in {"1", "true", "yes", "on"}
CPU_OFFLOAD = os.environ.get("CPU_OFFLOAD", "true").strip().lower() in {"1", "true", "yes", "on"}
MAX_GPU_MEMORY_GB = float(os.environ.get("MAX_GPU_MEMORY_GB", "4.5"))
COMPUTE_DTYPE = os.environ.get("COMPUTE_DTYPE", "float16").strip().lower()
INFERENCE_USE_CACHE = os.environ.get("INFERENCE_USE_CACHE", "false").strip().lower() in {"1", "true", "yes", "on"}
EMPTY_CUDA_CACHE_AFTER_REQUEST = os.environ.get("EMPTY_CUDA_CACHE_AFTER_REQUEST", "true").strip().lower() in {"1", "true", "yes", "on"}

_model = None
_tokenizer = None
_model_lock = threading.Lock()
_resolved_model_path = None


def _get_base_model_name(adapter_path: str) -> str:
    adapter_config_path = Path(adapter_path) / "adapter_config.json"
    with open(adapter_config_path, "r", encoding="utf-8") as f:
        adapter_config = json.load(f)
    return adapter_config["base_model_name_or_path"]


def _resolve_model_path(model_path: str) -> str:
    requested = Path(model_path)
    ai_server_dir = Path(__file__).resolve().parent
    candidates = []

    if requested.is_absolute():
        candidates.append(requested)
    else:
        # Support running from either ai_server or another current working directory.
        candidates.append(Path.cwd() / requested)
        candidates.append(ai_server_dir / requested)

    # Common fallbacks for local workspace layouts.
    candidates.append(ai_server_dir.parent.parent / "wargaming_llm" / "wargame_final_outputs" / "checkpoint-125")
    if len(ai_server_dir.parents) >= 3:
        candidates.append(ai_server_dir.parents[2] / "wargaming_llm" / "wargame_final_outputs" / "checkpoint-125")

    deduped = []
    seen = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        key = str(resolved).lower()
        if key not in seen:
            deduped.append(resolved)
            seen.add(key)

    for candidate in deduped:
        if (candidate / "adapter_config.json").exists():
            return str(candidate)

    searched = "\n".join(f"- {p}" for p in deduped)
    raise FileNotFoundError(
        "Could not find adapter checkpoint (adapter_config.json missing).\n"
        "Set MODEL_PATH to your checkpoint folder, for example:\n"
        "  $env:MODEL_PATH='C:\\models\\wargame_final_outputs\\checkpoint-125'\n"
        f"Searched:\n{searched}"
    )


def build_prompt(instruction: str, battlefield_data: str) -> str:
    return (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n"
        "Return only the final SITREP output. Do not include reasoning, analysis notes, or <think> blocks.\n\n"
        f"### Instruction:\n{instruction}\n\n"
        f"### Input:\n{battlefield_data}\n\n"
        "### Response:\n"
    )


def clean_response_text(text: str) -> str:
    # Remove chain-of-thought style blocks if model emits them.
    if "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>") + len("</think>")
        text = (text[:start] + text[end:]).strip()

    # If model outputs a leading marker line, strip it.
    if text.startswith("Response:"):
        text = text[len("Response:") :].strip()

    return text.strip()


def _resolve_compute_dtype() -> torch.dtype:
    if COMPUTE_DTYPE == "bfloat16":
        return torch.bfloat16
    if COMPUTE_DTYPE == "float32":
        return torch.float32
    return torch.float16


def load_model() -> None:
    global _model, _tokenizer, _resolved_model_path
    if _model is not None and _tokenizer is not None:
        return

    _resolved_model_path = _resolve_model_path(MODEL_PATH)
    base_model_name = _get_base_model_name(_resolved_model_path)
    _tokenizer = AutoTokenizer.from_pretrained(_resolved_model_path, trust_remote_code=True)

    has_cuda = torch.cuda.is_available()
    model_kwargs = {"trust_remote_code": True}
    compute_dtype = _resolve_compute_dtype()

    if has_cuda and LOAD_IN_4BIT and not USE_8BIT:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        model_kwargs["device_map"] = "auto"
    elif has_cuda and USE_8BIT:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=CPU_OFFLOAD,
        )
        model_kwargs["device_map"] = "auto"
    elif has_cuda:
        model_kwargs["torch_dtype"] = compute_dtype
        model_kwargs["device_map"] = "auto"
    else:
        model_kwargs["torch_dtype"] = torch.float32

    if has_cuda:
        # Leave headroom on 6 GB cards so other GPU work can run while the server is alive.
        gpu_mem_mb = max(int(MAX_GPU_MEMORY_GB * 1024), 1024)
        model_kwargs["max_memory"] = {0: f"{gpu_mem_mb}MiB", "cpu": "48GiB"}

    if CPU_OFFLOAD:
        offload_dir = Path(__file__).resolve().parent / "offload"
        offload_dir.mkdir(parents=True, exist_ok=True)
        model_kwargs["offload_folder"] = str(offload_dir)

    # Lower peak host RAM usage during weight loading on Windows.
    model_kwargs["low_cpu_mem_usage"] = True
    model_kwargs["offload_state_dict"] = True

    try:
        base_model = AutoModelForCausalLM.from_pretrained(base_model_name, **model_kwargs)
        _model = PeftModel.from_pretrained(base_model, _resolved_model_path)
        _model.eval()
    except OSError as exc:
        err = str(exc)
        if "os error 1455" in err.lower() or "paging file is too small" in err.lower():
            raise RuntimeError(
                "Model load failed due to low Windows virtual memory (paging file). "
                "Increase page file size (System managed or >= 32 GB), then restart the backend. "
                "If needed, set LOAD_IN_4BIT=False to reduce loader complexity."
            ) from exc
        raise


def generate_sitrep(
    instruction: str,
    battlefield_data: str,
    max_new_tokens: int = 384,
    temperature: float = 0.45,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
) -> str:
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model is not loaded")

    prompt = build_prompt(instruction=instruction, battlefield_data=battlefield_data)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    with _model_lock:
        inputs = _tokenizer(text=[prompt], return_tensors="pt").to(device)
        with torch.inference_mode():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                use_cache=INFERENCE_USE_CACHE,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=4,
            )

    decoded = _tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    response = decoded.split("### Response:\n")[-1].strip()

    if torch.cuda.is_available() and EMPTY_CUDA_CACHE_AFTER_REQUEST:
        # Return cached allocator blocks so non-server GPU work can run concurrently.
        del inputs
        del outputs
        torch.cuda.empty_cache()

    return clean_response_text(response)


class BackendHandler(BaseHTTPRequestHandler):
    def _normalized_path(self) -> str:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path if path else "/"

    def _query_params(self) -> dict:
        parsed = urlparse(self.path)
        return parse_qs(parsed.query)

    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        path = self._normalized_path()
        query = self._query_params()

        if path == "/":
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "wargaming-backend",
                    "message": "Use /health, /api/echo, or /api/sitrep",
                    "endpoints": {
                        "GET": ["/", "/health", "/api/echo", "/api/sitrep"],
                        "POST": ["/api/echo", "/api/sitrep"],
                    },
                },
            )
            return

        if path == "/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "wargaming-backend",
                    "model_loaded": _model is not None,
                    "model_path": _resolved_model_path or MODEL_PATH,
                    "device": "cuda" if torch.cuda.is_available() else "cpu",
                },
            )
            return

        if path == "/api/echo":
            self._send_json(200, {"ok": True, "received": query})
            return

        if path == "/api/sitrep":
            battlefield_data = query.get("battlefield_data", [""])[0]
            instruction = query.get("instruction", ["Generate a tactical SITREP."])[0]

            if not battlefield_data:
                self._send_json(
                    400,
                    {
                        "error": "battlefield_data is required",
                        "hint": "Send POST JSON or add ?battlefield_data=... in URL",
                    },
                )
                return

            max_new_tokens = int(query.get("max_new_tokens", ["220"])[0])
            temperature = float(query.get("temperature", ["0.45"])[0])
            top_p = float(query.get("top_p", ["0.9"])[0])

            try:
                response_text = generate_sitrep(
                    instruction=instruction,
                    battlefield_data=str(battlefield_data),
                    max_new_tokens=max(32, min(max_new_tokens, 1024)),
                    temperature=max(0.0, min(temperature, 2.0)),
                    top_p=max(0.1, min(top_p, 1.0)),
                )
            except Exception as exc:
                self._send_json(500, {"error": "inference_failed", "details": str(exc)})
                return

            self._send_json(200, {"ok": True, "response": response_text})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        path = self._normalized_path()
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        if path == "/api/echo":
            self._send_json(200, {"ok": True, "received": body})
            return

        if path == "/api/sitrep":
            instruction = body.get("instruction", "Generate a tactical SITREP.")
            battlefield_data = body.get("battlefield_data", "")

            if not battlefield_data:
                self._send_json(400, {"error": "battlefield_data is required"})
                return

            max_new_tokens = int(body.get("max_new_tokens", 384))
            temperature = float(body.get("temperature", 0.45))
            top_p = float(body.get("top_p", 0.9))

            try:
                response_text = generate_sitrep(
                    instruction=instruction,
                    battlefield_data=str(battlefield_data),
                    max_new_tokens=max(32, min(max_new_tokens, 1024)),
                    temperature=max(0.0, min(temperature, 2.0)),
                    top_p=max(0.1, min(top_p, 1.0)),
                )
            except Exception as exc:
                self._send_json(500, {"error": "inference_failed", "details": str(exc)})
                return

            self._send_json(
                200,
                {
                    "ok": True,
                    "response": response_text,
                },
            )
            return

        self._send_json(404, {"error": "Not found"})


def run() -> None:
    print("Loading fine-tuned model...")
    load_model()
    print("Model loaded successfully.")
    print(f"Using model path: {_resolved_model_path}")

    server = ThreadingHTTPServer((HOST, PORT), BackendHandler)
    print(f"Backend running on http://{HOST}:{PORT}")
    print("Endpoints:")
    print("  GET  /health")
    print("  POST /api/echo")
    print("  POST /api/sitrep")
    server.serve_forever()


if __name__ == "__main__":
    run()
