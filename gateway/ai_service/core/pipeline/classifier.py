# core/pipeline/classifier.py

import re
import torch
import numpy as np

def classify_case(narrative, model, tokenizer, device, label_maps):
    text = narrative.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)

    inputs = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        logits_main, logits_sub, logits_interv, logits_priority = model(**inputs)

    return {
        "main_category": label_maps["main_categories"][np.argmax(logits_main.cpu().numpy())],
        "sub_category": label_maps["sub_categories"][np.argmax(logits_sub.cpu().numpy())],
        "intervention": label_maps["interventions"][np.argmax(logits_interv.cpu().numpy())],
        "priority": label_maps["priorities"][np.argmax(logits_priority.cpu().numpy())]
    }
