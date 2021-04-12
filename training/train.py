import argparse
import csv
import os
import random

import numpy as np
import torch
from torch.utils.data import DataLoader, RandomSampler
from tqdm import tqdm
import wandb
from transformers import AutoModelForCausalLM, AutoTokenizer

import utils_optim

torch.manual_seed(0)
np.random.seed(0)
random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, required=True, help="Which dataset to use.")
parser.add_argument("--use_gpu", action="store_true", help="Use gpu if available")
parser.add_argument("--size", type=str, default="medium", help="Size of base model: medium or large")
parser.add_argument("--learning_rate", type=float, default=1e-5, help="Learning rate.")
parser.add_argument(
    "--optimizer_name", type=str, default="adam", help="Two options for now: `adam` and `lamb`",
)
args = parser.parse_args()

wandb.init(project="talk_to_transformers")
wandb.config.update(args)
wandb.run.name = f"{args.dataset}-{args.size}"

device = "cpu"
if args.use_gpu:
    if torch.cuda.is_available():
        device = "cuda"
    else:
        print("GPU NOT AVAILABLE! USING CPU")

tokenizer = AutoTokenizer.from_pretrained(f"microsoft/DialoGPT-{args.size}")
model = AutoModelForCausalLM.from_pretrained(f"microsoft/DialoGPT-{args.size}").to(device)

optimizer = utils_optim.build_optimizer(
    model, optimizer_name=args.optimizer_name, learning_rate=args.learning_rate
)

path_to_dataset = path = os.path.join("data", args.dataset, "comments.csv")
with open(path_to_dataset, newline='', encoding = 'utf8') as f:
    csvread = csv.reader(f)
    dataset = list(csvread)

dataloader = DataLoader(
    dataset=dataset, batch_size=1, sampler=RandomSampler(dataset), drop_last=True,
)

model.train()
for i, data in tqdm(enumerate(dataloader)):
    past_key_values, last_tokens = None, None
    for j, inp in enumerate(data):
        new_inputs = tokenizer([inp[0] + " " + tokenizer.eos_token], return_tensors="pt")["input_ids"].to(device)
        if j == 0:
            outputs = model(input_ids=new_inputs, use_cache=True)
        else:
            outputs = model(input_ids=new_inputs, past_key_values=past_key_values, labels=new_inputs, use_cache=True)
            loss = outputs.loss
            wandb.log({"loss": loss.item()})

        past_key_values = outputs.past_key_values
    
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

model.save_pretrained(os.path.join("models", f"{args.dataset}-{args.size}"))
tokenizer.save_pretrained(os.path.join("models", f"{args.dataset}-{args.size}"))
