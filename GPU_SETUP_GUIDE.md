# 🎮 GPU Acceleration Setup Guide (RTX 3050)

## Overview
Panduan lengkap untuk mengaktifkan GPU acceleration pada RTX 3050 Anda untuk mempercepat semua proses voice conversion (Demucs, RVC, TTS).

---

## 🚀 Quick Start (5 menit)

### Step 1: Install CUDA Toolkit & cuDNN
```bash
# Windows: Download CUDA 12.1
https://developer.nvidia.com/cuda-12-1-0-download-wizard

# During installation:
# ✓ Pilih CUDA Toolkit
# ✓ Pilih cuDNN (jika tersedia)
# ✓ Add to PATH
```

### Step 2: Install PyTorch with CUDA
```bash
# Run dari terminal dalam project folder:
.\setup_gpu.bat
```

### Step 3: Verify CUDA
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0))"
```

Expected output:
```
CUDA Available: True
Device: NVIDIA GeForce RTX 3050
```

✅ GPU Ready!

---

## 📊 Performance Comparison

### Processing Time (per 3-minute song)

| Task | GPU (RTX 3050) | CPU (Ryzen) | Speedup |
|------|---|---|---|
| **Download (yt-dlp)** | ~1-2 min | ~1-2 min | 1x |
| **Separate (Demucs)** | 45 sec | 3-4 min | 4-5x ⚡ |
| **Convert (RVC)** | 1-2 min | 5-10 min | 5x ⚡ |
| **Merge (FFmpeg)** | 15 sec | 20 sec | 1.3x |
| **TOTAL** | **~3-5 min** | **~10-15 min** | **3-4x** ⚡ |

---

## ⚙️ Configuration

### Enable GPU (Default)
Edit `config.py`:
```python
enable_gpu_acceleration = True  # GPU enabled
gpu_device = "cuda"  # Use NVIDIA GPU
```

### Force CPU (Fallback)
```python
enable_gpu_acceleration = False  # CPU only
gpu_device = "cpu"
```

---

## 📦 Dependencies with GPU Support

### 1. PyTorch + CUDA
```bash
# Via setup_gpu.bat (recommended)
.\setup_gpu.bat

# Or manual:
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 2. Demucs (with GPU)
```bash
pip install demucs
# Already installed if you followed setup_gpu.bat
```

### 3. RVC (Voice Conversion)
```bash
# Option A: RVC CLI (recommended for beginners)
pip install rvc-python

# Option B: RVC WebUI (for training)
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
python infer-web.py
```

### 4. Other Dependencies
```bash
pip install yt-dlp librosa soundfile numpy
```

---

## 📂 RVC Model Setup

### 1. Download Pre-trained Model

**Option A: Anime/VTuber Models (Recommended)**
```
Source: https://huggingface.co/lj1995/VoiceConversionModels
Model: Any anime/kawaii voice model (~200MB-2GB)
```

**Option B: Open Voice Model**
```
Source: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/releases
Download latest model files
```

### 2. Place Model in Project

```
Project Root/
├── models/
│   ├── atri_rvc_model.pth  ← Main model file
│   └── atri_rvc_index.index  ← Optional index file
├── config.py  ← Already configured to use this path
└── ...
```

### 3. Verify Model Path

Edit `config.py`:
```python
rvc_model_path = "models/atri_rvc_model.pth"
rvc_index_path = "models/atri_rvc_index.index"  # Optional
```

Test:
```bash
python -c "
import os
model_path = 'models/atri_rvc_model.pth'
if os.path.exists(model_path):
    print(f'✓ Model found: {model_path}')
else:
    print(f'✗ Model NOT found: {model_path}')
"
```

---

## 🎤 Voice Conversion Parameters

### Quick Tuning
Edit `config.py`:

```python
# Pitch shift (-12 to 12)
rvc_f0_up_key = 0  # 0=original, positive=higher, negative=lower

# Voice smoothing (0-10)
rvc_filter_radius = 3  # Higher = smoother but might sound artificial

# Vocal loudness (0-1)
rvc_rms_mix_rate = 0.25  # Lower = quieter vocals, higher = louder

# Consonant protection (0-1)
rvc_protect = 0.33  # Higher = preserve voiceless sounds better
```

