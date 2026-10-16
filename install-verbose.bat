@echo off
setlocal

REM Redirect everything to a file with FULL path
set LOG=C:\Users\dabsa\install-verbose.log
echo === STARTING INSTALL %DATE% %TIME% > %LOG%

REM Change to a writable location
cd /d C:\Users\dabsa

REM Capture in stages with progress
echo [%TIME%] Uninstalling CPU torch >> %LOG%
pip uninstall -y torch torchvision torchaudio >> %LOG% 2>&1

echo [%TIME%] Installing CUDA torch (2-3GB, 5-10 min) >> %LOG%
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --no-cache-dir >> %LOG% 2>&1

echo [%TIME%] Torch done. Installing vllm and ML libs >> %LOG%
pip install vllm transformers accelerate bitsandbytes safetensors huggingface-hub --no-cache-dir >> %LOG% 2>&1

echo [%TIME%] ML libs done. Installing obliteratus >> %LOG%
if not exist OBLITERATUS (
    git clone https://github.com/elder-plinius/OBLITERATUS.git >> %LOG% 2>&1
)
cd OBLITERATUS
pip install -e . >> %LOG% 2>&1
cd ..

echo [%TIME%] === ALL DONE %DATE% %TIME% >> %LOG%
endlocal
