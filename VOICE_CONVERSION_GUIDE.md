# 🎤 Advanced Voice Conversion Cover Guide

## Fitur
Bot bisa membuat cover lagu dengan suara **Atri** menggunakan teknologi RVC (Retrieval-based Voice Conversion)!

```
User: "_atri cover_advanced https://youtu.be/xxxxx"
  ↓
[1] Download audio via yt-dlp
[2] Pisahkan vokal & instrumen via Demucs
[3] Konversi vokal ke suara Atri via RVC
[4] Gabungkan hasil akhir via FFmpeg
  ↓
Bot: Kirim audio hasil cover ke Discord
```

---

## Installation

### 1. Install Dependencies

```bash
pip install yt-dlp demucs
```

### 2. Setup RVC Model

#### Option A: Menggunakan Pre-trained Model
```bash
mkdir models
# Download pre-trained RVC model untuk Atri
# Contoh: https://huggingface.co/lj1995/VoiceConversionModels/resolve/main/...

# Letakkan di: models/atri_rvc_model.pth
```

#### Option B: Training Custom RVC Model
```bash
# Clone RVC repository
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Ikuti instruksi training di repo
python infer-web.py
```

### 3. FFmpeg
- **Windows**: Download dari https://ffmpeg.org/download.html
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

---

## Usage

### Commands

```
# RVC Voice Conversion Cover
_atri cover_advanced https://youtu.be/xxxxx
_atri cover_rvc https://youtu.be/xxxxx
_atri rvc https://youtu.be/xxxxx

# Simple Parody Cover (TTS, lebih cepat)
_atri cover Nama Lagu
_atri sing Nama Lagu
```

### Example

```
_atri cover_advanced https://youtu.be/dQw4w9WgXcQ
```

Output:
- Bot downloads lagu dari YouTube
- Pisahkan vokal dan backing track
- Ubah suara vokal menjadi suara Atri
- Gabung dan kirim hasil ke Discord

---

## Supported Sources

✅ YouTube (`youtu.be`, `youtube.com`)
✅ SoundCloud
✅ Spotify (via proxy)
✅ Direct file links

---

## Performance

| Step | Time | Hardware |
|------|------|----------|
| Download | 1-5 min | Network dependent |
| Separation | 1-2 min | GPU recommended |
| RVC Convert | 2-5 min | GPU: 1-2 min, CPU: 5-10 min |
| Merge | 30 sec | Fast |
| **Total** | **5-15 min** | - |

> **Tip**: GPU significantly speeds up process. Install PyTorch with CUDA for faster processing.

---

## Troubleshooting

### Error: "yt-dlp tidak terinstall"
```bash
pip install yt-dlp
```

### Error: "Demucs tidak terinstall"
```bash
pip install demucs
```

### Error: "FFmpeg tidak terinstall"
- Download dari: https://ffmpeg.org/download.html
- Pastikan di PATH atau set path di config

### Error: "RVC Model tidak ditemukan"
```
Letakkan model di: models/atri_rvc_model.pth
```

### Slow Processing
- Gunakan GPU: Install `torch` dengan CUDA support
- Reduce quality: Adjust parameters di voice_conversion.py

---

## Advanced Options

### Modify RVC Parameters

Edit dalam `handle_cover_advanced_command()`:

```python
# f0_up_key: Pitch shift (-12 to 12)
f0_up_key=0,  # 0 = original, 12 = +1 octave

# filter_radius: Smoothing (0-10)
filter_radius=3,

# rms_mix_rate: Vocal loudness (0-1)
rms_mix_rate=0.25,
```

### Custom Model Path

```python
rvc_model_path = "path/to/custom_model.pth"
```

---

## Resources

- **RVC Project**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **Demucs**: https://github.com/facebookresearch/demucs
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Pre-trained Models**: https://huggingface.co/lj1995/VoiceConversionModels

---

## Limitations

⚠️ **Processing Time**: 5-15 menit per lagu (CPU), 5-10 menit (GPU)
⚠️ **Quality**: Bergantung pada RVC model quality
⚠️ **Separation**: Tidak perfect untuk semua lagu jenis
⚠️ **File Size**: Max 25MB untuk Discord upload

---

## License & Credits

- RVC: MIT License by lj1995
- Demucs: Creative Commons License by Meta
- yt-dlp: Public Domain
