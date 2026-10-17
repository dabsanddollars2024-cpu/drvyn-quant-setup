@echo off
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set OBLITERATUS_PHASE_ADMISSION=off

echo ============================================================
echo  Starting vLLM server with abliterated Qwen2.5-7B-Instruct
echo  Port: 8001
echo  Started: %DATE% %TIME%
echo ============================================================

cd C:\Users\dabsa

python -m vllm.entrypoints.openai.api_server ^
  --model C:\Users\dabsa\quant-lab-llms\models\abliterated-qwen-research ^
  --port 8001 ^
  --served-model-name qwen-research ^
  --quantization bitsandbytes ^
  --load-format bitsandbytes ^
  --max-model-len 8192 ^
  --gpu-memory-utilization 0.9 ^
  --dtype bfloat16 ^
  --trust-remote-code

echo.
echo Server stopped: %DATE% %TIME%
