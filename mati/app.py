from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# Wczytaj zmienne środowiskowe (np. klucz API)
load_dotenv()

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
CORS(app)  # Pozwala na połączenie z frontendem (HTML/React)

# Endpoint testowy
@app.route("/", methods=["GET"])
def home():
    return "<h3>✅ Serwer ChatGPT API działa! Użyj endpointu POST /chat.</h3>"

# Główny endpoint czatu
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt.strip():
            return jsonify({"error": "Brak treści w wiadomości"}), 400

        # Zapytanie do modelu OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # możesz zmienić na "gpt-4o" lub inny
            messages=[{"role": "user", "content": prompt}],
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Błąd: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
