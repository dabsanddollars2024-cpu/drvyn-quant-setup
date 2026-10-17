@echo off
set OBLITERATUS_PHASE_ADMISSION=loose
cd C:\Users\dabsa
python -m obliteratus obliterate Qwen/Qwen2.5-Coder-7B-Instruct --method advanced --quantization 4bit --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-coder --dtype bfloat16 --gpu-memory-utilization 0.6 > C:\Users\dabsa\ablate3.log 2>&1
