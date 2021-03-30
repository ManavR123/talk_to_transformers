from flask import Flask, jsonify, request, send_from_directory
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_url_path="", static_folder="static")
dialog_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
dialog_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
chat_history_ids = None


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/get_response_from_user_input", methods=["GET"])
def get_response():
    global chat_history_ids
    input_text = request.args.get("input_text", None)
    if not input_text:
        return jsonify({"response": "Error! No input text given.", "next_text": ""})

    logging.info(f"User input: {input_text}")
    # encode the new user input, add the eos_token and return a tensor in Pytorch
    new_user_input_ids = dialog_tokenizer.encode(
        input_text + dialog_tokenizer.eos_token, return_tensors="pt"
    )
    # append the new user input tokens to the chat history but only keep up to the last 1000 tokens
    bot_input_ids = (
        torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
        if chat_history_ids is not None
        else new_user_input_ids
    )
    bot_input_ids = bot_input_ids[:, -1000:]

    logging.info(bot_input_ids)
    logging.info(bot_input_ids.shape)
    # generated a response based on chat hisstory
    chat_history_ids = dialog_model.generate(
        bot_input_ids, max_length=1500, pad_token_id=dialog_tokenizer.eos_token_id
    )

    logging.info(chat_history_ids)
    logging.info(chat_history_ids.shape)
    # convert last output tokens to text
    output_text = dialog_tokenizer.decode(
        chat_history_ids[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    logging.info(f"DialogGPT: {output_text}")
    return jsonify({"reponse": "", "next_text": output_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, debug=True)
