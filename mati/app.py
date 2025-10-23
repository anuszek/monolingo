from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

from io import BytesIO
from PIL import Image
import pytesseract
import requests
import base64


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "<h3>✅ Flask backend działa! Użyj POST /chat</h3>"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt.strip():
        return jsonify({"error": "Brak treści w wiadomości"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an English-language tutor for Polish speakers. Your primary responses should be in clear, simple English suitable for a learner. After replying in English, if the user's input contains mistakes, provide a short correction: show the corrected sentence and a brief explanation in Polish. Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences) unless the user requests more."
                },
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agent-tts', methods=['POST'])
def agent_tts():
    data = request.get_json() or {}
    message = data.get('message')
    lang = data.get('lang', 'en-US')
    if not message:
        return jsonify({'error': 'Brak pola message'}), 400

    # choose prompt by lang
    system_prompt = 'Jesteś pomocnym asystentem, odpowiadaj po polsku.'
    if str(lang).startswith('en'):
        system_prompt = (
            "You are an English-language tutor for Polish speakers. Your primary responses should be in clear, simple English suitable for a learner. After replying in English, if the user's input contains mistakes, provide a short correction: show the corrected sentence and a brief explanation in Polish. Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences) unless the user requests more."
        )

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        return jsonify({'error': 'Chat failed', 'detail': str(e)}), 502

    # TTS via OpenAI REST (configurable)
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
    TTS_VOICE = os.getenv('OPENAI_TTS_VOICE', 'alloy')
    TTS_FORMAT = os.getenv('OPENAI_TTS_FORMAT', 'mp3')
    TTS_TIMEOUT = int(os.getenv('OPENAI_TTS_TIMEOUT', '30'))

    tts_payload = {'voice': TTS_VOICE, 'input': reply, 'format': TTS_FORMAT}
    try:
        tts_resp = requests.post(
            'https://api.openai.com/v1/audio/speech',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json=tts_payload,
            stream=True,
            timeout=TTS_TIMEOUT,
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'TTS request failed', 'detail': str(e)}), 502

    if not tts_resp.ok:
        return jsonify({'error': 'TTS failed', 'detail': tts_resp.text}), 502

    content_type = tts_resp.headers.get('Content-Type', '')
    if 'audio' not in content_type:
        # Return body for debugging
        return jsonify({'error': 'TTS returned non-audio', 'content_type': content_type, 'detail': tts_resp.text}), 502

    # stream back audio with same content-type
    def generate():
        for chunk in tts_resp.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    resp = app.response_class(generate(), mimetype=content_type)
    # suggest filename for download if needed
    resp.headers['Content-Disposition'] = f'inline; filename="assistant.{TTS_FORMAT}"'
    return resp


@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    # accept file in field 'file' or 'image'
    file = None
    if 'file' in request.files:
        file = request.files['file']
    elif 'image' in request.files:
        file = request.files['image']
    else:
        return jsonify({'error': 'No file part'}), 400

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        img = Image.open(file.stream).convert('RGB')
        text = pytesseract.image_to_string(img, lang='eng+pol')
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agent-ocr-tts', methods=['POST'])
def agent_ocr_tts():
    # accept multipart form: file optional, message optional, lang optional
    lang = request.form.get('lang') or request.args.get('lang') or 'en-US'
    message = request.form.get('message') or request.args.get('message') or None
    ocr_text = None

    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            try:
                img = Image.open(file.stream).convert('RGB')
                ocr_text = pytesseract.image_to_string(img, lang='eng+pol')
            except Exception as e:
                return jsonify({'error': 'OCR failed', 'detail': str(e)}), 500

    prompt_parts = []
    if message:
        prompt_parts.append(message)
    if ocr_text:
        prompt_parts.append('\n[OCR]\n' + ocr_text)
    if not prompt_parts:
        return jsonify({'error': 'No message or file provided'}), 400

    combined = '\n\n'.join(prompt_parts)
    system_prompt = 'Jesteś pomocnym asystentem, odpowiadaj po polsku.'
    if str(lang).startswith('en'):
        system_prompt = (
            "You are an English-language tutor for Polish speakers. Your primary responses should be in clear, simple English suitable for a learner. After replying in English, if the user's input contains mistakes, provide a short correction: show the corrected sentence and a brief explanation in Polish. Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences) unless the user requests more."
        )

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': combined}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        return jsonify({'error': 'Chat failed', 'detail': str(e)}), 502

    # TTS (configurable and robust)
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
    TTS_VOICE = os.getenv('OPENAI_TTS_VOICE', 'alloy')
    TTS_FORMAT = os.getenv('OPENAI_TTS_FORMAT', 'mp3')
    TTS_TIMEOUT = int(os.getenv('OPENAI_TTS_TIMEOUT', '30'))

    tts_payload = {'voice': TTS_VOICE, 'input': reply, 'format': TTS_FORMAT}
    try:
        tts_resp = requests.post(
            'https://api.openai.com/v1/audio/speech',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json=tts_payload,
            stream=True,
            timeout=TTS_TIMEOUT,
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'TTS request failed', 'detail': str(e)}), 502

    if not tts_resp.ok:
        return jsonify({'error': 'TTS failed', 'detail': tts_resp.text}), 502

    content_type = tts_resp.headers.get('Content-Type', '')
    if 'audio' not in content_type:
        return jsonify({'error': 'TTS returned non-audio', 'content_type': content_type, 'detail': tts_resp.text}), 502

    audio_buf = BytesIO()
    for chunk in tts_resp.iter_content(chunk_size=8192):
        if chunk:
            audio_buf.write(chunk)
    audio_buf.seek(0)
    audio_b64 = base64.b64encode(audio_buf.read()).decode('utf-8')

    return jsonify({'reply': reply, 'audio_b64': audio_b64, 'ocr_text': ocr_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
