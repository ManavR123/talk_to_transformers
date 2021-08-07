import base64
import json
import os
import struct
import sys
import wave
from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from flask import Flask, jsonify, request, send_file, send_from_directory
from scipy.io.wavfile import write

from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder

app = Flask(__name__, static_url_path="", static_folder="static")
API_TOKEN = os.environ.get("hfapi")
DEBUG = os.environ.get("DEBUG", False)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/get_response_from_user_input", methods=["POST"])
def get_response_from_user_input():
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    data = json.dumps({"inputs": request.json.get("inputs")})
    response = requests.request("POST", request.json.get("url"), headers=headers, data=data)
    response = json.loads(response.content.decode("utf-8"))
    next_text = response.get("generated_text")
    return jsonify({"next_text": next_text})


@app.route("/get_sound_from_text", methods=["GET", "POST"])
def get_sound_from_text():
    filename = "output.wav"
    if request.method == "POST":
        input_text = request.json.get("input")
        if not input_text:
            return jsonify({"next_text": "hello"})

        rate = synthesizer.sample_rate

        specs = synthesizer.synthesize_spectrograms([input_text], [embeds])
        generated_wav = vocoder.infer_waveform(specs[0])
        generated_wav = np.pad(generated_wav, (0, rate), mode="constant")
        generated_wav = encoder.preprocess_wav(generated_wav)

        if len(generated_wav.shape) == 1:
            nchan = 1
        elif len(generated_wav.shape) == 2:
            nchan = generated_wav.shape[0]
            generated_wav = generated_wav.T.ravel()

        scaled = np.int16(generated_wav / np.max(np.abs(generated_wav)) * 32767).tolist()
        fp = BytesIO()
        waveobj = wave.open(fp, mode="wb")
        waveobj.setnchannels(nchan)
        waveobj.setframerate(rate)
        waveobj.setsampwidth(2)
        waveobj.setcomptype("NONE", "NONE")
        waveobj.writeframes(b"".join([struct.pack("<h", x) for x in scaled]))
        val = fp.getvalue()
        waveobj.close()
        src = base64.b64encode(val).decode("ascii")
        return jsonify({"src": src})


if __name__ == "__main__":
    dir = "voice_cloning"
    if DEBUG:
        dir = os.path.join("server", dir)
    sys.path.append(dir)

    encoder.load_model(Path(os.path.join(dir, "encoder", "saved_models", "pretrained.pt")))
    synthesizer = Synthesizer(Path(os.path.join(dir, "synthesizer", "saved_models", "pretrained/pretrained.pt")))
    vocoder.load_model(Path(os.path.join(dir, "vocoder", "saved_models", "pretrained/pretrained.pt")))

    default_sound = os.path.join("samples", "default.mp3")
    if DEBUG:
        default_sound = os.path.join("server", default_sound)
    preprocessed_wav = encoder.preprocess_wav(default_sound)
    embeds = encoder.embed_utterance(preprocessed_wav)
    app.run(host="0.0.0.0", threaded=True, debug=DEBUG)
