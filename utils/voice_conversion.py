"""
Advanced Voice Conversion Module
Supports: yt-dlp, Demucs/UVR, RVC CLI, FFmpeg
GPU Support: CUDA optimization for RTX 3050 and other NVIDIA GPUs
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# GPU Configuration
try:
    import torch
    import fairseq
    torch.serialization.add_safe_globals([fairseq.data.dictionary.Dictionary])
    CUDA_AVAILABLE = torch.cuda.is_available()
    GPU_DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"
    if CUDA_AVAILABLE:
        GPU_NAME = torch.cuda.get_device_name(0)
    else:
        GPU_NAME = "CPU Only"
except:
    CUDA_AVAILABLE = False
    GPU_DEVICE = "cpu"
    GPU_NAME = "CPU Only"

print(f"[Voice Conversion] GPU Support: {GPU_NAME} ({'ENABLED' if CUDA_AVAILABLE else 'DISABLED'})")

def check_dependency(cmd):
    """Check if command exists in PATH"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def download_audio(url, output_path=None):
    """Download audio from YouTube/URL using yt-dlp dengan pemaksaan format WAV"""
    if not check_dependency("yt-dlp"):
        raise RuntimeError("yt-dlp tidak terinstall. Install dengan: pip install yt-dlp")
    
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"atri_cover_download.wav")
    
    # Memastikan jika output_path bertipe Path, diubah ke string
    output_path = str(output_path)
    
    # yt-dlp kadang menambahkan ekstensi sendiri jika tidak dipaksa, 
    # kita hapus .wav di ujung template -o karena --audio-format akan menambahkan .wav secara otomatis
    if output_path.endswith('.wav'):
        template_path = output_path[:-4]
    else:
        template_path = output_path

    try:
        cmd = [
            "yt-dlp",
            "-x",                          # Ekstrak audio saja
            "--audio-format", "wav",       # PAKSA konversi ke format .wav (Membutuhkan FFmpeg di PATH)
            "--audio-quality", "0",        # Kualitas terbaik
            "-f", "bestaudio/best",
            "--cookies", "cookies.txt",
            "-o", f"{template_path}",     # Template output tanpa ekstensi ganda
            "--no-playlist",               # Hindari mendownload seluruh playlist jika link berupa list
            url
        ]
        
        print(f"[yt-dlp] Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp error: {result.stderr}")
        
        # Pengaman: Jika yt-dlp menghasilkan file dengan ekstensi pasca-proses
        if not os.path.exists(output_path) and os.path.exists(f"{template_path}.wav"):
            output_path = f"{template_path}.wav"
            
        if not os.path.exists(output_path):
            raise RuntimeError(f"Audio file tidak ditemukan di lokasi target: {output_path}")
        
        print(f"[yt-dlp] Download sukses: {output_path}")
        return output_path
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("Download timeout (>5 menit)")
    except Exception as e:
        raise RuntimeError(f"Download error: {str(e)}")

def separate_vocals(audio_path, output_dir=None, engine="demucs"):
    """
    Separate vocals and instruments using Demucs or UVR
    Returns: (vocal_path, instrumental_path)
    """
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), f"atri_cover_separated")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if engine.lower() == "demucs":
        return _separate_demucs(audio_path, output_dir)
    elif engine.lower() == "uvr":
        return _separate_uvr(audio_path, output_dir)
    else:
        raise ValueError(f"Unknown engine: {engine}. Use 'demucs' or 'uvr'")

