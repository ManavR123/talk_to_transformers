import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, required=True, help="Which dataset to use.")
parser.add_argument("--use_gpu", action="store_true", help="Use gpu if available")
parser.add_argument("--history_length", type=int, default=200, help="Which dataset to use.")
args = parser.parse_args()

device = "cpu"
if args.use_gpu:
    if torch.cuda.is_available():
        device = "cuda"
    else:
        print("GPU NOT AVAILABLE! USING CPU")

tokenizer = AutoTokenizer.from_pretrained(args.model)
model = AutoModelForCausalLM.from_pretrained(args.model)
model.eval()
model = model.to(device)

chat_history_ids = None
while True:
    text = input(">>> ")
    new_user_input_ids = tokenizer.encode(
        text + tokenizer.eos_token, return_tensors="pt"
    ).to(device)
    bot_input_ids = (
        torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
        if chat_history_ids is not None
        else new_user_input_ids
    )
    bot_input_ids = bot_input_ids[:, -300:]
    chat_history_ids = model.generate(
        bot_input_ids, 
        max_length=1500, 
        pad_token_id=tokenizer.eos_token_id, 
        num_beams=10,
        do_sample=False,
    )
    output_text = tokenizer.decode(
        chat_history_ids[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    print(output_text)
