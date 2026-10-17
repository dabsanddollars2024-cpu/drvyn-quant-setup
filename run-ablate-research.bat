@echo off
echo ============================================================
echo  Qwen2.5-7B-Instruct Abliteration (Research model)
echo  Started: %DATE% %TIME%
echo ============================================================

set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa

echo.
echo Loading model and abliterating...
python -m obliteratus obliterate Qwen/Qwen2.5-7B-Instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-research --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-research.log 2>&1
echo  Exit code: %ERRORLEVEL%
echo  Finished: %TIME%
echo ============================================================
