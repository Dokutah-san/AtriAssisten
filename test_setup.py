#!/usr/bin/env python3
"""
Test script untuk verify GPU acceleration dan voice conversion setup
Run this to check if everything is configured correctly
"""

import os
import sys

def test_pytorch_cuda():
    """Test if PyTorch CUDA is working"""
    print("\n[TEST 1] PyTorch CUDA Support")
    print("-" * 50)
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print(f"✓ CUDA Available: {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"✓ GPU Count: {device_count}")
            
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_mem = torch.cuda.get_device_properties(i).total_memory / 1e9
                print(f"  GPU {i}: {gpu_name} ({gpu_mem:.1f}GB)")
            
            return True
        else:
            print("✗ CUDA not available - Run: .\\setup_gpu.bat")
            return False
    except ImportError:
        print("✗ PyTorch not installed - Run: pip install torch")
        return False

def test_dependencies():
    """Test if all voice conversion dependencies are available"""
    print("\n[TEST 2] Voice Conversion Dependencies")
    print("-" * 50)
    
    deps = {
        "yt-dlp": "pip install yt-dlp",
        "demucs": "pip install demucs",
        "ffmpeg": "https://ffmpeg.org/download.html",
        "soundfile": "pip install soundfile",
    }
    
    all_good = True
    for dep, install_cmd in deps.items():
        try:
            if dep == "ffmpeg":
                import subprocess
                subprocess.run([dep, "-version"], capture_output=True, timeout=5)
            else:
                __import__(dep.replace("-", "_"))
            print(f"✓ {dep:15} installed")
        except:
            print(f"✗ {dep:15} NOT installed - {install_cmd}")
            all_good = False
    
    return all_good

def test_config():
    """Test if config.py has GPU settings"""
    print("\n[TEST 3] Configuration")
    print("-" * 50)
    
    try:
        from config import (
            enable_gpu_acceleration,
            gpu_device,
            rvc_model_path,
            rvc_f0_up_key,
            voice_separation_engine,
        )
        
        print(f"✓ enable_gpu_acceleration: {enable_gpu_acceleration}")
        print(f"✓ gpu_device: {gpu_device}")
        print(f"✓ voice_separation_engine: {voice_separation_engine}")
        print(f"✓ rvc_f0_up_key: {rvc_f0_up_key}")
        print(f"✓ rvc_model_path: {rvc_model_path}")
        
        # Check if model exists
        if os.path.exists(rvc_model_path):
            size_mb = os.path.getsize(rvc_model_path) / (1024 * 1024)
            print(f"✓ RVC Model exists: {size_mb:.1f}MB")
            return True
        else:
            print(f"✗ RVC Model NOT found at: {rvc_model_path}")
            print(f"  Download from: https://huggingface.co/lj1995/VoiceConversionModels")
            return False
            
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_voice_conversion_module():
    """Test if voice_conversion module works"""
    print("\n[TEST 4] Voice Conversion Module")
    print("-" * 50)
    
    try:
        from utils.voice_conversion import (
            check_dependency,
            download_audio,
            separate_vocals,
            convert_voice_rvc,
            merge_audio,
        )
        
        print("✓ download_audio function available")
        print("✓ separate_vocals function available")
        print("✓ convert_voice_rvc function available")
        print("✓ merge_audio function available")
        print("✓ check_dependency function available")
        
        # Print GPU info from module
        from utils.voice_conversion import CUDA_AVAILABLE, GPU_NAME
        print(f"\n  Module GPU Status: {GPU_NAME}")
        print(f"  CUDA Available in Module: {CUDA_AVAILABLE}")
        
        return True
    except Exception as e:
        print(f"✗ Voice conversion module error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_function():
    """Test if new prompt function exists"""
    print("\n[TEST 5] Prompt Generator")
    print("-" * 50)
    
    try:
        from utils.promptMaker import getPromptForCoverLyrics
        
        # Generate test prompt
        prompt = getPromptForCoverLyrics("Test Lagu", "Test Artist", language="id")
        
        print(f"✓ getPromptForCoverLyrics function available")
        print(f"✓ Generated prompt with {len(prompt)} messages")
        
        for i, msg in enumerate(prompt):
            print(f"  Message {i+1}: {msg['role']:10} ({len(msg['content'])} chars)")
        
        return True
    except Exception as e:
        print(f"✗ Prompt function error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("  AI WAIFU VTUBER - GPU & VOICE CONVERSION TEST")
    print("="*50)
    
    results = {
        "PyTorch CUDA": test_pytorch_cuda(),
        "Dependencies": test_dependencies(),
        "Configuration": test_config(),
        "Voice Conversion Module": test_voice_conversion_module(),
        "Prompt Generator": test_prompt_function(),
    }
    
    print("\n" + "="*50)
    print("  TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {test_name}")
    
    print("="*50)
    print(f"Result: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("🎉 All systems GO! Ready for voice conversion!")
        print("\nTry: _atri cover_advanced https://youtu.be/xxxxx")
        print("Or:  _atri cover <Song Name>\n")
        return 0
    else:
        print("⚠️  Some tests failed - see above for details")
        print("Common fixes:")
        print("  1. Run: .\\setup_gpu.bat")
        print("  2. Install missing dependencies: pip install <package>")
        print("  3. Check config.py settings")
        print("  4. Download RVC model to models/atri_rvc_model.pth\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
