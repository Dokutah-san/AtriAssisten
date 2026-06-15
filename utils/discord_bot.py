import sys
import os
import json
import math
import re
import wave
import audioop
import base64
import asyncio
import shutil
import tempfile
import subprocess
import uuid
import threading
import time
import logging
import discord
import random
import requests
import feedparser
import aiohttp
from discord.ext import tasks
from bs4 import BeautifulSoup
from discord import Intents
from discord.ext import commands

# Masukkan Alamat IP yang kamu dapatkan dari Serial Monitor Arduino
ESP8266_IP = "192.168.100.126" 

async def handle_control_led(message, command_text):
    """Fungsi manual untuk kontrol LED lokal lewat ESP8266. Penggunaan: _atri led on / _atri led off"""
    # ---- PERUBAHAN DI SINI: Hak akses khusus Developer / Pemilik Bot ----
    if message.author.id != int(developer_id):
        await message.channel.send("❌ Maaf, perintah kontrol LED ini sangat rahasia dan hanya bisa diakses oleh Master saya!")
        return True
    # ---------------------------------------------------------------------

    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("❌ Perintah salah! Gunakan: `_atri led on` atau `_atri led off`")
        return True
        
    aksi = parts[1].strip().lower()
    if aksi not in ["on", "off"]:
        await message.channel.send("❌ Perintah salah! Gunakan: `_atri led on` atau `_atri led off`")
        return True

    # Kirim pesan loading awal ke Discord
    loading_msg = await message.channel.send(f"🔄 Sedang mengirim perintah ke ESP8266...")

    # Mulai HTTP Request secara asinkronus
    async with aiohttp.ClientSession() as session:
        try:
            url = f"http://{ESP8266_IP}/led/{aksi}"
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    text_respons = await response.text()
                    if "LED_NYALA" in text_respons:
                        await loading_msg.edit(content="💡 **AtriAssisten Berhasil:** Lampu bawaan ESP8266 sekarang **NYALA**!")
                    elif "LED_MATI" in text_respons:
                        await loading_msg.edit(content="🌑 **AtriAssisten Berhasil:** Lampu bawaan ESP8266 sekarang **MATI**!")
                else:
                    await loading_msg.edit(content=f"❌ ESP8266 merespons dengan eror kode: {response.status}")
        
        except aiohttp.ClientConnectorError:
            await loading_msg.edit(content=f"❌ Gagal terhubung ke ESP8266 di IP `{ESP8266_IP}`! Pastikan alat menyala dan PC kamu satu jaringan Wi-Fi.")
        except Exception as e:
            await loading_msg.edit(content=f"❌ Terjadi kesalahan sistem: {str(e)}")
            
    return True

CHANNEL_GAME_GRATIS_ID = 1510245357068484608  # <-- GANTI DENGAN ID CHANNELMU

# Set untuk menyimpan ID game yang sudah pernah dikabarkan agar tidak spam
terkirim_cache = set()

@tasks.loop(hours=1)
async def cek_game_gratis_steam():
    """Task latar belakang untuk mengecek game gratis di Steam & Epic Games Store"""
    global conversation
    
    channel = client.get_channel(CHANNEL_GAME_GRATIS_ID)
    if not channel:
        return

    # Kueri RSS diubah agar mencari domain Steam ATAU Epic Games
    url_feed = "https://www.reddit.com/r/FreeGameFindings/search.rss?q=site:store.steampowered.com+OR+steam+OR+site:epicgames.com+OR+epic&sort=new&restrict_sr=on"
    
    try:
        feed = await asyncio.to_thread(feedparser.parse, url_feed)
        
        for entry in reversed(feed.entries[:5]):
            entry_id = entry.id
            title = entry.title
            link = entry.link
            
            if entry_id in terkirim_cache:
                continue
                
            title_lower = title.lower()
            
            # Deteksi platform berdasarkan teks judul atau link kiriman
            platform = "Unknown"
            embed_color = discord.Color.default()
            
            if "steam" in title_lower or "steampowered" in link.lower():
                platform = "Steam"
                embed_color = discord.Color.from_rgb(0, 172, 237)  # Biru Khas Steam
            elif "epic" in title_lower or "epicgames" in link.lower():
                platform = "Epic Games Store"
                embed_color = discord.Color.from_rgb(31, 31, 31)   # Hitam Khas Epic
            
            # Memastikan pos ini adalah info game gratisan/diskon 100%
            if platform != "Unknown":
                if any(keyword in title_lower for keyword in ["100%", "free", "gratis"]):
                    
                    # Membuat tampilan pengumuman kustom berdasarkan platform game
                    embed = discord.Embed(
                        title=f"🎮 Master! Ada Game Gratis di {platform}!",
                        description=f"**{title}**",
                        color=embed_color
                    )
                    embed.add_field(name="🔗 Tautan Informasi / Klaim", value=f"[Diskusi & Cara Klaim]({link})", inline=False)
                    embed.set_footer(text=f"AtriAssisten • Pemburu Game Gratis {platform}")
                    
                    await channel.send(content="@everyone 📢 **Ada game gratis!**", embed=embed)
                    terkirim_cache.add(entry_id)
                    
    except Exception as e:
        print(f"[Game Scraper Error]: {e}")

try:
    import nacl  # noqa: F401
    import davey  # noqa: F401
    VOICE_BACKEND_READY = True
except Exception:
    VOICE_BACKEND_READY = False

try:
    from discord.ext import voice_recv
    VOICE_RECV_AVAILABLE = True
except Exception:
    voice_recv = None
    VOICE_RECV_AVAILABLE = False

try:
    from discord.opus import OpusError
except Exception:
    OpusError = Exception

try:
    import speech_recognition as sr
except Exception:
    sr = None

# Paksa Python mengenali folder 'utils' agar tidak terjadi ImportError saat memanggil video_downloader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    discord_bot_token,
    video_download_dir,
    developer_id,
    whisper_model,
    whisper_model_dir,
    whisper_device,
    whisper_compute_type,
    whisper_language,
    tts_engine,
    tts_language,
    tts_model,
    tts_speaker,
    discord_voice_no_speech_threshold,
    discord_voice_max_no_speech_prob,
    discord_voice_min_avg_logprob,
    discord_voice_language,
    discord_voice_min_rms,
    discord_voice_min_duration,
    discord_voice_keep_last_wav,
    discord_voice_last_wav,
)
from utils.llm import chat_completion, translate_for_display
from utils.TTS import voicevox_tts, silero_tts
from utils.stt import transcribe_local_audio
from utils.promptMaker import getPrompt, getPromptForCoverLyrics, generate_cover_lyrics_with_fallback
from utils.voice_conversion import (
    download_audio, separate_vocals, convert_voice_rvc, merge_audio,
    process_cover_full, check_dependency, cleanup
)

try:
    from video_downloader import download_video
except ImportError:
    from utils.video_downloader import download_video

# Impor pustaka untuk pencarian internet (Skenario B)
from ddgs import DDGS

DISCORD_API_BASE = "https://discord.com/api/v10"
VOICE_MESSAGE_FLAG = 1 << 13
MAX_WAVEFORM_POINTS = 256
TTS_TEMP_WAV = os.path.join(tempfile.gettempdir(), "atri_discord_voice.wav")
TTS_TEMP_OGG = os.path.join(tempfile.gettempdir(), "atri_discord_voice.ogg")
FFMPEG_PATH = shutil.which("ffmpeg")
VOICE_SILENCE_RMS = 80  # Reduced from 120 since we now use left channel only (lower RMS)
VOICE_UTTERANCE_TIMEOUT = 1.15
VOICE_MIN_BUFFER_SECONDS = 0.45
VOICE_TRIGGER_WORD = "atri"


class VoiceSession:
    def __init__(self):
        self.sink = None
        self.text_channel_id = None
        self.busy = False
        self.lock = asyncio.Lock()


voice_sessions = {}

