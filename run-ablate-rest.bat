@echo off
echo ============================================================
echo  DRVYN Quant Lab LLM Abliteration Queue - RETRY 2
echo  Started: %DATE% %TIME%
echo ============================================================

set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa

echo.
echo ============================================================
echo  Model 3/4: DeepSeek-R1-Distill-Qwen-7B (CPU device, surgical)
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --method surgical --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-deepseek-r1 --dtype float16 --device cpu --gate-mode off --max-perplexity-increase 30 > C:\Users\dabsa\ablate-deepseek3.log 2>&1
echo  DeepSeek exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  Model 4/4: NousResearch Llama 3.1-8B (CPU device)
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate NousResearch/Meta-Llama-3.1-8B-Instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-llama31 --dtype float16 --device cpu > C:\Users\dabsa\ablate-llama3.log 2>&1
echo  Llama exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  ALL DONE: %DATE% %TIME%
echo ============================================================
