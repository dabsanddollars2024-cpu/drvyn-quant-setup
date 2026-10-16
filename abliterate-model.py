import sys
import time
from pathlib import Path
from obliteratus import obliterate

LOG = Path(r"C:\Users\dabsa\ablation-log.txt")
def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        f.flush()
    print(msg)

log("=== Starting abliteration ===")
log("Model: Qwen/Qwen2.5-Coder-7B-Instruct")
log("Method: advanced")
log("Quantization: 4bit")

start = time.time()
try:
    result = obliterate(
        model_name="Qwen/Qwen2.5-Coder-7B-Instruct",
        method="advanced",
        quantization="4bit",
        output_dir=r"C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-coder",
        dtype="bfloat16"
    )
    elapsed = time.time() - start
    log(f"SUCCESS in {elapsed/60:.1f} minutes")
except Exception as e:
    log(f"ERROR: {e}")
    import traceback
    log(traceback.format_exc())
