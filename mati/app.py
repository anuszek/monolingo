from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os


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
    prompt = data.get("prompt", "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")

    if not prompt.strip():
        return jsonify({"error": "Brak treści w wiadomości"}), 400

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
