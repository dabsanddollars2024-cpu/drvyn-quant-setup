@echo off
set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa
python -m obliteratus obliterate Qwen/Qwen2.5-Coder-7B-Instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-coder --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-coder.log 2>&1
