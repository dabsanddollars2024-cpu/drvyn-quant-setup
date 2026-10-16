
import subprocess
import sys
import time
from pathlib import Path

LOG_FILE = Path(r"C:\Users\dabsa\install-progress.log")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        f.flush()

log("=== STARTING INSTALL ===")

# Step 1: Uninstall CPU torch
log("Step 1: Uninstalling CPU torch...")
r = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"],
                  capture_output=True, text=True, timeout=120)
log(f"  Result: rc={r.returncode}")
if r.stdout.strip():
    log(f"  stdout: {r.stdout[-200:]}")

# Step 2: Install CUDA torch
log("Step 2: Installing CUDA torch (this will take 5-10 min)...")
r = subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio",
                    "--index-url", "https://download.pytorch.org/whl/cu128", "--no-cache-dir"],
                  capture_output=True, text=True, timeout=900)
log(f"  Result: rc={r.returncode}")
if r.returncode == 0:
    log("  Torch installed successfully")
else:
    log(f"  ERROR: {r.stderr[-500:]}")

# Step 3: Install vllm and friends
log("Step 3: Installing vllm + ML libraries...")
r = subprocess.run([sys.executable, "-m", "pip", "install", "vllm", "transformers", "accelerate",
                    "bitsandbytes", "safetensors", "huggingface-hub", "--no-cache-dir"],
                  capture_output=True, text=True, timeout=600)
log(f"  Result: rc={r.returncode}")
if r.returncode == 0:
    log("  ML libs installed")
else:
    log(f"  ERROR: {r.stderr[-500:]}")

# Step 4: Install obliteratus
log("Step 4: Cloning + installing obliteratus...")
oblit_dir = Path(r"C:\Users\dabsa\OBLITERATUS")
if not oblit_dir.exists():
    r = subprocess.run(["git", "clone", "https://github.com/elder-plinius/OBLITERATUS.git",
                       str(oblit_dir)], capture_output=True, text=True, timeout=120)
    log(f"  Clone: rc={r.returncode}")
r = subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(oblit_dir), "--no-cache-dir"],
                  capture_output=True, text=True, timeout=300)
log(f"  Obliteratus install: rc={r.returncode}")
if r.returncode == 0:
    log("  Obliteratus installed")

log("=== ALL DONE ===")