try:
    from discord.ext.voice_recv.extras.speechrecognition import SpeechRecognitionSink
except Exception:
    SpeechRecognitionSink = None

logging.getLogger("discord.ext.voice_recv").setLevel(logging.WARNING)

if VOICE_RECV_AVAILABLE:
    _original_decode_packet = voice_recv.opus.PacketDecoder._decode_packet

    def _safe_decode_packet(self, packet):
        try:
            return _original_decode_packet(self, packet)
        except OpusError:
            if packet:
                try:
                    return packet, self._decoder.decode(None, fec=False)
                except Exception:
                    return packet, b""
            return packet, b""

    voice_recv.opus.PacketDecoder._decode_packet = _safe_decode_packet

def save_conversation(conversation):
    with open("conversation.json", "w", encoding="utf-8") as f:
        json.dump({"history": conversation}, f, indent=4)

def is_voice_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("suara", "voice", "vn")

def is_voice_channel_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("vc", "voicechannel", "speakvc")

def is_voice_disconnect_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("vcend", "vcoff", "leavevc", "disconnectvc", "dcvc")

def is_cover_command(command_text):
    """Check if command is a song cover request"""
    return command_text.lower().split(maxsplit=1)[0] in ("cover", "sing", "nyanyi", "lagu")

def is_cover_advanced_command(command_text):
    """Check if command is advanced voice conversion cover"""
    cmd = command_text.lower().split(maxsplit=1)[0]
    return cmd in ("cover_advanced", "cover_rvc", "cover_vokal", "rvc", "voicecover")

def generate_tts_audio(text, wav_path=TTS_TEMP_WAV):
    if tts_engine == "voicevox":
        return voicevox_tts(text, output_path=wav_path)
    return silero_tts(text, tts_language, tts_model, tts_speaker, output_path=wav_path)

def make_temp_audio_paths():
    token = uuid.uuid4().hex
    wav_path = os.path.join(tempfile.gettempdir(), f"atri_{token}.wav")
    ogg_path = os.path.join(tempfile.gettempdir(), f"atri_{token}.ogg")
    return wav_path, ogg_path

def get_voice_session(guild_id):
    session = voice_sessions.get(guild_id)
    if session is None:
        session = VoiceSession()
        voice_sessions[guild_id] = session
    return session

def build_voice_recognition_sink(guild_id):
    if SpeechRecognitionSink is None or sr is None:
        raise RuntimeError("SpeechRecognitionSink belum tersedia. Pastikan SpeechRecognition terpasang.")

    def process_cb(recognizer, audio, user):
        if user and (getattr(user, "bot", False) or getattr(user, "id", None) == getattr(client.user, "id", None)):
            print(f"[Discord Voice STT] Ignoring bot/self audio from {user.display_name if user else 'Unknown'}")
            return None
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"atri_vc_{uuid.uuid4().hex}.wav")
            # AudioData dari SpeechRecognition sudah berupa audio mono.
            # Ambil raw PCM mono langsung dari objek audio, lalu simpan sebagai WAV 16kHz/16-bit mono.
            raw_bytes = audio.get_raw_data(convert_rate=16000, convert_width=2)
            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(raw_bytes)

            try:
                # Transkrip dengan penguncian bahasa dan toleransi threshold yang aman
                text = transcribe_local_audio(
                    temp_path,
                    min_duration=0.3,
                    min_rms=50,
                    beam_size=5,             # Berikan space agar Whisper berpikir lebih akurat
                    vad_filter=True,
                    language=discord_voice_language,           # Use discord voice language setting
                    no_speech_threshold=discord_voice_no_speech_threshold,
                    min_avg_logprob=discord_voice_min_avg_logprob,
                    max_no_speech_prob=discord_voice_max_no_speech_prob
                )
            finally:
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

            if text:
                print(f"[Discord Voice STT] {user.display_name if user else 'Unknown'} -> {text}")
            return text
        except Exception as e:
            print(f"[Discord Voice STT] Failed transcribe for {user.display_name if user else 'Unknown'}: {repr(e)}")
            return None

    def text_cb(user, text):
        if not user or not text:
            return

        if getattr(user, "bot", False) or getattr(user, "id", None) == getattr(client.user, "id", None):
            return

        normalized = text.lower().strip()
        if not re.search(r"\b(atri|atrii|atry)\b", normalized):
            return

        cleaned_text = re.sub(r"\b(atri|atrii|atry)\b[\s,.:;!?-]*", "", text, flags=re.IGNORECASE).strip()
        if not cleaned_text:
            return

        session = get_voice_session(guild_id)
        if session.busy:
            print("[Discord Voice Text] Atri sedang sibuk berbicara, perintah diabaikan.")
            return

        async def runner():
            async with session.lock:
                if session.busy:
                    return
                session.busy = True
            try:
                member = None
                guild = client.get_guild(guild_id)
                if guild and user:
                    member = guild.get_member(user.id)
                speaker_name = member.display_name if member else (user.display_name if user else "Someone")
                await handle_voice_speech_trigger(
                    guild_id=guild_id,
                    speaker_name=speaker_name,
                    transcript=cleaned_text,
                )
            finally:
                session.busy = False

        asyncio.run_coroutine_threadsafe(runner(), client.loop)

    return SpeechRecognitionSink(
        process_cb=process_cb,
        text_cb=text_cb,
        default_recognizer="faster_whisper",
        phrase_time_limit=5,
        ignore_silence_packets=True,
    )

