import os
import shutil
import torch
import requests
import urllib.parse
from utils.katakana import *
from config import *

# https://github.com/snakers4/silero-models#text-to-speech
def silero_tts(tts, language, model, speaker, output_path="test.wav"):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                    local_file)  

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "i'm fine thank you and you?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts,
                                speaker=speaker,
                                sample_rate=sample_rate)
    if isinstance(audio_paths, (list, tuple)) and audio_paths:
        generated_path = audio_paths[0]
    elif isinstance(audio_paths, str):
        generated_path = audio_paths
    else:
        generated_path = "test.wav"

    if output_path and generated_path and os.path.exists(generated_path) and os.path.abspath(generated_path) != os.path.abspath(output_path):
        shutil.copyfile(generated_path, output_path)
        return output_path

    return generated_path
    
def voicevox_tts(tts, output_path="test.wav"):
    # You need to run VoicevoxEngine.exe first before running this script
    url = globals().get("voicevox_url", "http://localhost:50021").rstrip("/")
    speaker = globals().get("voicevox_speaker", 46)
    # Convert the text to katakana. Example: ORANGE -> オレンジ, so the voice will sound more natural
    katakana_text = katakana_converter(tts)
    # You can change the voice to your liking. You can find the list of voices on speaker.json
    # or check the website https://voicevox.hiroshiba.jp
    params_encoded = urllib.parse.urlencode({'text': katakana_text, 'speaker': speaker})
    request = requests.post(f'{url}/audio_query?{params_encoded}', timeout=30)
    request.raise_for_status()
    params_encoded = urllib.parse.urlencode({'speaker': speaker, 'enable_interrogative_upspeak': True})
    request = requests.post(f'{url}/synthesis?{params_encoded}', json=request.json(), timeout=60)
    request.raise_for_status()

    with open(output_path, "wb") as outfile:
        outfile.write(request.content)

    return output_path

if __name__ == "__main__":
    silero_tts()
