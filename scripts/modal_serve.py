"""OpenAI-compatible vLLM endpoint on Modal for the base/successor models (replaces starter's scaffold, which pins
vllm 0.6.6, has no weight cache, no concurrency and an open endpoint). Deploy once; it idles to zero after 5 min.

  # one-time, by YOU (the key stays out of chat/logs):
  modal secret create modal-serve MODAL_SERVE_API_KEY=<any long random string>
  # per model:
  MODAL_SERVE_MODEL=openai/gpt-oss-20b MODAL_SERVE_GPU=A100-40GB uv run python -m modal deploy scripts/modal_serve.py
  # stop it:  uv run python -m modal app stop cartel-serve-<name>

Use: LLM_BASE_URL=<printed url>/v1  LLM_API_KEY=<the key>  and pass the same model id as --model.
The vLLM pin is unverified for every GPU: the first smoke call is the test.
"""
import os
import subprocess

import modal

MODEL = os.environ.get("MODAL_SERVE_MODEL", "openai/gpt-oss-20b")
GPU = os.environ.get("MODAL_SERVE_GPU", "A100-40GB")
VLLM = os.environ.get("MODAL_SERVE_VLLM", "0.11.0")
MAX_PARALLEL = int(os.environ.get("MODAL_SERVE_PARALLEL", "32"))  # concurrent requests per container
MAX_CONTAINERS = int(os.environ.get("MODAL_SERVE_MAX_CONTAINERS", "2"))  # GPUs per model, at most
EXTRA = os.environ.get("MODAL_SERVE_ARGS", "")  # extra vLLM flags, e.g. Mistral: --tokenizer-mode mistral ...
PORT = 8000
NAME = "cartel-serve-" + MODEL.split("/")[-1].lower().replace(".", "-")[:40]

app = modal.App(NAME)
cache = modal.Volume.from_name("hf-cache", create_if_missing=True)  # weights downloaded once, reused
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(f"vllm=={VLLM}", "transformers>=4.55.2,<5", "huggingface_hub[hf_transfer]")  # transformers 5 breaks vllm 0.11 (ERROR_LOG)
    # MODEL must be baked in: the container re-imports this file WITHOUT the deploy-time shell env (ERROR_LOG)
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache", "MODAL_SERVE_MODEL": MODEL, "MODAL_SERVE_ARGS": EXTRA,
          "MODAL_SERVE_PARALLEL": str(MAX_PARALLEL), "MODAL_SERVE_MAX_CONTAINERS": str(MAX_CONTAINERS)})
)


@app.function(
    image=image,
    gpu=GPU,
    timeout=24 * 3600,
    scaledown_window=300,
    max_containers=MAX_CONTAINERS,  # cost cap: queue requests rather than add GPUs
    secrets=[modal.Secret.from_name("modal-serve")],  # no key -> deploy fails: never expose an open endpoint
    volumes={"/cache": cache},
)
@modal.concurrent(max_inputs=MAX_PARALLEL)
@modal.web_server(port=PORT, startup_timeout=2400)  # 120B first start downloads ~65 GB
def serve():
    key = os.environ["MODAL_SERVE_API_KEY"]
    print(f"serving {MODEL}", flush=True)  # visible in `modal app logs`
    subprocess.Popen(
        [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", MODEL, "--served-model-name", MODEL,
            "--host", "0.0.0.0", "--port", str(PORT),
            "--api-key", key, "--max-model-len", "16384",
            *EXTRA.split(),
        ]
    )
