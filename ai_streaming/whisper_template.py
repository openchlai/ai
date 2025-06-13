# aii.py  ----------------------------------------------------
import time
import numpy as np
import torch
import .utils
import .tokenizer
import .decoding
import .mel
import .model

# model_name = "large-v3.pt" 
# model_alignment_heads = b"ABzY8gWO1E0{>%R7(9S+Kn!D~%ngiGaR?*L!iJG9p-nab0JQ=-{D1-g00"
	
model_name = "/usr/src/pt/tiny.pt" 
model_alignment_heads = b"ABzY8bu8Lr0{>%RKn9Fp%m@SkK7Kt=7ytkO"

if __name__ == "__main__":
	ts0 = time.time()
	
	device = "cuda" if torch.cuda.is_available() else "cpu" 
	fp = open(model_name, "rb")
	checkpoint = torch.load(fp, map_location=device)
	dims = ModelDimensions(**checkpoint["dims"])

	print(device)
	print(type(checkpoint))
	print(checkpoint.keys())
	print(dims)
	
	model = Whisper(dims)
	ts1 = time.time()

	model.load_state_dict(checkpoint["model_state_dict"])
	# ts2 = time.time()

	# model.set_alignment_heads(model_alignment_heads)
	# ts3 = time.time()

	# model.to(device)
	ts4 = time.time()
	diff = ts4-ts0

	print(f"------------> model ready! {ts0} {ts4} {diff}")

	# while read buf
	# transcribe ()