### Recommended Presets

**Anime/Cute Voice:**
```python
rvc_f0_up_key = 3  # Slightly higher pitched
rvc_filter_radius = 5  # Smooth and blended
rvc_rms_mix_rate = 0.2  # Soft vocals
rvc_protect = 0.5  # Better consonants
```

**Deep/Strong Voice:**
```python
rvc_f0_up_key = -2  # Slightly lower pitched
rvc_filter_radius = 2  # More natural
rvc_rms_mix_rate = 0.35  # Prominent vocals
rvc_protect = 0.2  # Less protection (more character)
```

**Neutral/Natural:**
```python
rvc_f0_up_key = 0  # Original pitch
rvc_filter_radius = 3  # Balanced
rvc_rms_mix_rate = 0.25  # Default
rvc_protect = 0.33  # Balanced
```

---

## 🔧 Advanced GPU Optimization

### Monitor GPU Usage
```bash
# Windows PowerShell
while($true) { nvidia-smi; Start-Sleep -Seconds 2; Clear-Host }

# Linux / Mac
watch -n 2 nvidia-smi
```

### Memory Management
If RTX 3050 runs out of memory (8GB):

1. Reduce batch size in RVC parameters
2. Close other GPU applications
3. Use CPU fallback:
   ```python
   enable_gpu_acceleration = False
   ```

### Advanced Settings for Discord Bot
In `utils/voice_conversion.py`:

```python
# Change these if experiencing issues
CUDA_AVAILABLE = True  # Set to False to disable CUDA
GPU_DEVICE = "cuda:0"  # Use first GPU
```

---

## 🐛 Troubleshooting

### Error: "CUDA not available"
```bash
# Solution 1: Install CUDA Toolkit 12.1
# https://developer.nvidia.com/cuda-12-1-0-download-wizard

# Solution 2: Check if PyTorch recognizes GPU
python -c "import torch; print(torch.cuda.is_available())"

# Solution 3: Update NVIDIA drivers
# https://www.nvidia.com/Download/driverDetails.aspx
```

### Error: "Out of memory" (CUDA OOM)
```python
# config.py - Fall back to CPU
enable_gpu_acceleration = False
gpu_device = "cpu"
```

### Error: "Demucs not found"
```bash
pip install demucs --upgrade
```

### Error: "RVC model not found"
```
1. Check file exists: models/atri_rvc_model.pth
2. Check path in config.py is correct
3. Download model from: https://huggingface.co/lj1995/VoiceConversionModels
```

### Slow Processing Despite GPU Enabled
```bash
# Check GPU utilization
nvidia-smi

# If low usage:
# 1. Restart Discord bot
# 2. Check model size (too large?)
# 3. Force GPU: enable_gpu_acceleration = True in config.py
# 4. Check other apps using GPU
```

---

## 📚 Resources

- **PyTorch Installation**: https://pytorch.org/get-started/locally/
- **CUDA Toolkit**: https://developer.nvidia.com/cuda-12-1-0-download-wizard
- **Demucs**: https://github.com/facebookresearch/demucs
- **RVC GitHub**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **RVC Models**: https://huggingface.co/lj1995/VoiceConversionModels
- **NVIDIA Driver**: https://www.nvidia.com/Download/driverDetails.aspx

---

## 🎯 Testing GPU Performance

### Run Full Pipeline Test
```bash
# This will test download → separate → convert → merge
python -c "
from utils.voice_conversion import process_cover_full
import time

start = time.time()
result = process_cover_full('https://youtu.be/dQw4w9WgXcQ')  # Example video
end = time.time()

print(f'Total time: {end - start:.1f} seconds')
print(f'Result: {result}')
"
```

---

## 💡 Tips

✅ Keep `enable_gpu_acceleration = True` in config.py
✅ Monitor `nvidia-smi` during first run to verify GPU is being used
✅ RVC quality depends heavily on model - download a good quality model
✅ For best results, use models trained on similar voice type
✅ Consider downloading multiple models for different voice styles
✅ Update NVIDIA drivers monthly for best performance

---

**Last Updated**: June 2026
**Target GPU**: NVIDIA RTX 3050 (8GB VRAM)
**Status**: ✅ Fully Optimized
