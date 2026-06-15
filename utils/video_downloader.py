import os
import tempfile
from config import video_download_dir

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None


class YTDLPLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(f"yt-dlp error: {msg}")


def download_video(url, output_dir=None, target_format=None):
    if YoutubeDL is None:
        raise RuntimeError("yt-dlp is not installed. Install it with pip install yt-dlp")

    # Resolve output directory: explicit > config > system temp
    resolved_dir = output_dir or (video_download_dir if video_download_dir else None) or tempfile.gettempdir()
    resolved_dir = os.path.abspath(resolved_dir)
    os.makedirs(resolved_dir, exist_ok=True)

    # Build ydl options depending on requested target_format
    ydl_opts = {
        "outtmpl": os.path.join(resolved_dir, "%(title).200s.%(ext)s"),
        "noplaylist": True,
        # produce filesystem-safe filenames to avoid Windows illegal chars
        "restrictfilenames": True,
        "logger": YTDLPLogger(),
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "continuedl": True,
    }

    tf = (target_format or "").lower() if target_format else ""
    # If user requested audio extraction
    if tf in ("mp3", "wav", "m4a", "aac"):
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": tf,
                    "preferredquality": "192",
                }
            ],
        })
    else:
        # Default: download video. Prefer HEVC if requested
        ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"
        if tf in ("hevc", "h265", "hvcc"):
            # Ask yt-dlp to recode the video to HEVC (requires ffmpeg)
            # This uses yt-dlp's recode_video option which maps to --recode-video
            ydl_opts["recode_video"] = "hevc"
        else:
            # leave original encoding; user gets default container
            pass

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename, info.get("title", "video")
