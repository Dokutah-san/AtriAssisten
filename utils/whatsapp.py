import json
import re
import requests
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from config import *
from utils.llm import chat_completion
from utils.promptMaker import getPrompt
from utils.TTS import *

_whatsapp_server = None
_whatsapp_message_handler = None


def set_whatsapp_message_handler(handler):
    global _whatsapp_message_handler
    _whatsapp_message_handler = handler


def normalize_phone(phone_number):
    if phone_number.startswith("whatsapp:"):
        phone_number = phone_number[len("whatsapp:"):]
    return phone_number.strip().lstrip("+")


def send_whatsapp_message(to_phone, text):
    if not whatsapp_phone_number_id or not whatsapp_access_token:
        raise ValueError("WhatsApp configuration is missing in config.py")

    to_phone = normalize_phone(to_phone)
    url = f"https://graph.facebook.com/v17.0/{whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text},
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        normalized_path = re.sub(r'/+', '/', parsed.path)
        print(f"[WhatsApp] GET {self.path} -> normalized {normalized_path}")
        if normalized_path != whatsapp_webhook_path:
            self.send_response(404)
            self.end_headers()
            return

        query = parse_qs(parsed.query)
        mode = query.get("hub.mode", [""])[0]
        challenge = query.get("hub.challenge", [""])[0]
        token = query.get("hub.verify_token", [""])[0]

        if mode == "subscribe" and token == whatsapp_webhook_verify_token:
            print("[WhatsApp] Verification request accepted")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode())
        else:
            print("[WhatsApp] Verification request rejected")
            self.send_response(403)
            self.end_headers()

    def do_POST(self):
        normalized_path = re.sub(r'/+', '/', self.path)
        if normalized_path != whatsapp_webhook_path:
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            payload = json.loads(body)
            print("[WhatsApp] POST payload:", json.dumps(payload, ensure_ascii=False))
            handle_whatsapp_payload(payload)
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print("WhatsApp webhook error:", e)

    def log_message(self, format, *args):
        return


def handle_whatsapp_payload(payload):
    if not isinstance(payload, dict):
        return

    entry = payload.get("entry", [])
    for item in entry:
        changes = item.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                continue

            for message in messages:
                sender = message.get("from")
                text = None
                if message.get("type") == "text":
                    text = message["text"].get("body")
                elif message.get("type") == "button":
                    text = message["button"].get("text")
                elif message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        text = interactive["button_reply"].get("title")

                # Deteksi pesan grup (heuristik) dan abaikan jika diatur di config
                is_group = False
                try:
                    if isinstance(sender, str):
                        if sender.endswith("@g.us") or "-" in sender:
                            is_group = True
                    # some payloads include interactive/context/group indicators
                    if message.get("context") and message["context"].get("group_id"):
                        is_group = True
                except Exception:
                    is_group = False

                if is_group and globals().get("whatsapp_ignore_group_messages", False):
                    # skip group messages
                    print(f"Ignoring group message from {sender}")
                    continue

                if sender and text and _whatsapp_message_handler:
                    threading.Thread(
                        target=_whatsapp_message_handler,
                        args=(sender, text),
                        daemon=True,
                    ).start()


def reply_to_whatsapp_message(conversation, sender, text):
    conversation.append({"role": "user", "content": f"{sender} berkata {text}"})
    prompt = getPrompt()
    try:
        reply = chat_completion(prompt)
    except Exception as e:
        print("Error getting WhatsApp LLM answer:", e)
        return

    conversation.append({"role": "assistant", "content": reply})
    try:
        send_whatsapp_message(sender, reply)
    except Exception as e:
        print("Error sending WhatsApp reply:", e)

    try:
        if tts_engine == "voicevox":
            voicevox_tts(reply)
        else:
            silero_tts(reply, tts_language, tts_model, tts_speaker)
    except Exception as e:
        print("Error playing WhatsApp answer locally:", e)


def start_whatsapp_webhook_server():
    global _whatsapp_server
    server_address = ("", whatsapp_webhook_port)
    _whatsapp_server = ThreadingHTTPServer(server_address, WhatsAppWebhookHandler)
    print(f"WhatsApp webhook server running on port {whatsapp_webhook_port} path {whatsapp_webhook_path}")
    _whatsapp_server.serve_forever()
