@echo off
echo ============================================================
echo  DRVYN Quant Lab LLM Abliteration Queue - RETRY
echo  Started: %DATE% %TIME%
echo ============================================================

set OBLITERATUS_PHASE_ADMISSION=off
cd C:\Users\dabsa

echo.
echo ============================================================
echo  Model 3/4: DeepSeek-R1-Distill-Qwen-7B (retry with surgical method)
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --method surgical --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-deepseek-r1 --dtype bfloat16 --gpu-memory-utilization 0.9 --gate-mode off --max-perplexity-increase 30 > C:\Users\dabsa\ablate-deepseek2.log 2>&1
echo  DeepSeek exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  Model 4/4: NousResearch Llama 3.1-8B (non-gated mirror)
echo  Started: %TIME%
echo ============================================================
python -m obliteratus obliterate NousResearch/Meta-Llama-3.1-8B-Instruct --method advanced --output-dir C:\Users\dabsa\quant-lab-llms\models\abliterated-llama31 --dtype bfloat16 --gpu-memory-utilization 0.9 > C:\Users\dabsa\ablate-llama2.log 2>&1
echo  Llama exit code: %ERRORLEVEL%
echo  Finished: %TIME%

echo.
echo ============================================================
echo  ALL DONE: %DATE% %TIME%
echo ============================================================
