@echo off
set HF_ENDPOINT=https://hf-mirror.com
set HF_XET_HIGH_PERFORMANCE=1
cd C:\Users\dabsa
echo Starting download: %DATE% %TIME% > C:\Users\dabsa\download.log
python C:\Users\dabsa\drvyn-quant-setup\download-qwen.py >> C:\Users\dabsa\download.log 2>&1
echo Done: %DATE% %TIME% >> C:\Users\dabsa\download.log
