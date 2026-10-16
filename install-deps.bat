
cd C:\Users\dabsa
echo Starting pip install at %DATE% %TIME% > install-pip.log

REM Uninstall CPU torch first
pip uninstall -y torch torchvision torchaudio 2>&1 >> install-pip.log

REM Install CUDA 12.8 torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 2>&1 >> install-pip.log
echo. >> install-pip.log
echo Torch CUDA install done at %DATE% %TIME% >> install-pip.log

REM Install vllm, transformers, accelerate, bitsandbytes
pip install vllm transformers accelerate bitsandbytes safetensors huggingface-hub 2>&1 >> install-pip.log
echo. >> install-pip.log
echo ML libs install done at %DATE% %TIME% >> install-pip.log

REM Install obliteratus
git clone https://github.com/elder-plinius/OBLITERATUS.git 2>&1 >> install-pip.log
cd OBLITERATUS
pip install -e . 2>&1 >> install-pip.log
echo. >> install-pip.log
echo Obliteratus install done at %DATE% %TIME% >> install-pip.log

echo All done at %DATE% %TIME% >> install-pip.log
