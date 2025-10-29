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
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

# Load .env from the same directory as this file to ensure mati/.env is read
basedir = os.path.dirname(__file__)
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)

# --- Sprawdzenie dostępności Tesseract OCR (funkcja pomocnicza) ---
def check_tesseract():
    """Try to configure pytesseract and return True if tesseract is callable.

    This reads TESSERACT_CMD from the environment (if set) so users can point
    to tesseract.exe on Windows without modifying PATH. It returns a boolean.
    """
    try:
        t_cmd = os.getenv('TESSERACT_CMD')
        if t_cmd:
            pytesseract.pytesseract.tesseract_cmd = t_cmd

        # This will raise if tesseract is not available
        _ = pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


# Evaluate availability at startup (can be re-checked at request time)
TESSERACT_AVAILABLE = check_tesseract()
if not TESSERACT_AVAILABLE:
    print('Warning: Tesseract not found or not in PATH. OCR endpoints will return an instructive error. '
          'Install Tesseract and add it to PATH or set TESSERACT_CMD in mati/.env to the full tesseract.exe path.')

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
                "You are an English teacher whose job is to hold a natural, helpful conversation in English aimed at teaching the user. "
                "Speak in clear, natural English appropriate to the user's level. Encourage the user to answer and continue the conversation. "
                "When the user makes mistakes, politely point them out: provide the corrected sentence, a short explanation of the error in simple English (and a brief note in Polish if helpful), "
                "and offer a short practice suggestion or follow-up question. If pronunciation is requested or helpful, give a concise phonetic hint (IPA or simple phonetics). "
                "Keep replies friendly, concise (2-4 sentences) and focused on teaching and practice."
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
    global TESSERACT_AVAILABLE
    lang = request.form.get('lang', 'en-US')
    message = request.form.get('message')
    image_file = request.files.get('file')
    ocr_text = None

    if not message and not image_file:
        return jsonify({'error': 'Nie podano wiadomości ani pliku'}), 400

    # Jeśli użytkownik dołącza obrazek, spróbuj ponownie sprawdzić dostępność
    # Tesseract (pozwala to na ustawienie TESSERACT_CMD w locie bez restartu).
    if image_file and not TESSERACT_AVAILABLE:
        # Re-check availability in case the user set TESSERACT_CMD or updated PATH
        if check_tesseract():
            # Update global flag so subsequent calls in this process see the change
            TESSERACT_AVAILABLE = True
        else:
            # Provide a helpful error payload including attempted command
            attempted = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
            return jsonify({
                'error': 'Tesseract OCR nie jest zainstalowany lub nie jest dostępny w PATH.',
                'help': 'Zainstaluj Tesseract i dodaj do PATH LUB ustaw TESSERACT_CMD w mati/.env na pełną ścieżkę do tesseract.exe',
                'attempted_tesseract_cmd': attempted
            }), 500

    # Krok 1: OCR, jeśli jest obrazek
    if image_file:
        try:
            img = Image.open(image_file.stream).convert('RGB')
            # Basic preprocessing to improve OCR accuracy, especially on photos/handwriting
            # 1) Convert to grayscale
            gray = ImageOps.grayscale(img)
            # 2) Resize up to make small writing clearer
            base_w, base_h = gray.size
            scale = 2 if max(base_w, base_h) < 2000 else 1
            if scale != 1:
                gray = gray.resize((base_w * scale, base_h * scale), Image.LANCZOS)
            # 3) Apply a slight sharpen filter
            gray = gray.filter(ImageFilter.MedianFilter(size=3))
            enhancer = ImageEnhance.Contrast(gray)
            gray = enhancer.enhance(1.5)
            # 4) Autocontrast to boost readability
            gray = ImageOps.autocontrast(gray)

            # Try OCR with multiple PSMs and pick the best result by average confidence.
            # This often helps with short handwritten lines.
            psm_candidates = [7, 6, 11, 3]
            best_text = None
            best_conf = -999.0
            best_psm = None
            for psm in psm_candidates:
                cfg = f'--oem 1 --psm {psm}'
                try:
                    data = pytesseract.image_to_data(gray, lang='eng+pol', config=cfg, output_type=pytesseract.Output.DICT)
                    # data['text'] is list of words; data['conf'] are confidences as strings
                    texts = [t for t in data.get('text', []) if t and t.strip()]
                    confs = [int(c) for c in data.get('conf', []) if c and c.strip() and c != '-1']
                    avg_conf = sum(confs) / len(confs) if confs else -1.0
                    candidate_text = " ".join(texts).strip()
                    # Prefer higher average confidence, break ties by longer text
                    score = avg_conf + (len(candidate_text) / 100.0)
                    if score > best_conf:
                        best_conf = score
                        best_text = candidate_text
                        best_psm = psm
                except Exception:
                    continue

            # Fallback: if best_text is empty, try the default image_to_string
            if not best_text:
                tesseract_cfg = '--oem 1 --psm 6'
                best_text = pytesseract.image_to_string(gray, lang='eng+pol', config=tesseract_cfg)
            ocr_text = best_text
            ocr_debug = {
                'best_psm': best_psm,
                'score': best_conf,
            }
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
        # Include OCR debug info to help improve recognition during development
        resp = {'reply': reply, 'audio_b64': audio_b64, 'ocr_text': ocr_text}
        if 'ocr_debug' in locals():
            resp['ocr_debug'] = ocr_debug
        return jsonify(resp)

    except Exception as e:
        return jsonify({'error': 'Przetwarzanie nie powiodło się', 'detail': str(e)}), 500


@app.route('/api/diag', methods=['GET'])
def api_diag():
    """Diagnostic endpoint to help debug Tesseract availability and config."""
    info = {
        'tesseract_available': TESSERACT_AVAILABLE,
        'tesseract_cmd': getattr(pytesseract.pytesseract, 'tesseract_cmd', None),
    }
    if TESSERACT_AVAILABLE:
        try:
            info['tesseract_version'] = str(pytesseract.get_tesseract_version())
        except Exception as e:
            info['tesseract_version_error'] = str(e)
    return jsonify(info)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)