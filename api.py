import json
import os
import requests

API_TOKEN = os.environ.get("hfapi")

API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


data = {"conversation": {"past_user_inputs": [], "generated_responses": [],}}

while True:
    text = input(">>> ")
    data = query({"inputs": {**(data["conversation"]), "text": text,},})
    data["conversation"]["past_user_inputs"] = data["conversation"]["past_user_inputs"][-1:]
    data["conversation"]["past_user_inputs"] = data["conversation"]["generated_responses"][-1:]
    print(data["generated_text"])
