import json
import sys
from config import *

try:
    sys.stdout.reconfigure(encoding="utf8")
except Exception:
    pass

outputNum = 80

def getReplyInstruction(reply_language=None):
    if reply_language is None:
        reply_language = globals().get("assistant_reply_language", "en")
    reply_language = reply_language.lower()

    if reply_language in ("ja", "jp", "japanese"):
        return (
            "Understand Indonesian input and answer as Atri, not as a translator. Reply only in natural Japanese. "
            "Be calm, wise, and stable. If the input is unclear, ask the user to repeat it. "
            "Do not include romaji, Indonesian translation, furigana, or explanations."
        )
    if reply_language in ("id", "indonesian", "indonesia"):
        return (
            "Understand Indonesian input and answer as Atri in natural Indonesian. "
            "Be calm, wise, and stable. If the input is unclear, ask the user to repeat it. "
            "Do not include Japanese, romaji, or extra translations."
        )
    return "Reply in English so the local voice can speak it clearly."

def getIdentity(identityPath):  
    with open(identityPath, "r", encoding="utf-8") as f:
        identityContext = f.read()
    return {"role": "system", "content": identityContext}
    
def getPrompt(reply_language=None):
    total_len = 0
    prompt = []
    prompt.append(getIdentity("characterConfig/Pina/identity.txt"))
    # If a caller requests a specific reply language, add a high-priority
    # system message right after the identity to override the identity's
    # default language instructions (useful for Discord mode).
    if reply_language:
        rl = reply_language.lower()
        if rl in ("id", "indonesian", "indonesia"):
            prompt.append({
                "role": "system",
                "content": (
                    "Override: Reply in natural Indonesian as Atri. "
                    "Be calm, wise, and stable. If the input is unclear, ask the user to repeat it. "
                    "Do not include Japanese, romaji, or extra translations."
                ),
            })
    prompt.append({"role": "system", "content": f"Below is conversation history.\n"})

    with open("conversation.json", "r") as f:
        data = json.load(f)
    history = data["history"]
    for message in history[:-1]:
        prompt.append(message)

    prompt.append({
        "role": "system",
        "content": f"Here is the latest conversation.\n*{getReplyInstruction(reply_language)} Make sure your response is within {outputNum} characters!*\n",
    })


    prompt.append(history[-1])

    total_len = sum(len(d['content']) for d in prompt)
    
    while total_len > 4000:
        try:
            # print(total_len)
            # print(len(prompt))
            prompt.pop(2)
            total_len = sum(len(d['content']) for d in prompt)
        except:
            print("Error: Prompt too long!")

    # total_characters = sum(len(d['content']) for d in prompt)
    # print(f"Total characters: {total_characters}")

    return prompt

def getPromptForCoverLyrics(song_title, artist, language="id"):
    """
    Generate specialized prompt for cover song lyrics with examples
    Returns prompt ready for LLM
    """
    if language.lower() in ("id", "indonesian", "indonesia"):
        prompt = [
            {
                "role": "system",
                "content": "Kamu adalah Atri, assistant lucu yang membuat lirik parodi lagu yang seru dan catchy!"
            },
            {
                "role": "system",
                "content": (
                    "CONTOH lirik parodi yang bagus:\n\n"
                    "BAIT 1:\n"
                    "🎵 Dengar aku nyanyi parodi nih\n"
                    "Atri kasih lirik yang seru banget deh\n"
                    "Gaya Atri yang paling unik\n"
                    "Bikin dengar jadi tersenyum terus~\n\n"
                    "CHORUS:\n"
                    "🎵 Ini parodi dari Atri~\n"
                    "Seru dan ceria selamanya!\n"
                    "Musik yang indah dan menyenangkan\n"
                    "Jadi bahagia dengan lirik kami~\n\n"
                    "Lirik parodi yang bagus:\n"
                    "✓ Bahasa Indonesia yang mudah dipahami\n"
                    "✓ Rhyme yang terdengar alami (nih/deh, banget/terus)\n"
                    "✓ Lucu atau touching tapi tidak over\n"
                    "✓ Langsung, tanpa panjang lebar"
                )
            },
            {
                "role": "user",
                "content": f"Buat lirik parodi lagu '{song_title}' dari {artist}! Bikin lucu dan catchy seperti contoh di atas."
            },
            {
                "role": "system",
                "content": "Langsung beri liriknya saja. Format: BAIT 1:\n[lirik]\n\nCHORUS:\n[lirik]\n\nBAIT 2:\n[lirik]"
            }
        ]
        return prompt
    
    else:  # Default English
        prompt = [
            {
                "role": "system",
                "content": "You are Atri, a fun AI who creates catchy parody song lyrics!"
            },
            {
                "role": "system",
                "content": (
                    "EXAMPLE of good parody lyrics:\n\n"
                    "VERSE 1:\n"
                    "🎵 Hear me sing this parody here\n"
                    "Atri's got the fun lyrics, yay!\n"
                    "Style so unique and so clear\n"
                    "Makes everyone smile every day~\n\n"
                    "CHORUS:\n"
                    "🎵 This parody's from Atri~\n"
                    "Fun and happy forever!\n"
                    "Music so beautiful and great\n"
                    "Makes us happy with every word~\n\n"
                    "Good parody lyrics:\n"
                    "✓ Easy to understand English\n"
                    "✓ Rhymes that sound natural (here/clear, yay/day)\n"
                    "✓ Funny or touching but not over the top\n"
                    "✓ Direct, no long explanations"
                )
            },
            {
                "role": "user",
                "content": f"Write a parody for '{song_title}' by {artist}! Make it fun and catchy like the example above."
            },
            {
                "role": "system",
                "content": "Give just the lyrics. Format: VERSE 1:\n[lyrics]\n\nCHORUS:\n[lyrics]\n\nVERSE 2:\n[lyrics]"
            }
        ]
        return prompt

