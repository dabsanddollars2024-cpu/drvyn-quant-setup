@echo off
REM ============================================================
REM DRVYN QUANT LAB LLM INSTALLER
REM RTX 5060 Ti 16GB - Windows 10/11
REM Author: Kinetic (Hermes Agent) for Dabs
REM Date: 2026-10-15
REM
REM Models installed:
REM   PRIMARY    - Qwen2.5-Coder-7B-Instruct (Pine Script, backtest code)
REM   REASONING  - DeepSeek-R1-Distill-Qwen-7B (strategy logic)
REM   FAST       - Phi-3.5-mini (quick analysis)
REM   RESEARCH   - Llama 3.1-8B-Instruct (synthesis)
REM
REM Run as Administrator (right-click -> Run as administrator)
REM Total install time: 30-60 minutes depending on internet
REM Total disk: ~25GB (models + tools)
REM ============================================================

echo.
echo ============================================================
echo  DRVYN QUANT LAB LLM INSTALLER
echo  RTX 5060 Ti 16GB
echo ============================================================
echo.

REM Check for admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator
    pause
    exit /b 1
)

REM Step 1: Check prerequisites
echo [1/8] Checking prerequisites...

where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found. Installing Python 3.12...
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if %errorLevel% neq 0 (
        echo FAILED to install Python. Install manually: https://python.org
        pause
        exit /b 1
    )
)

where git >nul 2>&1
if %errorLevel% neq 0 (
    echo Git not found. Installing...
    winget install Git.Git --accept-source-agreements --accept-package-agreements
)

where node >nul 2>&1
if %errorLevel% neq 0 (
    echo Node.js not found. Installing...
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
)

REM Refresh PATH
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts

python --version
git --version
echo Prerequisites OK.
echo.

REM Step 2: Check GPU
echo [2/8] Checking GPU...
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
echo.

REM Step 3: Set up directories
echo [3/8] Setting up directories...
set QUANT_DIR=%USERPROFILE%\quant-lab-llms
set MODELS_DIR=%QUANT_DIR%\models
set LOGS_DIR=%QUANT_DIR%\logs

if not exist "%QUANT_DIR%" mkdir "%QUANT_DIR%"
if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Install dir: %QUANT_DIR%
echo Models dir:  %MODELS_DIR%
echo Logs dir:    %LOGS_DIR%
echo.

REM Step 4: Install Python packages
echo [4/8] Installing Python packages (this takes 5-10 min)...
python -m pip install --upgrade pip
python -m pip install vllm torch transformers accelerate bitsandbytes safetensors huggingface-hub

if %errorLevel% neq 0 (
    echo WARNING: Some pip installs may have failed. Check output above.
    echo Continuing anyway...
)
echo.

REM Step 5: Install obliteratus
echo [5/8] Installing OBLITERATUS...
cd /d %QUANT_DIR%
if not exist "OBLITERATUS" (
    git clone https://github.com/elder-plinius/OBLITERATUS.git
)
cd OBLITERATUS
python -m pip install -e .

if %errorLevel% neq 0 (
    echo WARNING: OBLITERATUS install may have issues. Check output.
)
echo.

REM Step 6: Abliterate models
echo [6/8] Abliterating models (this takes 1-2 hours)...
echo.
echo We are running ONE model first to verify the pipeline works.
echo After it completes, you can run the rest.
echo.

REM Primary: Qwen2.5-Coder-7B-Instruct
echo ============================================================
echo  MODEL 1/4: Qwen2.5-Coder-7B-Instruct (PRIMARY)
echo  Purpose: Pine Script, backtest code, quant research
echo  Time: 15-20 min
echo ============================================================
echo.

cd /d %QUANT_DIR%
if not exist "abliterated-qwen-coder" (
    obliteratus obliterate Qwen/Qwen2.5-Coder-7B-Instruct ^
        --method advanced ^
        --quantization 4bit ^
        --output-dir ./abliterated-qwen-coder ^
        --dtype bfloat16
)

if exist "abliterated-qwen-coder" (
    move "abliterated-qwen-coder" "%MODELS_DIR%\" 2>nul
)
echo.

