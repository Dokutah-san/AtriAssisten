# 🎤 AI Cover Lagu - Comprehensive Implementation Guide

## 📊 Comparison: 2 Mode Cover

### Mode 1: SIMPLE PARODY (TTS-based)
```
Command: _atri cover Jangan Pergi Dulu
```

**Process:**
```
User input → Generate parody lyrics → TTS synthesis → Send audio
```

**Karakteristik:**
- ✓ Cepat (30 detik - 1 menit)
- ✓ Bahasa Indonesia yang good
- ✗ Suara datar (text-to-speech, no melody)
- ✗ Tanpa musik instrumental
- ✓ Tidak butuh dependencies (kecuali TTS engine)

**Teknologi:**
- Voicevox: Neural TTS (200+ voices, high quality)
- Silero TTS: Lightweight, offline

**Use Case:**
- Parodi cepat
- Testing/demo
- Fun banter di Discord

---

### Mode 2: ADVANCED AI COVER (RVC-based)
```
Command: _atri cover_advanced https://youtu.be/xxxxxx
Command: _atri cover_rvc https://youtu.be/xxxxxx
```

**Process:**
```
Download → Separate (Demucs) → Convert (RVC) → Merge (FFmpeg) → Send
```

**Karakteristik:**
- ✗ Lambat (3-5 menit per lagu)
- ✓ Musik instrumental original (terpisah)
- ✓ Vokal dengan Atri's voice character (RVC)
- ✓ Full melody dan musik preserved
- ✓ Professional quality cover
- ✗ Butuh RVC model file (~2GB)

**Teknologi:**
- yt-dlp: Download audio dari YouTube
- Demucs: Vocal & instrumental separation
- RVC (Retrieval-based Voice Conversion): Voice style transfer
- FFmpeg: Audio mixing dan processing

**Use Case:**
- Professional AI cover
- Voice conversion showcase
- Full production quality
- Upload ke YouTube/TikTok

---

## ✅ Setup Checklist untuk Mode 2 (Advanced)

### Step 1: Install Dependencies
```bash
pip install yt-dlp demucs rvc-python librosa soundfile numpy
```

### Step 2: Install FFmpeg
**Windows:**
```
1. Download: https://ffmpeg.org/download.html
2. Extract ke folder (e.g., C:\ffmpeg)
3. Add to PATH:
   - Right-click "This PC" → Properties → Advanced → Environment Variables
   - New PATH entry: C:\ffmpeg\bin
4. Verify: ffmpeg -version (dalam PowerShell baru)
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Step 3: Download RVC Model
**Option A: Pre-trained Anime Voice (Recommended)**
```
URL: https://huggingface.co/lj1995/VoiceConversionModels
Download: Any model dengan suffix .pth
Size: ~200MB - 2GB

Recommended models:
- Any "anime" or "kawaii" voice model
- Look for models dengan ratings/downloads tinggi
```

**Option B: Train Custom Model**
```
(Advanced) Lihat: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
```

### Step 4: Place Model File
```
Project structure:
E:\New\AI-Waifu-Vtuber-master\
├── models\
│   └── atri_rvc_model.pth  ← RVC model harus di sini!
├── utils\
├── config.py
└── ...
```

### Step 5: Verify Setup
```bash
# Check all dependencies
python check_cover_setup.py

# Expected output: All checks PASS ✓
```

---

## 🎯 Command Usage

### Simple Cover (Mode 1)
```
_atri cover Jangan Pergi Dulu
_atri sing Bohemian Rhapsody
_atri nyanyi Lagu Favorit
```

**Output:**
- Parody lyrics dalam Bahasa Indonesia
- TTS audio file (voice only, no music)
- Sent to Discord as .wav file

---

### Advanced Cover (Mode 2)
```
_atri cover_advanced https://youtu.be/dQw4w9WgXcQ
_atri cover_rvc https://www.youtube.com/watch?v=xxxx
_atri rvc https://youtu.be/xxxx
```

**Process:**
1. Download audio dari URL (1-2 menit)
2. Separate vocals & instrumental (1-2 menit)
3. Convert vokal ke Atri's voice (2-3 menit)
4. Merge hasil akhir (30 detik)
5. Send to Discord

**Output:**
- Full AI cover dengan vokal + instrumen
- Original melodi dan musik preserved
- Vokal dengan Atri's voice character
- Professional quality audio

---

## 🔍 Diagnostics

### Check Dependencies Status
```bash
python check_cover_setup.py
```

Output akan show:
```
[CHECK 1] yt-dlp
✓ INSTALLED: yt-dlp 2024.06.01

[CHECK 2] ffmpeg
✓ INSTALLED: ffmpeg version 6.0

[CHECK 3] demucs
✓ INSTALLED: demucs 4.0.1

[CHECK 4] rvc
✓ INSTALLED: RVC CLI module available

