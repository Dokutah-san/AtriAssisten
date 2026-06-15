@echo off
REM ============================================================
REM GPU Setup untuk RTX 3050 (CUDA 12.1)
REM ============================================================

echo.
echo [GPU Setup] Installing PyTorch dengan CUDA support...
echo.

REM Aktifkan virtual environment
call .venv\Scripts\activate.bat

REM Uninstall PyTorch versi CPU
echo Removing old PyTorch...
pip uninstall -y torch torchaudio torchvision

REM Install PyTorch dengan CUDA 12.1
echo Installing PyTorch with CUDA 12.1 support...
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu121

REM Install GPU-optimized packages
echo Installing GPU-optimized packages...
pip install --upgrade onnxruntime-gpu
pip install librosa

REM Verify installation
echo.
echo [GPU Setup] Verifying CUDA availability...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

echo.
echo [GPU Setup] Setup complete! RTX 3050 is ready to use.
echo.
pause
