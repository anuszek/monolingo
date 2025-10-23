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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
