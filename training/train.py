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
parser.add_argument("--use_half_precision", action="store_true", help="Use half precision")
parser.add_argument("--size", type=str, default="medium", help="Size of base model: medium or large")
parser.add_argument("--num_epochs", type=int, default=3, help="Number of epochs of training")
parser.add_argument("--learning_rate", type=float, default=1e-5, help="Learning rate.")
parser.add_argument("--optim_every", type=int, default=1, help="Learning rate.")
parser.add_argument(
    "--optimizer_name", type=str, default="adam", help="Two options: `adam` and `lamb`",
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
model = AutoModelForCausalLM.from_pretrained(f"microsoft/DialoGPT-{args.size}")
model = model.to(device)
model.parallelize()

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

def step(model, data, optimizer, device, iter_num):
    past_key_values, last_tokens = None, None
    loss = torch.tensor(0).float().to(device)
    for j, inp in enumerate(data):
        new_inputs = tokenizer([inp[0] + " " + tokenizer.eos_token], return_tensors="pt", max_length=100, truncation=True)["input_ids"].to(device)
        if j == 0:
            outputs = model(input_ids=new_inputs, use_cache=True)
        else:
            outputs = model(input_ids=new_inputs, past_key_values=past_key_values, labels=new_inputs, use_cache=True)
            loss += outputs.loss

        past_key_values = outputs.past_key_values[-100:]
    
    wandb.log({"loss": loss.item()})
    loss.backward()
    if iter_num % args.optim_every == 0:
        optimizer.step()
        optimizer.zero_grad()

model = model.train()
if args.use_half_precision:
    model = model.half()
wandb.watch(model)
for _ in tqdm(range(args.num_epochs)):
    for i, data in tqdm(enumerate(dataloader), total=len(dataloader)):
        step(model, data, optimizer, device, i)

        if i % 1000 == 0:
            model.save_pretrained(os.path.join("models", f"{args.dataset}-{args.size}"))
            tokenizer.save_pretrained(os.path.join("models", f"{args.dataset}-{args.size}"))
