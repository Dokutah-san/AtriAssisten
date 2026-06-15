import requests
from config import *


def chat_completion(messages):
    provider = globals().get("llm_provider", "ollama").lower()

    if provider == "openai":
        import openai

        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=globals().get("openai_model", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=128,
            temperature=1,
            top_p=0.9,
        )
        return response["choices"][0]["message"]["content"]

    return ollama_chat(messages)


def translate_for_display(text, target_language="id"):
    target = target_language.lower()
    if target in ("none", "off", ""):
        return text
    if target in ("id", "indonesian", "indonesia"):
        language_name = "Indonesian"
    elif target in ("en", "english"):
        language_name = "English"
    else:
        language_name = target_language

    return ollama_chat([
        {
            "role": "system",
            "content": (
                "Translate the user's text into {0}. Return only the translation. "
                "Do not add explanations, quotes, labels, or extra commentary."
            ).format(language_name),
        },
        {"role": "user", "content": text},
    ], temperature=0.2, max_tokens=160)


def ollama_chat(messages, temperature=1, max_tokens=128):
    url = globals().get("ollama_url", "http://localhost:11434").rstrip("/")
    model = globals().get("ollama_model", "llama3.2:3b")

    response = requests.post(
        f"{url}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": max_tokens,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
