import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"

from huggingface_hub import snapshot_download
import time

print("Starting download of Qwen2.5-7B-Instruct...")
print("Expected: 15.2 GB, 4 safetensors files")

start = time.time()
try:
    path = snapshot_download(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        cache_dir="C:\\Users\\dabsa\\.cache\\huggingface",
        max_workers=4,
        etag_timeout=30,
        resume_download=True,
    )
    print(f"Downloaded to: {path}")
    print(f"Time: {time.time() - start:.1f}s")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