def _separate_demucs(audio_path, output_dir):
    """Separate using Facebook's Demucs with GPU optimization"""
    if not check_dependency("demucs"):
        raise RuntimeError("Demucs tidak terinstall. Install dengan: pip install demucs")
    
    try:
        # Run demucs with GPU support
        cmd = [
            r".venv\Scripts\python.exe", "-m", "demucs",
            "-n", "htdemucs",          # Model name
            "--two-stems", "vocals",   # FIX: Paksa Demucs hanya mengeluarkan 'vocals' dan 'no_vocals'
            "-o", output_dir,
            "--device", GPU_DEVICE,    # Use GPU if available
        ]
        
        # For CPU-only, add jobs parameter for faster processing
        if not CUDA_AVAILABLE:
            cmd.extend(["--jobs", "4"])
        
        cmd.append(audio_path)
        
        print(f"[Demucs] Processing on {GPU_DEVICE} - {GPU_NAME}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise RuntimeError(f"Demucs error: {result.stderr}")
        
        # Find output folder (demucs creates folder with audio name)
        audio_name = Path(audio_path).stem
        demucs_output = os.path.join(output_dir, "htdemucs", audio_name)
        
        if not os.path.exists(demucs_output):
            raise RuntimeError(f"Demucs output folder tidak ditemukan: {demucs_output}")
        
        # Jalur vokal default
        vocal_path = os.path.join(demucs_output, "vocals.wav")
        
        # Karena di atas kita pakai --two-stems vocals, filenya PASTI bernama no_vocals.wav
        instrumental_path = os.path.join(demucs_output, "no_vocals.wav")
        
        # Fallback pengaman jika ternyata versinya berbeda
        if not os.path.exists(instrumental_path):
            instrumental_path = os.path.join(demucs_output, "accompaniment.wav")
        
        if not os.path.exists(vocal_path):
            raise RuntimeError(f"Vocal file tidak ditemukan: {vocal_path}")
        if not os.path.exists(instrumental_path):
            raise RuntimeError(f"Instrumental file tidak ditemukan (no_vocals / accompaniment tidak ada)")
        
        return vocal_path, instrumental_path
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("Demucs timeout (>10 menit)")
    except Exception as e:
        raise RuntimeError(f"Separation error: {str(e)}")

def _separate_uvr(audio_path, output_dir):
    """Separate using UVR (UltraVoiceRemover)"""
    # Note: UVR is more complex to setup, for now we support basic Demucs
    raise NotImplementedError("UVR support sedang dikembangkan. Gunakan 'demucs' untuk sekarang.")

def convert_voice_rvc(vocal_path, output_path=None, model_path=None, index_path=None, 
                      speaker_id=0, f0_up_key=0, filter_radius=3, resample_sr=0, 
                      rms_mix_rate=0.25, protect=0.33):
    """
    Convert vocal using RVC (Retrieval-based Voice Conversion) with GPU optimization
    Supports NVIDIA GPUs (CUDA), can fallback to CPU
    
    Args:
        vocal_path: Path to vocal audio
        output_path: Output path for converted vocal
        model_path: Path to RVC model (.pth file)
        index_path: Path to RVC index (.index file)
        speaker_id: Speaker ID in model (usually 0)
        f0_up_key: Pitch shift (-12 to 12)
    
    Returns: output_path
    """
    if not check_dependency("python"):
        raise RuntimeError("Python tidak ditemukan")
    
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), "atri_cover_vocal_converted.wav")
    
    # Check if model exists
    if model_path is None:
        raise RuntimeError("Model path tidak diberikan. Setup RVC model dulu.")
    
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model tidak ditemukan: {model_path}")
    
    try:
        print(f"[RVC] Converting voice on {GPU_DEVICE} - {GPU_NAME}")
        
        # Build RVC inference command with GPU support
        cmd = [
            r".venv\Scripts\python.exe",
            "tools/infer_cli.py",
            "--model_name", os.path.basename(model_path),
            "--input_path", str(vocal_path),
            "--opt_path", str(output_path),
            "--f0up_key", str(f0_up_key),
            "--filter_radius", str(filter_radius),
            "--resample_sr", str(resample_sr),
            "--rms_mix_rate", str(rms_mix_rate),
            "--protect", str(protect),
            "--device", GPU_DEVICE  # GPU or CPU
        ]
        
        # Use half precision on GPU for faster inference
        if CUDA_AVAILABLE:
            cmd.extend(["--is_half", "True"])
        
        if index_path and os.path.exists(index_path):
            cmd.extend(["--index_path", index_path])
        
        # Menyuntikkan folder rvc ke dalam jalur pencarian Python
        current_env = os.environ.copy()
        current_env["PYTHONPATH"] = os.path.abspath("rvc")
        current_env["TORCH_FORCE_WEIGHTS_ONLY_LOAD"] = "0"

        result = subprocess.run(
            cmd, 
            cwd="rvc",
            capture_output=True, 
            text=True, 
            timeout=600,
            env=current_env  # <--- Memaksa Python RVC mengenali foldernya sendiri
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"RVC error: {result.stderr}")
        
        if not os.path.exists(output_path):
            raise RuntimeError(f"Converted vocal tidak ditemukan: {output_path}")
        
        print(f"[RVC] Conversion complete: {output_path}")
        return output_path
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("RVC conversion timeout (>10 menit)")
    except Exception as e:
        raise RuntimeError(f"RVC conversion error: {str(e)}")

def merge_audio(vocal_path, instrumental_path, output_path):
    """Menggabungkan vokal hasil RVC dan instrumen kembali menjadi satu berkas MP3"""
    # Paksa output_path menggunakan ekstensi .mp3 jika belum
    base, ext = os.path.splitext(output_path)
    if ext.lower() != ".mp3":
        output_path = base + ".mp3"

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except:
            pass

    # Command FFmpeg untuk mixing vokal + instrumen dan konversi ke MP3 320kbps
    cmd = [
        "ffmpeg", "-y",
        "-i", vocal_path,
        "-i", instrumental_path,
        "-filter_complex", "amix=inputs=2:duration=longest",
        "-b:a", "320k",
        output_path
    ]
    
    print(f"[Voice Conversion] Merging into MP3: {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg merge error: {result.stderr}")
        
    return output_path

def cleanup(paths):
    """Clean up temporary files"""
    if isinstance(paths, str):
        paths = [paths]
    
    for path in paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"[Voice Conversion] Cleanup error: {e}")

def process_cover_full(url, output_path=None, model_path=None, index_path=None,
                       separation_engine="demucs", f0_up_key=0):
    """
    Full pipeline: Download → Separate → Convert → Merge
    
    Returns: (final_output_path, metadata_dict)
    """
    temp_dir = os.path.join(tempfile.gettempdir(), f"atri_cover_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Step 1: Download
        print("[Voice Conversion] Downloading audio...")
        audio_path = os.path.join(temp_dir, "downloaded.wav")
        audio_path = download_audio(url, audio_path)
        
        # Step 2: Separate
        print("[Voice Conversion] Separating vocals and instruments...")
        vocal_path, instrumental_path = separate_vocals(audio_path, temp_dir, separation_engine)
        
        # Step 3: Convert
        print("[Voice Conversion] Converting vocal to Atri's voice...")
        vocal_converted_path = os.path.join(temp_dir, "vocal_converted.wav")
        vocal_converted_path = convert_voice_rvc(
            vocal_path,
            vocal_converted_path,
            model_path=model_path,
            index_path=index_path,
            f0_up_key=f0_up_key
        )
        
        # Step 4: Merge
        print("[Voice Conversion] Merging audio...")
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "atri_cover_final.wav")
        
        final_path = merge_audio(vocal_converted_path, instrumental_path, output_path)
        
        metadata = {
            "success": True,
            "output": final_path,
            "url": url,
            "stages": ["download", "separate", "convert", "merge"]
        }
        
        return final_path, metadata
    
    except Exception as e:
        print(f"[Voice Conversion] Pipeline error: {e}")
        raise
    finally:
        # Cleanup temp files
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