def write_pcm_to_wav(pcm_bytes, wav_path):
    with wave.open(wav_path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(pcm_bytes)

def pcm_stereo_48k_to_mono_16k(pcm_bytes):
    if not pcm_bytes:
        return b""

    # Extract LEFT channel only (Discord usually encodes user mic on left)
    # Stereo PCM: [L0, L1, R0, R1, L2, L3, R2, R3, ...] (2 bytes each sample)
    left_channel = b""
    for i in range(0, len(pcm_bytes), 4):  # 4 bytes = 1 left + 1 right sample
        if i + 1 < len(pcm_bytes):
            left_channel += pcm_bytes[i:i+2]
    
    # Convert 48kHz to 16kHz
    converted_bytes, _ = audioop.ratecv(left_channel, 2, 1, 48000, 16000, None)
    return converted_bytes


class AtriVoiceSink(voice_recv.AudioSink if VOICE_RECV_AVAILABLE else object):
    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = guild_id
        self._buffers = {}
        self._timers = {}
        self._lock = threading.Lock()
        self._closed = False
        self.paused = False
        self._atri_voice_client = None
        self._last_audio_time = {}  # Track last audio time per user

    def wants_opus(self):
        return False

    def _cancel_timer_locked(self, user_id):
        timer = self._timers.pop(user_id, None)
        if timer:
            print(f"[Discord Voice TIMER] Cancelled timer for user {user_id}")
            timer.cancel()

    def _schedule_finalize_locked(self, user_id):
        # Jangan schedule jika sudah ada timer yang berjalan
        if user_id in self._timers:
            # Update last audio time tapi jangan reset timer
            self._last_audio_time[user_id] = time.time()
            return
        
        self._last_audio_time[user_id] = time.time()
        print(f"[Discord Voice TIMER] Scheduling finalize for user {user_id} after {VOICE_UTTERANCE_TIMEOUT}s")
        timer = threading.Timer(VOICE_UTTERANCE_TIMEOUT, self._finalize_user, args=(user_id,))
        timer.daemon = True
        self._timers[user_id] = timer
        timer.start()

    def write(self, user, data):
        if self._closed or self.paused or user is None or getattr(user, "bot", False):
            return

        pcm = getattr(data, "pcm", b"")
        if not pcm:
            return

        rms = audioop.rms(pcm, 2)
        user_id = user.id
        user_name = user.display_name if user else "Unknown"

        with self._lock:
            buf = self._buffers.setdefault(user_id, bytearray())
            if rms >= VOICE_SILENCE_RMS:
                buf.extend(pcm)
                print(f"[Discord Voice AUDIO] {user_name} (RMS={rms}) -> buffered, total={len(buf)} bytes")
            else:
                print(f"[Discord Voice AUDIO] {user_name} (RMS={rms}) -> SILENT/NOISE, skipped")
            self._schedule_finalize_locked(user_id)

    def cleanup(self):
        self._closed = True
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()
            self._buffers.clear()

    def _finalize_user(self, user_id):
        if self._closed:
            return

        with self._lock:
            pcm = bytes(self._buffers.pop(user_id, b""))
            self._timers.pop(user_id, None)

        if not pcm:
            print(f"[Discord Voice FINALIZE] User {user_id}: No audio buffered, skipped")
            return

        # Calculate RMS of the buffer for debugging
        input_rms = audioop.rms(pcm, 2) if pcm else 0
        mono_pcm = pcm_stereo_48k_to_mono_16k(pcm)
        output_rms = audioop.rms(mono_pcm, 2) if mono_pcm else 0
        duration_secs = len(mono_pcm) / (16000 * 2)
        print(f"[Discord Voice FINALIZE] User {user_id}: input_rms={input_rms}, output_rms={output_rms}, duration={duration_secs:.2f}s, required={VOICE_MIN_BUFFER_SECONDS}s")
        
        if duration_secs < VOICE_MIN_BUFFER_SECONDS:
            print(f"[Discord Voice FINALIZE] User {user_id}: TOO SHORT, skipped")
            return

        wav_path = os.path.join(tempfile.gettempdir(), f"atri_voice_{uuid.uuid4().hex}.wav")
        write_pcm_to_wav(mono_pcm, wav_path)
        print(f"[Discord Voice FINALIZE] User {user_id}: WAV created -> {wav_path}")

        session = voice_sessions.get(self.guild_id)
        if not session or not session.sink or session.sink is not self:
            print(f"[Discord Voice FINALIZE] User {user_id}: Session invalid, cleanup WAV")
            try:
                os.remove(wav_path)
            except Exception:
                pass
            return

        loop = None
        voice_client = self._atri_voice_client
        if voice_client and voice_client.client:
            loop = voice_client.client.loop

        if loop is None:
            print(f"[Discord Voice FINALIZE] User {user_id}: No event loop, cleanup WAV")
            try:
                os.remove(wav_path)
            except Exception:
                pass
            return

        asyncio.run_coroutine_threadsafe(
            self._process_wav(user_id, wav_path),
            loop,
        )

    async def _process_wav(self, user_id, wav_path):
        session = voice_sessions.get(self.guild_id)
        if not session or session.sink is not self:
            try:
                os.remove(wav_path)
            except Exception:
                pass
            return

        voice_client = self._atri_voice_client
        guild = voice_client.guild if voice_client else None
        member = guild.get_member(user_id) if guild else None
        speaker_name = member.display_name if member else f"User {user_id}"
        print(f"[Discord Voice PROCESS] Processing from {speaker_name} (ID={user_id})")

        try:
            print(f"[Discord Voice PROCESS] Transcribing with language={discord_voice_language}, min_duration={discord_voice_min_duration}, min_rms={discord_voice_min_rms}...")
            transcript = await asyncio.to_thread(
                transcribe_local_audio,
                wav_path,
                min_duration=discord_voice_min_duration,
                min_rms=discord_voice_min_rms,
                language=discord_voice_language,
                no_speech_threshold=discord_voice_no_speech_threshold,
                max_no_speech_prob=discord_voice_max_no_speech_prob,
                min_avg_logprob=discord_voice_min_avg_logprob,
            )
            print(f"[Discord Voice PROCESS] Transcript: '{transcript}'")
            
            # Save WAV for debugging if configured
            if discord_voice_keep_last_wav and discord_voice_last_wav:
                try:
                    debug_wav = os.path.join(os.getcwd(), discord_voice_last_wav)
                    shutil.copy(wav_path, debug_wav)
                    print(f"[Discord Voice PROCESS] Saved WAV for debugging: {debug_wav}")
                except Exception as e:
                    print(f"[Discord Voice PROCESS] Failed to save debug WAV: {e}")
        except Exception as e:
            print(f"[Discord Voice PROCESS] Transcription error: {e}")
            import traceback
            traceback.print_exc()
            transcript = ""
        finally:
            try:
                os.remove(wav_path)
            except Exception:
                pass

        if not transcript:
            print(f"[Discord Voice PROCESS] Transcript empty")
            return

        normalized = transcript.lower()
        if "atri" not in normalized:
            print(f"[Discord Voice DEBUG] Trigger 'atri' not found in: '{transcript}'")
            return
        print(f"[Discord Voice DEBUG] Trigger 'atri' detected!")

        cleaned_text = re.sub(r"\batri\b[\s,.:;!?-]*", "", transcript, flags=re.IGNORECASE).strip()
        if not cleaned_text:
            print(f"[Discord Voice DEBUG] Cleaned text empty")
            return
        print(f"[Discord Voice DEBUG] Command: '{cleaned_text}'")

        if session.busy:
            return

        async with session.lock:
            if session.busy:
                return
            session.busy = True

        try:
            print(f"[Discord Voice DEBUG] Calling handler...")
            await handle_voice_speech_trigger(
                guild_id=self.guild_id,
                speaker_name=speaker_name,
                transcript=cleaned_text,
            )
            print(f"[Discord Voice DEBUG] Handler done")
        except Exception as e:
            print(f"[Discord Voice DEBUG] Handler error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.busy = False

def wav_duration_seconds(wav_path):
    with wave.open(wav_path, "rb") as wav_file:
        frame_count = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        if sample_rate <= 0:
            return 0.0
        return frame_count / float(sample_rate)

def build_waveform_base64(wav_path):
    with wave.open(wav_path, "rb") as wav_file:
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        pcm = wav_file.readframes(frame_count)

    if not pcm or sample_rate <= 0:
        return base64.b64encode(bytes([0])).decode("ascii")

    duration = frame_count / float(sample_rate)
    points = max(1, min(MAX_WAVEFORM_POINTS, int(math.ceil(duration * 10))))
    chunk_size = max(sample_width, (len(pcm) // points) // sample_width * sample_width)
    if chunk_size < sample_width:
        chunk_size = sample_width

    waveform = bytearray()
    for index in range(0, len(pcm), chunk_size):
        chunk = pcm[index:index + chunk_size]
        if not chunk:
            continue
        if len(chunk) % sample_width != 0:
            chunk = chunk[: len(chunk) - (len(chunk) % sample_width)]
        if not chunk:
            continue
        rms = audioop.rms(chunk, sample_width)
        amplitude = max(0, min(255, int(rms * 255 / 32768)))
        waveform.append(amplitude)
        if len(waveform) >= MAX_WAVEFORM_POINTS:
            break

    if not waveform:
        waveform.append(0)

    return base64.b64encode(bytes(waveform)).decode("ascii")

def convert_wav_to_ogg_opus(wav_path, ogg_path):
    if not FFMPEG_PATH:
        raise RuntimeError("ffmpeg tidak ditemukan di PATH.")

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        wav_path,
        "-ac",
        "1",
        "-ar",
        "48000",
        "-c:a",
        "libopus",
        "-b:a",
        "32k",
        ogg_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Gagal mengubah WAV ke OGG Opus.")

    return ogg_path

def send_discord_voice_message(channel_id, ogg_path, duration_secs, waveform_b64):
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
    payload = {
        "flags": VOICE_MESSAGE_FLAG,
        "attachments": [
            {
                "id": 0,
                "filename": os.path.basename(ogg_path),
                "duration_secs": round(duration_secs, 2),
                "waveform": waveform_b64,
            }
        ],
    }

    headers = {
        "Authorization": f"Bot {discord_bot_token}",
        "User-Agent": "DiscordBot (AI-Waifu-Vtuber, 1.0)",
    }

    with open(ogg_path, "rb") as audio_file:
        files = {
            "files[0]": (os.path.basename(ogg_path), audio_file, "audio/ogg"),
        }
        data = {
            "payload_json": json.dumps(payload),
        }
        response = requests.post(url, headers=headers, data=data, files=files, timeout=60)
        if not response.ok:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(f"Discord API error {response.status_code}: {detail}")
        return response.json()

async def send_voice_note_reply(message, text):
    wav_path = None
    ogg_path = None
    try:
        wav_path, ogg_path = make_temp_audio_paths()
        wav_path = generate_tts_audio(text, wav_path)
        duration_secs = wav_duration_seconds(wav_path)
        waveform_b64 = build_waveform_base64(wav_path)
        ogg_path = convert_wav_to_ogg_opus(wav_path, ogg_path)
        await asyncio.to_thread(
            send_discord_voice_message,
            message.channel.id,
            ogg_path,
            duration_secs,
            waveform_b64,
        )
        return True
    finally:
        for path in (wav_path, ogg_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

async def play_voice_channel_reply(message, text):
    if not message.guild:
        await message.channel.send("Fitur voice channel hanya bisa dipakai di server, bukan DM.")
        return True

    if not message.author.voice or not message.author.voice.channel:
        await message.channel.send("Kamu harus masuk ke voice channel dulu supaya Atri bisa ikut bicara di sana.")
        return True

    if not FFMPEG_PATH:
        await message.channel.send("ffmpeg belum ditemukan di PATH, jadi Atri belum bisa memutar audio di voice channel.")
        return True

    if not VOICE_BACKEND_READY:
        await message.channel.send(
            "Backend voice Discord belum lengkap. Pastikan `PyNaCl` dan `davey` terpasang di environment yang dipakai saat menjalankan bot."
        )
        return True

    wav_path = None
    voice_client = None
    try:
        wav_path, _ = make_temp_audio_paths()
        wav_path = generate_tts_audio(text, wav_path)

        voice_client = await ensure_voice_recv_connection(message)
        await ensure_voice_listener(message, voice_client)

        if voice_client.is_playing():
            voice_client.stop()

        session = get_voice_session(message.guild.id)
        if session.sink is not None:
            session.sink.paused = True

        done = asyncio.get_running_loop().create_future()

        def _after_play(error):
            if done.done():
                return
            if error:
                done.set_exception(error)
            else:
                done.set_result(None)

        source = discord.FFmpegOpusAudio(
            wav_path,
            executable=FFMPEG_PATH,
            before_options="-nostdin",
            options="-vn",
        )
        voice_client.play(source, after=_after_play)
        await done
        return True
    finally:
        session = voice_sessions.get(message.guild.id)
        if session and session.sink is not None:
            session.sink.paused = False
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

async def disconnect_voice_channel(message):
    if message.author.id != int(developer_id):
        await message.channel.send("Maaf, hanya developer yang boleh memutuskan voice channel.")
        return True

    voice_client = message.guild.voice_client if message.guild else None
    if not voice_client or not voice_client.is_connected():
        await message.channel.send("Atri sedang tidak terhubung ke voice channel.")
        return True

    try:
        session = voice_sessions.get(message.guild.id)
        if session and session.sink is not None:
            session.sink.cleanup()
            session.sink = None
        if voice_client.is_playing():
            voice_client.stop()
        if hasattr(voice_client, "is_listening") and voice_client.is_listening():
            voice_client.stop_listening()
        await voice_client.disconnect()
        voice_sessions.pop(message.guild.id, None)
        await message.channel.send("Atri sudah keluar dari voice channel.")
    except Exception as e:
        await message.channel.send(f"Gagal memutus voice channel: {e}")
    return True

async def generate_llm_answer_for_discord(message, command_text, conversation, reply_language="id"):
    user_ref = message.author.name
    prompt_text = f"{user_ref} berkata {command_text}"
    conversation.append({"role": "user", "content": prompt_text})
    prune_history()
    save_conversation(conversation)

    try:
        answer = chat_completion(getPrompt(reply_language=reply_language))
    except Exception as e:
        print("Error getting Discord LLM answer:", e)
        await message.channel.send("Terjadi error saat membuat jawaban. Coba lagi nanti.")
        return None

    conversation.append({"role": "assistant", "content": answer})
    save_conversation(conversation)
    return answer

async def generate_llm_answer_from_voice(speaker_name, command_text, conversation, reply_language="ja"):
    prompt_text = f"{speaker_name} berkata {command_text}"
    conversation.append({"role": "user", "content": prompt_text})
    prune_history()
    save_conversation(conversation)

    try:
        answer = chat_completion(getPrompt(reply_language=reply_language))
    except Exception as e:
        print("Error getting Discord voice answer:", e)
        return None

    conversation.append({"role": "assistant", "content": answer})
    save_conversation(conversation)
    return answer

def get_text_channel_for_guild(guild_id):
    session = voice_sessions.get(guild_id)
    if not session or not session.text_channel_id:
        return None

    channel = client.get_channel(session.text_channel_id)
    if channel is not None:
        return channel
    return None

async def ensure_voice_recv_connection(message):
    if not VOICE_RECV_AVAILABLE:
        raise RuntimeError("discord-ext-voice-recv belum terpasang.")

    target_channel = message.author.voice.channel
    voice_client = message.guild.voice_client if message.guild else None

    if voice_client and not isinstance(voice_client, voice_recv.VoiceRecvClient):
        await voice_client.disconnect()
        voice_client = None

    if voice_client and voice_client.is_connected():
        if voice_client.channel.id != target_channel.id:
            await voice_client.move_to(target_channel)
    else:
        voice_client = await target_channel.connect(cls=voice_recv.VoiceRecvClient)

    return voice_client

async def ensure_voice_listener(message, voice_client):
    session = get_voice_session(message.guild.id)
    session.text_channel_id = message.channel.id

    if not isinstance(voice_client, voice_recv.VoiceRecvClient):
        raise RuntimeError("Voice client belum mendukung voice receive.")

    if not voice_client.is_listening():
        sink = session.sink
        if sink is None or not isinstance(sink, AtriVoiceSink):
            sink = AtriVoiceSink(message.guild.id)
            session.sink = sink
        sink._atri_voice_client = voice_client
        voice_client.listen(sink)

async def say_in_voice_channel(guild_id, text):
    session = voice_sessions.get(guild_id)
    if not session:
        return False

    guild = client.get_guild(guild_id)
    if not guild:
        return False

    voice_client = guild.voice_client
    if not voice_client:
        return False

    wav_path = None
    try:
        wav_path, _ = make_temp_audio_paths()
        wav_path = generate_tts_audio(text, wav_path)

        if voice_client.is_playing():
            voice_client.stop()

        if hasattr(session, "sink") and session.sink is not None:
            try:
                session.sink.paused = True
            except Exception:
                pass

        done = asyncio.get_running_loop().create_future()

        def _after_play(error):
            if done.done():
                return
            if error:
                done.set_exception(error)
            else:
                done.set_result(None)

        source = discord.FFmpegOpusAudio(
            wav_path,
            executable=FFMPEG_PATH,
            before_options="-nostdin",
            options="-vn",
        )
        voice_client.play(source, after=_after_play)
        await done
        return True
    finally:
        if hasattr(session, "sink") and session.sink is not None:
            try:
                session.sink.paused = False
            except Exception:
                pass
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

async def handle_voice_speech_trigger(guild_id, speaker_name, transcript):
    print(f"[Voice Trigger] Handler started: {speaker_name} -> '{transcript}'")
    session = voice_sessions.get(guild_id)
    if not session:
        print(f"[Voice Trigger] No session")
        return

    text_channel = get_text_channel_for_guild(guild_id)
    if text_channel:
        print(f"[Voice Trigger] Sending to text channel")
        await text_channel.send(f"**{speaker_name}** bilang: {transcript}")

    print(f"[Voice Trigger] Generating answer...")
    answer = await generate_llm_answer_from_voice(speaker_name, transcript, conversation, reply_language="ja")
    if not answer:
        print(f"[Voice Trigger] No answer from LLM")
        if text_channel:
            await text_channel.send("Atri gagal membuat jawaban.")
        return
    print(f"[Voice Trigger] Answer: {answer}")

    translated_text = translate_for_display(answer, "id")
    print(f"[Voice Trigger] Translation: {translated_text}")
    if translated_text and text_channel:
        await text_channel.send(translated_text)

    try:
        print(f"[Voice Trigger] Playing audio...")
        result = await say_in_voice_channel(guild_id, answer)
        print(f"[Voice Trigger] Audio played: {result}")
    except Exception as e:
        print(f"[Voice Trigger] Audio error: {e}")
        import traceback
        traceback.print_exc()
        if text_channel:
            await text_channel.send(f"Gagal membalas lewat voice channel: {e}")

def scrape_pinterest(query):
    """Mencari gambar Pinterest menggunakan DuckDuckGo dengan Query Hak Paten Anime (Akurat & Anti-Blokir)"""
    # Memaksa pencarian hanya di pinterest.com DAN menambahkan keyword spesifik agar hasilnya terfilter akurat
    search_query = f"{query}"
    try:
        with DDGS() as ddgs:
            # Mengambil hasil gambar teratas
            results = ddgs.images(search_query, region="id-id", max_results=15)
            
            if not results:
                return None
                
            image_urls = []
            for r in results:
                url = r.get("image")
                if url:
                    # Filter tambahan untuk memastikan tautan aman dan mengarah ke gambar asli
                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        image_urls.append(url)
            
            return image_urls if image_urls else None
    except Exception as e:
        print(f"[Pinterest DDGS Error]: {e}")
        return None
    
def extract_atri_command(text):
    cleaned = text.strip()
    if cleaned.lower().startswith("_atri"):
        return cleaned[len("_atri"):].lstrip(" :,-").strip()
    return None

def is_video_download_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("unduh", "download", "video")

# ---- JALUR PENANGANAN PLAY VIDEO DI TEXT CHAT ----
def is_play_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("putar", "play", "video_chat")

async def handle_play_video_in_chat(message, command_text):
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("Tolong masukkan URL videonya! Contoh: `_atri putar https://...`")
        return True
        
    url = parts[1].strip()
    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1].strip()
    
    video_extensions = ('.mp4', '.webm', '.mov', '.avi')
    is_direct_file = any(url.lower().split('?')[0].endswith(ext) for ext in video_extensions)
    
    try:
        if is_direct_file:
            embed = discord.Embed(
                title="🎬 Video Player",
                description=f"Diminta oleh: {message.author.mention}",
                color=discord.Color.blue()
            )
            embed.set_video(url=url)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"🎬 **Memutar video untuk {message.author.mention}**:\n{url}")
        return True
    except Exception as e:
        print("[Video Chat Error]:", e)
        await message.channel.send(f"Gagal memuat video di chat. Error: {e}")
        return True

# ---- FUNGSI BARU: SKENARIO B (BROWSING INTERNET VIA DUCKDUCKGO) ----
def is_search_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("cari", "search", "browsing", "google")

async def handle_cari_internet(message, command_text, conversation):
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("Mau cari info apa di internet? Contoh: `_atri cari harga rtx 4060 terbaru`")
        return True

    query = parts[1].strip()
    await message.channel.send(f"Sebentar ya, Atri tanyakan ke internet dulu tentang '{query}'... 🔍🌐")

    try:
        with DDGS() as ddgs:
            raw_results = ddgs.text(query, region="id-id", max_results=3)
            results = [r for r in raw_results] if raw_results else []

        if not results:
            await message.channel.send("Wah, Atri tidak menemukan informasi apa pun terkait hal itu di internet.")
            return True

        sumber_data = ""
        for i, r in enumerate(results, 1):
            sumber_data += f" Sumber [{i}]:\nJudul: {r.get('title', 'Tanpa Judul')}\nRingkasan: {r.get('body', '')}\n\n"

        prompt_browsing = (
            f"Kamu adalah Atri, AI yang baru saja mencari informasi di internet secara real-time.\n"
            f"Gunakan data hasil pencarian internet berikut untuk menjawab pertanyaan user.\n\n"
            f"=== HASIL PENCARIAN INTERNET ===\n{sumber_data}\n================================\n\n"
            f"Pertanyaan User: {query}\n\n"
            f"Berikan jawaban yang akurat, padat, dan natural dalam Bahasa Indonesia berdasarkan data di atas.\n"
            f"CRITICAL INSTRUCTION: Jangan pernah gunakan kata 'aku' atau 'saya'. Selalu sebut dirimu sebagai 'Atri' saat berbicara!"
        )

        conversation.append({"role": "user", "content": prompt_browsing})
        save_conversation(conversation)

        answer = chat_completion(getPrompt(reply_language="id"))

        conversation.append({"role": "assistant", "content": answer})
        save_conversation(conversation)

        await message.channel.send(answer)
        return True

    except Exception as e:
        print("[Browsing Error]:", e)
        await message.channel.send(f"Aduh maaf, Atri gagal mengakses internet. Error: {e}")
        return True

# ---- FUNGSI DOWNLOAD VIDEO BAWAAN KAMU ----
async def handle_video_download(message, command_text):
    parts = command_text.split()
    fmt = None
    url = None

    tokens = [p for p in parts if p]
    remaining = []
    for t in tokens:
        if t.startswith("+") and len(t) > 1:
            fmt = t[1:]
        elif t.lower() in ("mp3", "wav", "m4a", "hevc", "h265", "video", "download", "unduh"):
            if t.lower() in ("mp3", "wav", "m4a", "hevc", "h265"):
                fmt = t.lower()
            else:
                pass
        else:
            remaining.append(t)

    if remaining:
        url = remaining[-1]
    else:
        if len(parts) >= 2:
            url = parts[1]
            
    if not parts or parts[0].lower() not in ("unduh", "download", "video"):
        return False

    if not url:
        await message.channel.send(
            "Tolong sertakan URL video setelah perintah. Contoh: `_Atri unduh https://youtube.com/...` or `_Atri unduh +mp3 https://...`"
        )
        return True

    await message.channel.send(f"Sedang mengunduh dari URL: {url} (format: {fmt or 'default'})")

    try:
        filepath, title = download_video(url, target_format=fmt)
    except Exception as e:
        await message.channel.send(f"Gagal mengunduh video: {e}")
        return True

    if not os.path.exists(filepath):
        search_dir = os.path.dirname(filepath) if os.path.dirname(filepath) else (video_download_dir or None) or tempfile.gettempdir()
        try:
            files = os.listdir(search_dir)
        except Exception:
            files = []

        def normalize(s):
            return ''.join(ch for ch in s.lower() if ch.isalnum())

        target_key = normalize(os.path.splitext(os.path.basename(filepath))[0])
        title_key = normalize(title or "")
        candidate = None
        for f in files:
            k = normalize(os.path.splitext(f)[0])
            if title_key and (title_key in k or k in title_key):
                candidate = os.path.join(search_dir, f)
                break
            if target_key and (target_key in k or k in target_key):
                candidate = os.path.join(search_dir, f)
                break

        if candidate and os.path.exists(candidate):
            filepath = candidate
        else:
            listing = '\n'.join(files[:50]) or '(empty)'
            await message.channel.send(
                f"Video terunduh tetapi file yang dicari tidak ditemukan: {os.path.basename(filepath)}\nContents of {search_dir}:\n{listing}"
            )
            return True

    try:
        filesize_mb = os.path.getsize(filepath) / (1024 * 1024)
        if filesize_mb <= 8:
            try:
                await message.channel.send(file=discord.File(filepath, filename=os.path.basename(filepath)))
                await message.channel.send(f"Video dikirim — file tidak disimpan di server.")
            finally:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
        else:
            try:
                os.remove(filepath)
            except Exception:
                pass
            await message.channel.send(
                f"Video berhasil diunduh tetapi ukurannya {filesize_mb:.1f} MB, terlalu besar untuk dikirim via Discord dan tidak akan disimpan di server. "
                "Jika ingin menyimpan, atur `video_download_dir` di config.py ke direktori dengan ruang tersedia atau gunakan upload cloud."
            )
    except Exception as e:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        await message.channel.send(f"Video terunduh tetapi gagal mengirim file: {e}")

    return True

def is_cloud_command(command_text):
    return command_text.lower().split(maxsplit=1)[0] in ("cloud", "simpan_pc")

async def handle_cloud_download(message, command_text):
    # 1. Pengecekan Hak Akses (Hanya Developer/Pemilik Bot)
    if message.author.id != int(developer_id):
        await message.channel.send("❌ Maaf, perintah cloud ini hanya boleh diakses oleh Master pemilik PC!")
        return True

    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("⚠️ Format salah! Contoh penggunaan: `_atri cloud https://youtube.com/...`")
        return True

    url = parts[1].strip()
    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1].strip()

    # Tentukan direktori penyimpanan cloud lokal Anda
    cloud_dir = r"E:\Cloud"
    await message.channel.send(f"📥 **Memproses unduhan cloud, Master...**\nVideo akan disimpan langsung ke `{cloud_dir}`.")

    try:
        # Menjalankan fungsi download bawaan dengan memaksakan output_dir ke E:\Cloud
        # Menggunakan asyncio.to_thread agar proses download tidak membuat bot hang/freeze
        filepath, title = await asyncio.to_thread(download_video, url, output_dir=cloud_dir)
        
        if os.path.exists(filepath):
            await message.channel.send(
                f"✅ **Unduhan Berhasil, Master!**\n"
                f"📝 **Judul:** {title}\n"
                f"📂 **Lokasi File:** `{filepath}`"
            )
        else:
            await message.channel.send("⚠️ Proses selesai, tetapi file tidak terdeteksi di direktori target.")
            
    except Exception as e:
        print(f"[Cloud Download Error]: {e}")
        await message.channel.send(f"❌ Gagal mengunduh ke PC lokal. Error: `{str(e)[:100]}`")

    return True

async def handle_voice_note_command(message, command_text, conversation):
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("Tolong tambahkan teksnya. Contoh: `_atri suara halo semuanya`")
        return True

    prompt = parts[1].strip()
    await message.channel.send("Sebentar ya, Atri sedang menyiapkan voice note...")
    answer = await generate_llm_answer_for_discord(message, prompt, conversation, reply_language="ja")
    if not answer:
        return True

    try:
        translated_text = translate_for_display(answer, "id")
        if translated_text:
            if conversation and conversation[-1].get("role") == "assistant":
                conversation[-1]["content"] = translated_text
                save_conversation(conversation)
            await message.channel.send(translated_text)
        await send_voice_note_reply(message, answer)
    except Exception as e:
        print("[Discord Voice Note Error]:", e)
        await message.channel.send(f"Gagal mengirim voice note: {e}")
    return True

async def handle_voice_channel_command(message, command_text, conversation):
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("Tolong tambahkan teksnya. Contoh: `_atri vc halo semuanya`")
        return True

    prompt = parts[1].strip()
    await message.channel.send("Sebentar ya, Atri sedang masuk voice channel dan menyiapkan suaranya...")
    answer = await generate_llm_answer_for_discord(message, prompt, conversation, reply_language="ja")
    if not answer:
        return True

    try:
        translated_text = translate_for_display(answer, "id")
        if translated_text:
            if conversation and conversation[-1].get("role") == "assistant":
                conversation[-1]["content"] = translated_text
                save_conversation(conversation)
            await message.channel.send(translated_text)

        await play_voice_channel_reply(message, answer)
    except Exception as e:
        print("[Discord Voice Channel Error]:", e)
        await message.channel.send(f"Gagal bicara di voice channel: {e}")
    return True

async def handle_cover_command(message, command_text):
    """Fungsi AI Cover RVC yang Sinkron dan Benar"""
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await message.channel.send("❌ Tolong masukkan URL YouTube lagu yang ingin dicover! Contoh: `_atri cover https://youtu.be/...`")
        return True
        
    url = parts[1].strip()
    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1].strip()

    # Validasi URL dasar
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.channel.send("❌ URL harus dimulai dengan http:// atau https://")
        return True

    # Membuat progress message agar user tahu bot sedang bekerja
    progress_msg = await message.channel.send("🎵 **Atri sedang menyiapkan panggung AI Cover...**\nProses: 1/5 (Mengunduh Lagu)...")

    # Siapkan penampung file temporer berbasis UUID agar tidak tabrakan antar user
    token = uuid.uuid4().hex
    audio_path = os.path.join(tempfile.gettempdir(), f"atri_raw_{token}.wav")
    vocal_path = os.path.join(tempfile.gettempdir(), f"atri_vokal_{token}.wav")
    instrumental_path = os.path.join(tempfile.gettempdir(), f"atri_instrumen_{token}.wav")
    vocal_converted_path = os.path.join(tempfile.gettempdir(), f"atri_vokal_rvc_{token}.wav")
    final_path = os.path.join(tempfile.gettempdir(), f"atri_cover_final_{token}.wav")

    try:
        # 1. DOWNLOAD AUDIO (Menggunakan fungsi bawaan dari utils.voice_conversion)
        audio_path = await asyncio.to_thread(download_audio, url, audio_path)
        
        # 2. AUDIO SPLITTING (Memisahkan Vokal asli dengan Musik Latar)
        await progress_msg.edit(content="✂️ **AI Cover Progress**\nProses: 2/5 (Memisahkan Vokal asli dengan Musik Latar)...")
        # Fungsi separate_vocals mengembalikan tuple (vocal, instrumental)
        vocal_path, instrumental_path = await asyncio.to_thread(separate_vocals, audio_path, None, "demucs")

        # 3. VOICE CONVERSION (Proses RVC GPU)
        await progress_msg.edit(content="🎙️ **AI Cover Progress**\nProses: 3/5 (Mengonversi vokal asli menjadi karakter suara Atri)...")
        
        # Mengarahkan ke model pth Atri kamu
        rvc_model_path = os.path.join(os.getcwd(), "models", "atri_rvc_model.pth")
        if not os.path.exists(rvc_model_path):
            await progress_msg.edit(content="❌ Gagal: Model RVC Atri (`models/atri_rvc_model.pth`) tidak ditemukan!")
            cleanup([audio_path, vocal_path, instrumental_path])
            return True

        vocal_converted_path = await asyncio.to_thread(
            convert_voice_rvc,
            vocal_path,
            vocal_converted_path,
            model_path=rvc_model_path,
            f0_up_key=0  # Ubah ke 12 jika lagu cowok ingin dinaikkan ke nada cewek Atri
        )

        # 4. AUDIO MIXING (Menggabungkan vokal Atri dengan musik latar)
        await progress_msg.edit(content="🎚️ **AI Cover Progress**\nProses: 4/5 (Menggabungkan kembali vokal Atri dengan musik latar)...")
        final_path = await asyncio.to_thread(merge_audio, vocal_converted_path, instrumental_path, final_path)

        # 5. PENGIRIMAN HASIL / PLAY KE VOICE CHANNEL
        await progress_msg.edit(content="🚀 **AI Cover Progress**\nProses: 5/5 (Memasuki panggung dan mengirimkan lagu)...")

        # Cek apakah user berada di Voice Channel
        user_voice = None
        if message.guild:
            member = message.guild.get_member(message.author.id)
            if member and member.voice:
                user_voice = member.voice

        if user_voice and user_voice.channel:
            # Jika user di VC, bot masuk dan bernyanyi secara live!
            await progress_msg.edit(content=f"🎤 Atri sedang menyanyikan cover secara live di voice channel: **{user_voice.channel.name}**!")
            await play_audio_in_channel(message.guild, user_voice.channel, final_path)
        else:
            # Jika tidak di VC, kirim filenya langsung ke chat text
            if os.path.exists(final_path):
                file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
                if file_size_mb > 25: # Batasan ukuran upload Discord biasa
                    await message.channel.send(f"⚠️ Hasil cover selesai, tapi ukuran file terlalu besar ({file_size_mb:.1f}MB) untuk dikirim langsung.")
                else:
                    with open(final_path, "rb") as f:
                        await message.channel.send(
                            content=f"💡 Kamu tidak berada di voice channel, jadi Atri kirimkan file audionya di sini, Master! 🎤",
                            file=discord.File(f, filename=f"atri_cover_{token[:6]}.wav")
                        )

    except Exception as e:
        print(f"[Cover Command Error]: {e}")
        import traceback
        traceback.print_exc()
        await message.channel.send(f"❌ Terjadi error saat mengeksekusi AI Cover: `{str(e)[:100]}`")
    
    finally:
        # Bersihkan sisa file sampah di temp folder komputer agar penyimpananmu tidak bengkak
        cleanup([audio_path, vocal_path, instrumental_path, vocal_converted_path, final_path])
    
    return True

async def handle_cover_from_url(message, url):
    """Handle cover request from YouTube/URL"""
    await message.channel.send(f"🎵 Atri sedang mengunduh lagu dari URL...")
    
    try:
        # Try to extract video info using yt-dlp or similar
        # For now, use a generic approach
        import subprocess
        
        # Create temp directory for downloads
        temp_dir = os.path.join(tempfile.gettempdir(), f"atri_cover_{uuid.uuid4().hex}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Try to download using yt-dlp
        try:
            # First try to get title
            cmd = [
                "yt-dlp",
                "-e",  # Extract title only
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            title = result.stdout.strip() if result.returncode == 0 else "Unknown Song"
        except:
            title = "Unknown Song"
        
        if not title or title == "Unknown Song":
            # Fallback: try to extract from URL
            try:
                title = url.split('/')[-1].split('?')[0].replace('-', ' ').replace('_', ' ')[:50]
            except:
                title = "Cover Song"
        
        await message.channel.send(f"📥 Title: **{title}**\n✨ Membuat cover parodi untuk lagu ini...")
        
        # Generate lyrics dengan fallback
        lyric_text = generate_cover_lyrics_with_fallback(title, "Unknown", language="id")
        
        if not lyric_text:
            await message.channel.send(f"❌ Maaf, Atri tidak bisa membuat cover untuk lagu ini...")
            return True
        
        # Display the generated lyrics
        embed = discord.Embed(
            title=f"🎤 Atri's Cover: {title}",
            description=lyric_text,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Diminta oleh {message.author.name} | URL: {url[:50]}...")
        await message.channel.send(embed=embed)
        
        # Generate TTS audio
        wav_path = os.path.join(tempfile.gettempdir(), f"atri_cover_{uuid.uuid4().hex}.wav")
        wav_path = generate_tts_audio(lyric_text, wav_path)
        
        if not wav_path or not os.path.exists(wav_path):
            await message.channel.send("❌ Gagal membuat audio cover...")
            return True
        
        # Check if user is in voice channel
        user_voice = None
        if message.guild:  # Check if command is in a guild (not DM)
            try:
                member = message.guild.get_member(message.author.id)
                if member:
                    user_voice = member.voice
            except Exception as e:
                print(f"[Cover URL] Error getting member voice: {e}")
        
        if user_voice and user_voice.channel:
            await message.channel.send(f"🎵 Atri sedang membawakan cover di voice channel: **{user_voice.channel.name}**...")
            try:
                await play_audio_in_channel(message.guild, user_voice.channel, wav_path)
                await message.channel.send(f"✅ Selesai! Cover {title} sudah dibawakan Atri! 🎤")
            except Exception as e:
                await message.channel.send(f"Gagal main audio di voice channel: {e}")
                with open(wav_path, "rb") as f:
                    await message.channel.send(file=discord.File(f, filename=f"atri_cover.wav"))
        else:
            await message.channel.send(f"💡 Kamu belum masuk voice channel, jadi Atri kirimkan audio cover-nya saja!")
            try:
                with open(wav_path, "rb") as f:
                    await message.channel.send(file=discord.File(f, filename=f"atri_cover_{title[:20]}.wav"))
            except Exception as e:
                await message.channel.send(f"Gagal mengirim audio: {e}")
        
        # Cleanup
        try:
            os.remove(wav_path)
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"[Cover From URL Error]: {e}")
        import traceback
        traceback.print_exc()
        await message.channel.send(f"❌ Error saat membuat cover dari URL: {e}")
        return True

async def handle_cover_advanced_command(message, command_text):
    """Handle advanced voice conversion cover (RVC + Voice Separation)"""
    parts = command_text.split(maxsplit=1)
    
    if len(parts) < 2:
        embed = discord.Embed(
            title="🎤 Advanced Cover Song (RVC Voice Conversion)",
            description="Mengkonversi vokal lagu dengan suara Atri menggunakan AI!",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Usage",
            value="`_atri cover_advanced <URL>`\n`_atri cover_rvc <URL>`",
            inline=False
        )
        embed.add_field(
            name="Requirements",
            value="• yt-dlp\n• FFmpeg\n• Demucs\n• RVC model",
            inline=False
        )
        embed.add_field(
            name="Example",
            value="`_atri cover_advanced https://youtu.be/xxxxx`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return True
    
    url = parts[1].strip()
    
    # Validate URL
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.channel.send("❌ URL harus dimulai dengan http:// atau https://")
        return True
    
    # Check dependencies
    missing_deps = []
    if not check_dependency("yt-dlp"):
        missing_deps.append("yt-dlp")
    if not check_dependency("ffmpeg"):
        missing_deps.append("ffmpeg")
    if not check_dependency("demucs"):
        missing_deps.append("demucs")
    
    if missing_deps:
        embed = discord.Embed(
            title="❌ Dependencies Tidak Lengkap",
            description=f"Instalasi: {', '.join(missing_deps)}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Install Commands",
            value=f"```\npip install {' '.join(missing_deps)}\n```",
            inline=False
        )
        await message.channel.send(embed=embed)
        return True
    
    # Send progress message
    progress_msg = await message.channel.send(
        "🎵 **Atri sedang membuat cover lagu dengan voice conversion...**\n"
        "Proses: 0/4 (Download)\n"
        "Ini mungkin butuh beberapa menit..."
    )
    
    try:
        # Step 1: Download
        await progress_msg.edit(content="🎵 **Voice Conversion Cover**\nProses: 1/4 (Download Audio)...")
        audio_path = await asyncio.to_thread(
            download_audio,
            url,
            os.path.join(tempfile.gettempdir(), f"atri_rvc_{uuid.uuid4().hex}.wav")
        )
        print(f"[Advanced Cover] Downloaded: {audio_path}")
        
        # Step 2: Separate vocals
        await progress_msg.edit(content="🎵 **Voice Conversion Cover**\nProses: 2/4 (Pisahkan Vokal & Instrumen)...\nIni butuh ~1-2 menit...")
        vocal_path, instrumental_path = await asyncio.to_thread(
            separate_vocals,
            audio_path,
            None,
            "demucs"
        )
        print(f"[Advanced Cover] Separated - Vocal: {vocal_path}, Instrumental: {instrumental_path}")
        
        # Step 3: Convert voice (RVC)
        await progress_msg.edit(content="🎵 **Voice Conversion Cover**\nProses: 3/4 (Konversi Vokal ke Atri's Voice)...\nIni butuh ~2-3 menit...")
        
        # Check if RVC model exists
        rvc_model_path = os.path.join(os.getcwd(), "models", "atri_rvc_model.pth")
        if not os.path.exists(rvc_model_path):
            await progress_msg.edit(
                content="❌ RVC Model tidak ditemukan\n"
                "Tempatkan model di: `models/atri_rvc_model.pth`"
            )
            cleanup([audio_path, vocal_path, instrumental_path])
            return True
        
        vocal_converted_path = os.path.join(tempfile.gettempdir(), f"atri_vocal_rvc_{uuid.uuid4().hex}.wav")
        vocal_converted_path = await asyncio.to_thread(
            convert_voice_rvc,
            vocal_path,
            vocal_converted_path,
            model_path=rvc_model_path,
            f0_up_key=0
        )
        print(f"[Advanced Cover] Converted: {vocal_converted_path}")
        
        # Step 4: Merge
        await progress_msg.edit(content="🎵 **Voice Conversion Cover**\nProses: 4/4 (Gabungkan Audio)...")
        
        final_path = os.path.join(tempfile.gettempdir(), f"atri_cover_final_{uuid.uuid4().hex}.wav")
        final_path = await asyncio.to_thread(
            merge_audio,
            vocal_converted_path,
            instrumental_path,
            final_path
        )
        print(f"[Advanced Cover] Final: {final_path}")
        
        # Done! Send result
        await progress_msg.edit(content="✅ **Cover selesai!** Mengirim file...")
        
        # Send audio file
        if os.path.exists(final_path):
            file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
            
            if file_size_mb > 25:  # Discord max file size
                await message.channel.send(
                    f"⚠️ File terlalu besar ({file_size_mb:.1f}MB, max 25MB)\n"
                    f"Silakan download dari: {final_path}"
                )
            else:
                with open(final_path, "rb") as f:
                    await message.channel.send(
                        f"🎤 **Atri's Voice Cover**",
                        file=discord.File(f, filename=f"atri_cover_{uuid.uuid4().hex()[:8]}.wav")
                    )
        
        # Cleanup
        cleanup([audio_path, vocal_path, instrumental_path, vocal_converted_path, final_path])
        
        return True
    
    except Exception as e:
        print(f"[Advanced Cover Error]: {e}")
        import traceback
        traceback.print_exc()
        
        await progress_msg.edit(
            content=f"❌ Error saat membuat cover:\n```\n{str(e)[:200]}\n```"
        )
        return True

async def play_audio_in_channel(guild, voice_channel, audio_file_path):
    """Connect to voice channel and play audio"""
    voice_client = guild.voice_client
    
    # Disconnect if already connected to different channel
    if voice_client and voice_client.channel != voice_channel:
        await voice_client.disconnect()
        voice_client = None
    
    # Connect if not connected
    if not voice_client:
        voice_client = await voice_channel.connect()
    
    # Play audio
    if voice_client.is_playing():
        voice_client.stop()
    
    source = discord.FFmpegOpusAudio(
        audio_file_path,
        executable=FFMPEG_PATH,
        before_options="-nostdin"
    )
    
    done = asyncio.get_running_loop().create_future()
    
    def _after_play(error):
        if done.done():
            return
        if error:
            done.set_exception(error)
        else:
            done.set_result(None)
    
    voice_client.play(source, after=_after_play)
    await done

# Setup Intents & Client
intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load conversation
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        conversation = json.load(f).get("history", [])
except Exception:
    conversation = []

def prune_history():
    global conversation
    if len(conversation) > 40:
        conversation = conversation[-40:]

@client.event
async def on_ready():
    print(f'[Discord] Bot is ready as {client.user}')

    if not cek_game_gratis_steam.is_running():
            cek_game_gratis_steam.start()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    raw_text = None
    is_reply_to_bot = False

    if message.reference and getattr(message.reference, 'message_id', None):
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            if ref_msg and getattr(ref_msg.author, 'id', None) == client.user.id:
                raw_text = message.content.strip()
                is_reply_to_bot = True
        except Exception as e:
            print("[Discord] reply detection error:", e)

    if not raw_text:
        raw_text = message.content.strip()

    if not raw_text:
        return

    if is_reply_to_bot:
        command_text = raw_text
    else:
        command_text = extract_atri_command(raw_text)

    if not command_text:
        return

    # ====================================================================
    # ----                 SISTEM ROUTING UTAMA BOT                   ----
    # ====================================================================
    
    # 1. Pengecekan Developer (Shutdown)
    if command_text.lower() == "shutdown":
        if message.author.id == int(developer_id):
            await message.channel.send("Dimengerti, Master. Mematikan sistem...")
            await client.close()
            return
        else:
            await message.channel.send("Maaf, perintah ini hanya boleh diakses oleh Developer saya!")
            return

    if is_cloud_command(command_text):
            if await handle_cloud_download(message, command_text):
                return

    if command_text.lower().startswith("led"):
        if await handle_control_led(message, command_text):
            return

    # 2. Pengecekan Fitur Browsing Internet (Skenario B)
    if is_search_command(command_text):
        if await handle_cari_internet(message, command_text, conversation):
            return

    # 2b. Pengecekan Voice Note Discord
    if is_voice_command(command_text):
        if await handle_voice_note_command(message, command_text, conversation):
            return

    # 2c. Pengecekan Real-time Voice di Voice Channel
    if is_voice_channel_command(command_text):
        if await handle_voice_channel_command(message, command_text, conversation):
            return

    # 2c-0. Pengecekan ADVANCED Song Cover (RVC Voice Conversion) - PRIORITAS TINGGI
    if is_cover_advanced_command(command_text):
        if await handle_cover_advanced_command(message, command_text):
            return

    # 2c-1. Pengecekan Song Cover Request (Simple Parody)
    if is_cover_command(command_text):
        if await handle_cover_command(message, command_text):
            return

    # 2d. Putuskan voice channel, khusus developer
    if is_voice_disconnect_command(command_text):
        if await disconnect_voice_channel(message):
            return

    # 3. PERBAIKAN POSISI: FITUR FOTO / PINTEREST DILETAKKAN DI ATAS VIDEO DOWNLOAD
    words = command_text.lower().split()
    if words and words[0] in ("foto", "gambar", "pinterest"):
        keyword = command_text.split(maxsplit=1)[1] if len(words) > 1 else None
        
        if not keyword:
            await message.channel.send("Format salah! Contoh penggunaan: `_atri foto anime aesthetic`")
            return
            
        await message.channel.send(f"🔍 Atri sedang mencari gambar **{keyword}** di Pinterest...")
        urls = scrape_pinterest(keyword)
        
        if not urls:
            await message.channel.send("❌ Maaf, Atri tidak menemukan gambar dengan kata kunci tersebut.")
            return
            
        chosen_url = random.choice(urls)
        embed = discord.Embed(
            title=f"Hasil Pencarian: {keyword}",
            color=discord.Color.from_rgb(230, 0, 35)
        )
        embed.set_image(url=chosen_url)
        embed.set_footer(text=f"Diminta oleh {message.author.name} | Sumber: Pinterest")
        
        await message.channel.send(embed=embed)
        return

    # 4. Pengecekan Fitur Putar Video di Chat
    if is_play_command(command_text):
        if await handle_play_video_in_chat(message, command_text):
            return

    # 5. Pengecekan Fitur Unduh Video
    if await handle_video_download(message, command_text):
        return

    # ====================================================================

    # Jika hanya percakapan santai biasa, teruskan ke Ollama Llama3.2 secara offline
    answer = await generate_llm_answer_for_discord(message, command_text, conversation)
    if not answer:
        return
    await message.channel.send(answer)


def start_discord_bot(initial_conversation=None):
    """Fungsi utama yang dipanggil oleh run.py dengan membawa data conversation"""
    global conversation
    
    if initial_conversation is not None:
        conversation = initial_conversation
        
    if not discord_bot_token:
        print("[Discord] Token tidak ditemukan di config.py!")
        return
    
    print("[Discord] Menghubungkan ke server Discord...")
    client.run(discord_bot_token)

if __name__ == "__main__":
    start_discord_bot()
