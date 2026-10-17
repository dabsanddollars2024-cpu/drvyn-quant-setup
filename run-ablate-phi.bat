@echo off
set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa
python -m obliteratus obliterate microsoft/Phi-3.5-mini-instruct --method advanced --quantization 4bit --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-phi35 --dtype bfloat16 --gpu-memory-utilization 0.7 > C:\Users\dabsa\ablate-phi.log 2>&1