def generate_cover_lyrics_with_fallback(song_title, artist, language="id"):
    """
    Generate cover lyrics with fallback templates jika LLM hasil jelek
    """
    from utils.llm import chat_completion
    
    # Get optimized prompt
    prompt = getPromptForCoverLyrics(song_title, artist, language)
    
    try:
        # Try to generate lyrics dengan LLM
        lyrics = chat_completion(prompt).strip()
        
        # Validate output - check if it looks like valid lyrics
        if lyrics and len(lyrics) > 50 and '\n' in lyrics:
            return lyrics
        else:
            # LLM output terlalu pendek atau tidak valid
            return generate_fallback_lyrics(song_title, artist, language)
    
    except Exception as e:
        print(f"[Cover Lyrics] LLM error: {e}, using fallback")
        return generate_fallback_lyrics(song_title, artist, language)

def generate_fallback_lyrics(song_title, artist, language="id"):
    """
    Fallback template generator jika LLM gagal
    Generates reasonable parody lyrics dari template
    """
    import random
    
    if language.lower() in ("id", "indonesian", "indonesia"):
        # Template-based fallback untuk Bahasa Indonesia
        templates = [
            f"""🎵 BAIT 1:
Aku dengar lagu {song_title} dari {artist}
Liriknya bagus dan menyenangkan sekali
Atri kasih parodi yang seru untuk kalian
Bikin semua orang tersenyum gembira~

CHORUS:
🎵 Ini parodi lagu yang asyik!
Cover dari Atri yang lucu
Musik indah dan menyenangkan
Jadi bahagia setiap waktu~

BAIT 2:
Mendengar nyanyi dari Atri hari ini
Parodi yang bagus dan menghibur hati
Lirik yang catchy dan mudah diingat
Semua orang senang dengar lagu ini!""",

            f"""🎵 BAIT 1:
{song_title} itu lagu yang enak didengar
Dibuat jadi parodi oleh Atri
Liriknya seru, catchy, dan menghibur banget
Bikin semua orang jadi tersenyum~

CHORUS:
🎵 Lagu parodi dari Atri nih!
Seru dan ceria selamanya
Musik yang indah dan menyenangkan
Jadi bahagia dengan melodi~

BAIT 2:
Atri ada cara unik bernyanyi
Parodi lagu yang orang kenal
Liriknya baru tapi tetap enak
Dengarkan dan tertawalah bersama!""",

            f"""🎵 BAIT 1:
Nyanyi parodi lagu {song_title}
Atri buat lirik yang lucu deh
Gaya yang unik dan menyenangkan
Semua orang jadi tertawa~

CHORUS:
🎵 Ini parodi dari Atri!
Fun dan catchy terus
Lirik yang seru dan mudah diingat
Nikmati musik yang ceria!

BAIT 2:
Parodi yang Atri buat hari ini
Liriknya segar dan menghibur
Musik yang indah terdengar
Jadi bahagia setiap detik!"""
        ]
        
        return random.choice(templates)
    
    else:
        # Fallback untuk English
        templates = [
            f"""🎵 VERSE 1:
I heard the song {song_title} from {artist}
The lyrics are great and fun to hear
Atri made a funny parody for you
Makes everyone smile and laugh~

CHORUS:
🎵 This parody's from Atri!
Fun and catchy always
Music so beautiful and nice
Happy with the lyrics we share~

VERSE 2:
Hearing the song today from Atri
The parody's entertaining and cool
Lyrics that stick and fun to sing
Everyone enjoys this song!""",

            f"""🎵 VERSE 1:
{song_title} is a song to enjoy
Made into parody by Atri now
Lyrics are fun, catchy, and great
Makes all the people smile~

CHORUS:
🎵 Song parody from Atri!
Fun and happy forever
Music that's beautiful and nice
Happy with the melody~

VERSE 2:
Atri sings in a special way
Parody of the song we know
New lyrics but still sounds good
Listen and laugh with us!"""
        ]
        
        return random.choice(templates)


if __name__ == "__main__":
    prompt = getPrompt()
    print(prompt)
    print(len(prompt))
