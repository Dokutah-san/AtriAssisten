from faster_whisper import WhisperModel
from config import *
import audioop
import wave


_local_model = None


def get_audio_stats(file):
    with wave.open(file, "rb") as audio:
        frames = audio.readframes(audio.getnframes())
        duration = audio.getnframes() / float(audio.getframerate())
        rms = audioop.rms(frames, audio.getsampwidth()) if frames else 0
    return duration, rms


def transcribe_local_audio(
    file,
    *,
    min_duration=None,
    min_rms=None,
    model=None,
    device=None,
    compute_type=None,
    download_root=None,
    beam_size=5,
    vad_filter=True,
    no_speech_threshold=None,
    max_no_speech_prob=None,
    min_avg_logprob=None,
    language=None,
):
    global _local_model

    duration, rms = get_audio_stats(file)
    min_duration = whisper_min_duration if min_duration is None else min_duration
    min_rms = whisper_min_rms if min_rms is None else min_rms
    no_speech_threshold = whisper_no_speech_threshold if no_speech_threshold is None else no_speech_threshold
    max_no_speech_prob = whisper_max_no_speech_prob if max_no_speech_prob is None else max_no_speech_prob
    min_avg_logprob = whisper_min_avg_logprob if min_avg_logprob is None else min_avg_logprob

    if duration < min_duration:
        print("Audio too short: {0:.2f}s".format(duration))
        return ""
    if rms < min_rms:
        print("Audio too quiet/noisy: RMS {0}".format(rms))
        return ""

    if _local_model is None:
        _local_model = WhisperModel(
            model or whisper_model,
            device=device or whisper_device,
            compute_type=compute_type or whisper_compute_type,
            download_root=download_root or whisper_model_dir,
        )

    language = language if language is not None else (globals().get("whisper_language", None) or None)
    segments, _info = _local_model.transcribe(
        file,
        beam_size=beam_size,
        language=language,
        vad_filter=vad_filter,
        condition_on_previous_text=False,
        no_speech_threshold=no_speech_threshold,
    )
    texts = []
    for segment in segments:
        text = segment.text.strip()
        if segment.no_speech_prob > max_no_speech_prob:
            print("Ignored uncertain speech: no_speech_prob {0:.2f}".format(segment.no_speech_prob))
            continue
        if segment.avg_logprob < min_avg_logprob:
            print("Ignored uncertain speech: avg_logprob {0:.2f}".format(segment.avg_logprob))
            continue
        if text:
            texts.append(text)
    return " ".join(texts).strip()
