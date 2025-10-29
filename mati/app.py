from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from groq import Groq  # Zmieniony import
from dotenv import load_dotenv
import os
import base64
from io import BytesIO

# Importy dla OCR i darmowego TTS
from gtts import gTTS
import pytesseract
from PIL import Image

load_dotenv()

# --- KONFIGURACJA KLIENTA GROQ ---
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Brak klucza GROQ_API_KEY w pliku .env")
client = Groq(api_key=groq_api_key)

app = Flask(__name__)
CORS(app)

# --- FUNKCJE POMOCNICZE ---

def get_system_prompt(lang='en-US'):
    """Zwraca prompt systemowy w zależności od języka. Pozostaje bez zmian."""
    if str(lang).startswith('en'):
        return (
            "You are an English-language tutor for Polish speakers. Your primary responses should be in clear, "
            "simple English suitable for a learner. After replying in English, if the user's input contains mistakes, "
            "provide a short correction: show the corrected sentence and a brief explanation in Polish. "
            "Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, "
            "give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences)."
            # Usunęliśmy fragment o obrazku, bo model go nie widzi
        )
    return 'Jesteś pomocnym asystentem, odpowiadaj po polsku.'


def get_ai_response(text_prompt, lang='en-US'):
    """Pobiera odpowiedź z modelu Groq (tylko tekst)."""
    system_prompt = get_system_prompt(lang)

    response = client.chat.completions.create(
        # Wybieramy jeden z darmowych, szybkich modeli Groq
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_prompt}
        ]
    )
    return response.choices[0].message.content


def get_tts_audio(text, stream=False):
    """Generuje audio TTS za pomocą darmowej biblioteki gTTS."""
    try:
        # Określamy język dla TTS na podstawie tekstu
        lang_code = 'pl' if any(c in 'ąćęłńóśźż' for c in text.lower()) else 'en'
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Zapisujemy audio do bufora w pamięci, aby uniknąć tworzenia plików
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_bytes = mp3_fp.read()

        if stream:
            return audio_bytes # Zwracamy bajty, Flask obsłuży strumieniowanie
        else:
            return base64.b64encode(audio_bytes).decode('utf-8')

    except Exception as e:
        print(f"Błąd podczas generowania TTS z gTTS: {e}")
        raise

# --- ENDPOINTY APLIKACJI ---

@app.route("/", methods=["GET"])
def home():
    return "<h3>✅ Backend Flask z integracją Groq działa!</h3>"


@app.route("/chat", methods=["POST"])
def chat():
    """Prosty endpoint do czatu tekstowego."""
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt.strip():
        return jsonify({"error": "Brak treści w wiadomości"}), 400

    try:
        reply = get_ai_response(text_prompt=prompt, lang='en-US')
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent-tts', methods=['POST'])
def agent_tts():
    """Endpoint, który odpowiada na tekst i zwraca audio w formie strumienia."""
    data = request.get_json() or {}
    message = data.get('message')
    lang = data.get('lang', 'en-US')
    
    if not message:
        return jsonify({'error': 'Brak pola message'}), 400

    try:
        reply = get_ai_response(text_prompt=message, lang=lang)
        audio_bytes = get_tts_audio(reply, stream=True)
        
        return Response(audio_bytes, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({'error': 'Przetwarzanie nie powiodło się', 'detail': str(e)}), 500


@app.route('/api/agent-ocr-tts', methods=['POST'])
def agent_ocr_tts():
    """Endpoint, który używa OCR do odczytu obrazu, a następnie generuje odpowiedź i audio."""
    lang = request.form.get('lang', 'en-US')
    message = request.form.get('message')
    image_file = request.files.get('file')
    ocr_text = None

    if not message and not image_file:
        return jsonify({'error': 'Nie podano wiadomości ani pliku'}), 400

    # Krok 1: OCR, jeśli jest obrazek
    if image_file:
        try:
            img = Image.open(image_file.stream).convert('RGB')
            # Używamy języka angielskiego i polskiego do rozpoznawania
            ocr_text = pytesseract.image_to_string(img, lang='eng+pol')
        except Exception as e:
            return jsonify({'error': 'OCR nie powiodło się', 'detail': str(e)}), 500

    # Krok 2: Połącz wiadomość użytkownika z tekstem z OCR
    prompt_parts = []
    if message:
        prompt_parts.append(message)
    if ocr_text:
        prompt_parts.append(f"\n\n[Tekst rozpoznany z obrazka]:\n{ocr_text}")
    
    combined_prompt = "".join(prompt_parts)

    try:
        # Krok 3: Wywołanie AI z połączonym tekstem
        reply = get_ai_response(text_prompt=combined_prompt, lang=lang)
        
        # Krok 4: Generowanie audio w base64
        audio_b64 = get_tts_audio(reply, stream=False)

        # Zwracamy odpowiedź, w tym rozpoznany tekst, aby użytkownik widział, co "zobaczył" model
        return jsonify({'reply': reply, 'audio_b64': audio_b64, 'ocr_text': ocr_text})

    except Exception as e:
        return jsonify({'error': 'Przetwarzanie nie powiodło się', 'detail': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)