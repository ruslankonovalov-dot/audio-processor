import os
import json
import base64
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Вказуємо явно стабільну версію API v1 через http_options (якщо потрібно)
# Але спочатку спробуємо просто повну назву моделі
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def process_audio_with_gemini(file_path):
    with open(file_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """
    Проаналізуй цей аудіозапис. Зроби транскрибацію та оцінку.
    Відповідь дай СТРОГО в форматі JSON:
    {"transcript": "...", "type": "...", "score": 1, "comment": "...", "is_bad": false}
    """

    # ЗМІНА: Використовуємо повну назву 'models/gemini-1.5-flash'
    # Це знімає питання пошуку моделі в різних версіях API
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=[
            prompt,
            {"inline_data": {"data": audio_data, "mime_type": "audio/mp3"}}
        ]
    )
    
    text_response = response.text
    if "```json" in text_response:
        text_response = text_response.split("```json")[1].split("```")[0].strip()
    elif "```" in text_response:
        text_response = text_response.split("```")[1].split("```")[0].strip()
        
    return json.loads(text_response)