[CHECK 5] RVC Model File (.pth)
✓ FOUND: models/atri_rvc_model.pth (262.3MB)

[CHECK 6] Python Packages
✓ torch - GPU acceleration
✓ librosa - Audio processing
✓ soundfile - Audio I/O
✓ numpy - Numerical arrays
```

### Test Individual Components
```bash
# Test yt-dlp
yt-dlp --version

# Test FFmpeg
ffmpeg -version

# Test Demucs
demucs --help

# Test Python imports
python -c "import torch, librosa, soundfile; print('✓ All packages OK')"
```

---

## ⚙️ Configuration (config.py)

```python
# Voice separation engine
voice_separation_engine = "demucs"  # or "uvr"

# RVC settings
rvc_model_path = "models/atri_rvc_model.pth"
rvc_f0_up_key = 0  # Pitch shift (-12 to 12)
rvc_filter_radius = 3  # Voice smoothing (0-10)
rvc_rms_mix_rate = 0.25  # Vocal loudness (0-1)
rvc_protect = 0.33  # Consonant protection (0-1)

# GPU acceleration
enable_gpu_acceleration = True
gpu_device = "cuda"  # or "cpu"
```

---

## 🚀 Recommended Workflow

### Untuk Testing/Demo:
```
1. Use Simple Cover (_atri cover ...)
2. Fast feedback (30 sec)
3. Good for banter
```

### Untuk Production/Upload:
```
1. Use Advanced Cover (_atri cover_advanced URL)
2. Wait 3-5 minutes
3. Get professional quality audio
4. Upload ke YouTube/TikTok
```

---

## 🐛 Troubleshooting

### Error: "yt-dlp not found"
```bash
pip install yt-dlp --upgrade
```

### Error: "ffmpeg not found"
**Windows:** Add to PATH:
1. Download FFmpeg: https://ffmpeg.org/download.html
2. Extract to C:\ffmpeg
3. Add C:\ffmpeg\bin to PATH
4. Restart terminal/IDE

### Error: "RVC model not found"
```
1. Download dari: https://huggingface.co/lj1995/VoiceConversionModels
2. Place at: models/atri_rvc_model.pth
3. Verify: python check_cover_setup.py
```

### Error: "Out of memory" (CUDA OOM)
```python
# config.py
enable_gpu_acceleration = False  # Force CPU
```

### Audio duration too short
This is **EXPECTED** for Simple Cover (TTS mode).
Use Advanced Cover for full duration music.

### Suara datar (no melody)
This is **EXPECTED** for Simple Cover (text-to-speech).
Use Advanced Cover for proper voice conversion with original melody.

---

## 📊 Performance Expectations

### Simple Cover (Mode 1)
| Metric | Value |
|--------|-------|
| Duration | 30 sec - 1 min |
| Processing Time | ~10 seconds |
| Quality | Parody/fun |
| Dependencies | TTS engine only |

### Advanced Cover (Mode 2)
| Metric | Value |
|--------|-------|
| Duration | 2-4 min (full song) |
| Processing Time | 3-5 min (CPU) / 2-3 min (GPU) |
| Quality | Professional |
| Dependencies | yt-dlp, Demucs, RVC, FFmpeg |

---

## 🎓 Advanced Topics

### Custom RVC Parameters
```python
# In config.py

# Pitch shift untuk higher/lower voice
rvc_f0_up_key = 3  # Naik 1.5 octave (lebih tinggi)
rvc_f0_up_key = -2  # Turun untuk deeper voice

# Voice smoothing (higher = smoother)
rvc_filter_radius = 5  # Lebih smooth
rvc_filter_radius = 1  # Lebih natural/rough

# Vocal loudness
rvc_rms_mix_rate = 0.15  # Vokal lebih soft
rvc_rms_mix_rate = 0.35  # Vokal lebih prominent
```

### Using Different RVC Models
```python
# config.py
rvc_model_path = "models/different_voice.pth"
# Just swap model file, rest akan handle otomatis
```

### GPU Optimization
```bash
# For RTX 3050:
.\setup_gpu.bat

# Check GPU usage:
nvidia-smi -l 1  # Update per second
```

---

## 📚 Resources

- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Demucs**: https://github.com/facebookresearch/demucs
- **RVC**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **RVC Models**: https://huggingface.co/lj1995/VoiceConversionModels
- **FFmpeg**: https://ffmpeg.org/download.html

---

## ✨ Summary

**If you want:** Fast parody with TTS
→ Use `_atri cover Lagu`

**If you want:** Professional AI cover with full music
→ Use `_atri cover_advanced URL`

**Setup time:**
- Simple: 0 min (already ready)
- Advanced: 30 min (install deps + download model)

**Next:** Run `python check_cover_setup.py` to verify your setup! 🚀
