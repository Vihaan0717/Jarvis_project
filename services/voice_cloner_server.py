import os
import torch
from TTS.api import TTS
from flask import Flask, request, send_file
import tempfile

app = Flask(__name__)

# JARVIS Anime Voice Config
VOICE_SAMPLE = "c:/Users/anger/Desktop/JARVIS_Project/anime-voice-erin-touch-2.wav"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading XTTSv2 model on {device}...")
# Initializing TTS with XTTSv2
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("Model loaded successfully!")

@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.json
    text = data.get("text", "")
    language = data.get("language", "en")
    
    if not text:
        return {"error": "No text provided"}, 400

    output_path = os.path.join(tempfile.gettempdir(), "jarvis_voice_output.wav")
    
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speaker_wav=VOICE_SAMPLE,
        language=language
    )
    
    return send_file(output_path, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(port=8768)
