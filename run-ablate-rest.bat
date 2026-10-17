@echo off
echo ============================================================
echo  DRVYN Quant Lab LLM Abliteration Queue
echo  Started: %DATE% %TIME%
echo ============================================================

set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa

echo.
echo ============================================================
echo  Model 3/4: DeepSeek-R1-Distill-Qwen-7B
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-deepseek-r1 --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-deepseek.log 2>&1
echo  DeepSeek exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  Model 4/4: Llama 3.1-8B-Instruct
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-llama31 --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-llama.log 2>&1
echo  Llama exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  ALL DONE: %DATE% %TIME%
echo ============================================================
