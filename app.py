from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
# from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)  # Pozwala na połączenie z frontendem (np. Reactem lub HTML/JS)

# Endpoint główny: przyjmuje wiadomość użytkownika i zwraca odpowiedź ChatGPT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")

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
