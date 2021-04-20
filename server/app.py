import os
import json

from flask import Flask, jsonify, request, send_from_directory
import requests


app = Flask(__name__, static_url_path="", static_folder="static")
API_TOKEN = os.environ.get("hfapi")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/get_response_from_user_input", methods=["POST"])
def get_response_from_user_input():
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    data = json.dumps({
        "inputs": request.json.get("inputs")
    })
    response = requests.request("POST", request.json.get("url"), headers=headers, data=data)
    next_text = response.get("generated_text")
    return jsonify({next_text})
     


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, debug=True)
