# VERIFY - Post-Install Checklist

Run these after `install-quant-lab-llms.bat` completes.

## 1. Tools Installed

```cmd
:: Check obliteratus
obliteratus --version
:: Expected: prints version

:: Check vllm
vllm --version
:: Expected: prints version

:: Check Python deps
python -c "import torch, transformers, vllm; print('OK')"
:: Expected: OK
```

## 2. Models Downloaded

```cmd
dir %USERPROFILE%\quant-lab-llms\models
```

Expected output (folder names may vary slightly):
```
abliterated-deepseek-r1
abliterated-llama31
abliterated-phi35
abliterated-qwen-coder
```

Each folder should have 5-10 GB of files (`config.json`, `*.safetensors`, `tokenizer.json`).

## 3. Can Start a Server

```cmd
cd %USERPROFILE%\quant-lab-llms
serve-model.bat qwen-coder
```

Expected:
- vLLM loads model (30-60 sec)
- Prints `Application startup complete`
- Server listening on `http://localhost:8001`

**Leave this terminal open.** In a NEW terminal, run tests:

```cmd
:: Test 1: Server is up
curl http://localhost:8001/v1/models
:: Expected: JSON with model list

:: Test 2: Can generate
curl http://localhost:8001/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"Qwen2.5-Coder-7B-Instruct-abliterated\",\"messages\":[{\"role\":\"user\",\"content\":\"Write hello world in Python\"}],\"max_tokens\":100}"
:: Expected: JSON with "print('hello world')" or similar in choices
```

## 4. All 4 Models Work

Stop the current server (Ctrl+C in its terminal), then test each:

```cmd
:: Fast model (smallest, fastest test)
serve-model.bat phi35
:: In another terminal:
curl http://localhost:8003/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"Phi-3.5-mini-instruct-abliterated\",\"messages\":[{\"role\":\"user\",\"content\":\"What is 2+2?\"}]}"
:: Expected: "4"

:: Repeat for deepseek-r1 (port 8002) and llama31 (port 8004)
```

## 5. Claude Code Integration

If you set up the MCP server in `CLAUDE-CODE-INTEGRATION.md`:

1. Make sure vLLM is running (`serve-model.bat qwen-coder`)
2. In a Claude Code session, type:
   > "Use the local-coder tool to write hello world in Python"
3. Should route to your local model

## 6. Disk Usage Check

```cmd
:: Total install size
powershell -Command "Get-ChildItem -Recurse %USERPROFILE%\quant-lab-llms | Measure-Object -Property Length -Sum | Select-Object @{Name='SizeGB';Expression={[math]::Round($_.Sum / 1GB, 2)}}"
:: Expected: ~25 GB
```

## Common Issues

### "Module not found" errors

```cmd
python -m pip install --upgrade vllm torch transformers accelerate bitsandbytes safetensors huggingface-hub
```

### CUDA out of memory during abliteration

The PC has 16GB VRAM. If abliteration fails:
1. Close all other GPU-using apps (browser, games, etc.)
2. Re-run the installer — it'll skip already-completed models
3. Or abliterate one at a time

### vLLM fails to start

```cmd
:: Check CUDA
nvidia-smi

:: Check vllm install
pip show vllm

:: Test minimal
vllm serve microsoft/Phi-3.5-mini-instruct --port 8003 --max-model-len 1024
```

### Model loads but generates garbage

The abliteration may have damaged coherence. Check:
- Refusal rate (should be ~0%)
- Perplexity (should be within 10% of original)
- Try a different method (`basic` instead of `advanced`)

Re-abliterate with:
```cmd
obliteratus obliterate <model> --method basic --quantization 4bit --output-dir ./retry
```

## If All Else Fails

Message me in Telegram. I can:
1. SSH into the PC from VPS
2. Check the actual error
3. Re-run installer steps manually
4. Debug vLLM / CUDA / model loading

The installer is designed to be resumable — re-running skips completed models.
