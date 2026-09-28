import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

load_dotenv()
app = Flask(__name__, template_folder="templates")
MODEL_NAME = "gemini-3.1-flash-lite"
CONFIG_PATH = Path(__file__).with_name("chatbot_config.txt")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in the .env file.")
client = genai.Client(api_key=api_key)
SYSTEM_PROMPT = CONFIG_PATH.read_text(encoding="utf-8")

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Please enter a question."}), 400
    prompt = f"{SYSTEM_PROMPT}\n\nUSER QUESTION:\n{message}\n\nRespond according to the TECH BOT rules above."
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return jsonify({"reply": response.text.strip()})
    except Exception:
        return jsonify({"error": "Sorry, I could not process your question right now."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
