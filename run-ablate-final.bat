@echo off
set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa

echo ============================================================
echo  Qwen2.5-7B-Instruct Abliteration (from local cache)
echo  Started: %DATE% %TIME%
echo ============================================================

set MODEL_PATH=C:\Users\dabsa\.cache\huggingface\models--Qwen--Qwen2.5-7B-Instruct\snapshots\a09a35458c702b33eeacc393d103063234e8bc28

python -m obliteratus obliterate "%MODEL_PATH%" --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-research --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-final.log 2>&1

echo Exit code: %ERRORLEVEL%
echo Finished: %TIME%
echo ============================================================
