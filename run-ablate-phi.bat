@echo off
set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa
python -m obliteratus obliterate microsoft/Phi-3.5-mini-instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-phi35 --dtype bfloat16 --gpu-memory-utilization 0.85 > C:\Users\dabsa\ablate-phi2.log 2>&1