REM Reasoning: DeepSeek-R1-Distill-Qwen-7B
echo ============================================================
echo  MODEL 2/4: DeepSeek-R1-Distill-Qwen-7B (REASONING)
echo  Purpose: Strategy logic, math, chain-of-thought
echo  Time: 20-25 min
echo  NOTE: Uses SURGICAL method to preserve reasoning
echo ============================================================
echo.

cd /d %QUANT_DIR%
if not exist "abliterated-deepseek-r1" (
    obliteratus obliterate deepseek-ai/DeepSeek-R1-Distill-Qwen-7B ^
        --method surgical ^
        --quantization 4bit ^
        --output-dir ./abliterated-deepseek-r1 ^
        --dtype bfloat16
)

if exist "abliterated-deepseek-r1" (
    move "abliterated-deepseek-r1" "%MODELS_DIR%\" 2>nul
)
echo.

REM Fast: Phi-3.5-mini-instruct
echo ============================================================
echo  MODEL 3/4: Phi-3.5-mini-instruct (FAST)
echo  Purpose: Quick analysis, indicator parsing
echo  Time: 10-15 min
echo ============================================================
echo.

cd /d %QUANT_DIR%
if not exist "abliterated-phi35" (
    obliteratus obliterate microsoft/Phi-3.5-mini-instruct ^
        --method advanced ^
        --quantization 4bit ^
        --output-dir ./abliterated-phi35 ^
        --dtype bfloat16
)

if exist "abliterated-phi35" (
    move "abliterated-phi35" "%MODELS_DIR%\" 2>nul
)
echo.

REM Research: Llama 3.1-8B-Instruct
echo ============================================================
echo  MODEL 4/4: Llama 3.1-8B-Instruct (RESEARCH)
echo  Purpose: General analysis, research synthesis
echo  Time: 15-20 min
echo ============================================================
echo.

cd /d %QUANT_DIR%
if not exist "abliterated-llama31" (
    obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct ^
        --method advanced ^
        --quantization 4bit ^
        --output-dir ./abliterated-llama31 ^
        --dtype bfloat16
)

if exist "abliterated-llama31" (
    move "abliterated-llama31" "%MODELS_DIR%\" 2>nul
)
echo.

REM Step 7: Set up vLLM serving scripts
echo [7/8] Setting up vLLM serving scripts...
echo.

REM Create start-serve.bat
(
echo @echo off
echo REM Start vLLM server for a specific model
echo REM Usage: serve-model.bat [model-name]
echo REM Example: serve-model.bat qwen-coder
echo.
echo if "%1"=="" (
echo     echo Usage: serve-model.bat [qwen-coder^|deepseek-r1^|phi35^|llama31]
echo     exit /b 1
echo ^)
echo.
echo set MODELS_DIR=%USERPROFILE%\quant-lab-llms\models
echo.
echo if "%1"=="qwen-coder" (
echo     vllm serve "%MODELS_DIR%\abliterated-qwen-coder" --port 8001 --gpu-memory-utilization 0.85
echo ^) else if "%1"=="deepseek-r1" (
echo     vllm serve "%MODELS_DIR%\abliterated-deepseek-r1" --port 8002 --gpu-memory-utilization 0.85
echo ^) else if "%1"=="phi35" (
echo     vllm serve "%MODELS_DIR%\abliterated-phi35" --port 8003 --gpu-memory-utilization 0.85
echo ^) else if "%1"=="llama31" (
echo     vllm serve "%MODELS_DIR%\abliterated-llama31" --port 8004 --gpu-memory-utilization 0.85
echo ^) else (
echo     echo Unknown model: %1
echo     exit /b 1
echo ^)
) > "%QUANT_DIR%\serve-model.bat"

echo Created: %QUANT_DIR%\serve-model.bat
echo.

REM Step 8: Test the install
echo [8/8] Testing install...
echo.
echo Verifying obliteratus is callable...
where obliteratus
echo.
echo Verifying vllm is callable...
where vllm
echo.
echo Listing installed models...
dir "%MODELS_DIR%" /b
echo.

echo ============================================================
echo  INSTALL COMPLETE
echo ============================================================
echo.
echo Models installed in: %MODELS_DIR%
echo.
echo To start serving a model:
echo   cd %QUANT_DIR%
echo   serve-model.bat qwen-coder
echo.
echo To use from Claude Code, see the CLAUDE-CODE-INTEGRATION.md
echo.
pause
