#!/usr/bin/env python3
"""
Diagnostic Tool untuk Check AI Cover Setup
Verify: yt-dlp, ffmpeg, RVC CLI, dan integration
"""

import subprocess
import os
import sys

def check_command_exists(cmd, version_flag="--version"):
    """Check jika command tersedia di PATH"""
    try:
        result = subprocess.run([cmd, version_flag], capture_output=True, timeout=5)
        return result.returncode == 0, result.stdout.decode().split('\n')[0] if result.stdout else ""
    except:
        return False, ""

def main():
    print("\n" + "="*60)
    print("  AI COVER LAGU - DEPENDENCY CHECK")
    print("="*60)
    
    # Check 1: yt-dlp
    print("\n[CHECK 1] yt-dlp (Download audio dari YouTube/URL)")
    print("-" * 60)
    exists, version = check_command_exists("yt-dlp")
    if exists:
        print(f"✓ INSTALLED: {version}")
    else:
        print("✗ NOT FOUND")
        print("  Install: pip install yt-dlp")
        print("  Or:      pip install --upgrade yt-dlp")
    
    # Check 2: FFmpeg
    print("\n[CHECK 2] ffmpeg (Audio processing & mixing)")
    print("-" * 60)
    exists, version = check_command_exists("ffmpeg", "-version")
    if exists:
        print(f"✓ INSTALLED: {version}")
    else:
        print("✗ NOT FOUND")
        print("  Windows: Download dari https://ffmpeg.org/download.html")
        print("  Linux:   sudo apt install ffmpeg")
        print("  macOS:   brew install ffmpeg")
        print("  Then add to PATH!")
    
    # Check 3: Demucs (Vocal Separation)
    print("\n[CHECK 3] demucs (Vocal & Instrumental Separation)")
    print("-" * 60)
    exists, version = check_command_exists("demucs")
    if exists:
        print(f"✓ INSTALLED: {version}")
    else:
        print("✗ NOT FOUND")
        print("  Install: pip install demucs")
    
    # Check 4: RVC CLI (Voice Conversion)
    print("\n[CHECK 4] rvc (Retrieval-based Voice Conversion)")
    print("-" * 60)
    try:
        result = subprocess.run([sys.executable, "-m", "rvc.infer", "--help"], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✓ INSTALLED: RVC CLI module available")
        else:
            print("✗ RVC CLI not properly installed")
            print("  Install: pip install rvc-python")
    except:
        print("✗ RVC CLI NOT FOUND")
        print("  Install: pip install rvc-python")
    
    # Check 5: RVC Model File
    print("\n[CHECK 5] RVC Model File (.pth)")
    print("-" * 60)
    model_paths = [
        "models/atri_rvc_model.pth",
        "./models/atri_rvc_model.pth",
        "E:\\New\\AI-Waifu-Vtuber-master\\models\\atri_rvc_model.pth",
    ]
    
    found = False
    for path in model_paths:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"✓ FOUND: {path} ({size_mb:.1f}MB)")
            found = True
            break
    
    if not found:
        print("✗ NOT FOUND")
        print("  Download dari: https://huggingface.co/lj1995/VoiceConversionModels")
        print("  Place at:      models/atri_rvc_model.pth")
    
    # Check 6: Python Packages
    print("\n[CHECK 6] Python Packages")
    print("-" * 60)
    packages = {
        "torch": "GPU acceleration",
        "librosa": "Audio processing",
        "soundfile": "Audio I/O",
        "numpy": "Numerical arrays",
    }
    
    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:15} - {desc}")
        except:
            print(f"✗ {pkg:15} - {desc} (install: pip install {pkg})")
    
    # Check 7: Discord.py Voice
    print("\n[CHECK 7] Discord.py Voice Support")
    print("-" * 60)
    try:
        import discord
        from discord.ext import voice_recv
        print(f"✓ discord.py {discord.__version__}")
        print(f"✓ voice_recv available")
    except ImportError as e:
        print(f"✗ Error: {e}")
        print("  Install: pip install discord-py-interactions discord-ext-voice-recv")
    
    # Summary & Recommendations
    print("\n" + "="*60)
    print("  RECOMMENDATIONS")
    print("="*60)
    
    print("""
UNTUK FULL AI COVER (dengan vokal + instrumen):

1. Setup Minimal (Quick):
   - pip install yt-dlp demucs rvc-python librosa soundfile
   - Download RVC model ke models/atri_rvc_model.pth
   - Pastikan ffmpeg di PATH
   
2. Test Command di Discord:
   _atri cover_advanced https://youtu.be/xxx
   (ini akan: download → separate → convert → merge)
   
3. Alternative (Fast TTS):
   _atri cover Nama Lagu
   (hanya generate parody lyrics dengan TTS - datar tapi cepat)

UNTUK GPU ACCELERATION:
   .\setup_gpu.bat
   (ini optimize PyTorch untuk RTX 3050)
""")
    
    print("="*60)

if __name__ == "__main__":
    main()
