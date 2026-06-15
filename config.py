llm_provider = "ollama"

# Dipakai kalau llm_provider = "ollama".
# Install Ollama, lalu jalankan: ollama pull llama3.2:3b
ollama_url = "http://localhost:11434"
ollama_model = "qwen2.5:3b"

# Dipakai untuk Mode 1 - Mic. Model tersimpan di drive E.
stt_provider = "local"
whisper_model = "small"
whisper_model_dir = "E:/WhisperModels"
whisper_device = "cuda"
whisper_compute_type = "float16"
whisper_language = "id"
whisper_min_duration = 1.0
whisper_min_rms = 120
whisper_no_speech_threshold = 0.6
whisper_max_no_speech_prob = 0.45
whisper_min_avg_logprob = -0.7

# Mode Discord Voice Channel
# Model yang dipakai khusus untuk transkripsi voice channel.
discord_voice_whisper_model = "small"
discord_voice_min_duration = 0.4
discord_voice_min_rms = 20
discord_voice_last_wav = "discord_voice_last.wav"
discord_voice_keep_last_wav = True
discord_voice_listener_enabled = True
# Toleransi threshold lebih tinggi untuk discord voice (lingkungan lebih bising)
discord_voice_no_speech_threshold = 0.6
discord_voice_max_no_speech_prob = 0.8
discord_voice_min_avg_logprob = -1.8
discord_voice_language = "id"  # Set to Bahasa Indonesia for proper recognition

# Mode 4 - always-on mic. Naikkan nilai ini kalau ruangan/mic berisik.
mic_rate = 16000
mic_chunk = 1024
always_on_calibration_seconds = 1.5
always_on_noise_multiplier = 3.0
always_on_min_rms = 350
always_on_end_silence_seconds = 1.0
always_on_min_record_seconds = 1.2
always_on_max_record_seconds = 12.0
always_on_preroll_seconds = 0.35

# Pilihan jawaban dan suara.
assistant_reply_language = "ja"
terminal_answer_language = "id"
tts_engine = "voicevox"

# ============================================================
# GPU ACCELERATION SETTINGS (RTX 3050)
# ============================================================
# Enable GPU for voice conversion tasks (Demucs, RVC)
enable_gpu_acceleration = True  # Set to False to force CPU-only

# Device selection: "cuda" for NVIDIA GPU, "cpu" for CPU
gpu_device = "cuda"

# ============================================================
# VOICE CONVERSION (RVC) SETTINGS
# ============================================================
# Path to RVC model file (.pth)
rvc_model_path = "models/atri_rvc_model.pth"

# Path to RVC index file (.index) - optional but recommended
rvc_index_path = "models/atri_rvc_index.index"

# RVC inference parameters
rvc_speaker_id = 0  # Speaker ID in the model (usually 0)
rvc_f0_up_key = 0  # Pitch shift: -12 to 12 (0 = original pitch)
rvc_filter_radius = 3  # Filter radius for smoothing (0-10, higher = smoother)
rvc_resample_sr = 0  # Resample SR (0 = auto)
rvc_rms_mix_rate = 0.25  # Vocal loudness mix rate (0-1)
rvc_protect = 0.33  # Protect voiceless consonants (0-1)

# ============================================================
# VOICE SEPARATION SETTINGS
# ============================================================
# Engine for voice separation: "demucs" or "uvr"
voice_separation_engine = "demucs"

# Demucs model: "htdemucs" (recommended), "mdx" for faster
demucs_model = "htdemucs"

# Dipakai untuk suara Jepang lokal VoiceVox.
voicevox_url = "http://localhost:50021"
voicevox_speaker = 46

# Dipakai kalau tts_engine = "silero".
tts_language = "en"
tts_model = "v3_en"
tts_speaker = "en_21"

# Opsional. Hanya dipakai kalau llm_provider = "openai".
api_key = ""

# Konfigurasi WhatsApp (Facebook/Meta WhatsApp Cloud API)
# Pastikan ini adalah Phone Number ID, bukan nomor telepon biasa.
# Phone Number ID bisa dilihat di WhatsApp Cloud API dashboard, bukan format +62xxxx.
whatsapp_phone_number_id = "1087395271130336"
whatsapp_access_token = "EAAOWuLY2UZBoBRmI5VErLfPZAbwoVVAOtAgDxBoUrXLBSm2Ag7g204LEbctQgSoDoiAdxHTqCj89t6jlnu2fclAhZApcseTHjgZBTbJx2417ZC3QMdcztHFz5FhTtXpernWlav11hcseUeofTynvwSQWEZCZCoNlKyiRNZCbpgwssp6gJGMkYOBnQYyoNVuQGwZDZD"
whatsapp_webhook_port = 5005
whatsapp_webhook_path = "/webhook"
whatsapp_webhook_verify_token = "AtriAssisten"
# Jika True, pesan dari grup akan diabaikan (tidak dibalas)
whatsapp_ignore_group_messages = True

# Discord bot configuration
# Create a bot token in Discord Developer Portal and paste it here.
discord_bot_token = "MTUxMDIzOTAxNzg1NjI3NDUxMw.GkhmmH.1d8KLf9QFiXRFj4MVcZVa45cb4nhzAQsh2-67E"
developer_id = "904628805400952862"
# Video download settings for Discord downloader
# If empty, downloader will use the system temporary directory (not the project folder).
video_download_dir = ""  # e.g. "D:/video_store" or "" to use system temp
# Retention in days for downloaded files (optional cleanup feature)
video_retention_days = 7
