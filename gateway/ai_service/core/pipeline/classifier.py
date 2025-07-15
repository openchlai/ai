import os
import re
import json
import yaml
import torch
import numpy as np
import torch.nn as nn
from importlib.resources import files
from transformers import (
    AutoTokenizer,
    DistilBertPreTrainedModel,
    DistilBertModel,
    logging
)

# === Suppress warnings and enforce offline mode ===
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_CACHE"] = os.path.abspath("./models/cache")  # Ensure local cache
logging.set_verbosity_error()

# === Load model config ===
try:
    config_path = os.getenv("MODEL_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config_file = files("ai_service").joinpath("config/model_config.yaml")
        with config_file.open("r") as f:
            config = yaml.safe_load(f)
except Exception as e:
    raise RuntimeError(f"Could not load model config: {e}")

# === Extract classifier model config ===
model_config = config.get("multitask_distilbert", {})
model_root_path = os.path.abspath(model_config.get("path", ""))
base_model_path = os.path.join(model_root_path, "multitask_distilbert")

print(f"Using classifier model path: {base_model_path}")
if not os.path.exists(base_model_path):
    raise FileNotFoundError(f"Classifier model path not found: {base_model_path}")

# === Verify required files ===
required_files = [
    "config.json", "model.safetensors", "tokenizer.json",
    "tokenizer_config.json", "vocab.txt", "special_tokens_map.json"
]
missing = [f for f in required_files if not os.path.exists(os.path.join(base_model_path, f))]
if missing:
    raise FileNotFoundError(f"Missing model files in {base_model_path}: {missing}")

# === Load label mappings from the parent folder ===
try:
    with open(os.path.join(model_root_path, "main_categories.json")) as f:
        main_categories = json.load(f)
    with open(os.path.join(model_root_path, "sub_categories.json")) as f:
        sub_categories = json.load(f)
    with open(os.path.join(model_root_path, "interventions.json")) as f:
        interventions = json.load(f)
    with open(os.path.join(model_root_path, "priorities.json")) as f:
        priorities = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load category mapping files: {e}")

# === Define the MultiTaskDistilBert model ===
class MultiTaskDistilBert(DistilBertPreTrainedModel):
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
        self.dropout = nn.Dropout(config.dropout)
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None,
                main_category_id=None, sub_category_id=None,
                intervention_id=None, priority_id=None):
        distilbert_output = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        pooled_output = distilbert_output.last_hidden_state[:, 0]
        pooled_output = self.pre_classifier(pooled_output)
        pooled_output = nn.ReLU()(pooled_output)
        pooled_output = self.dropout(pooled_output)

        logits_main = self.classifier_main(pooled_output)
        logits_sub = self.classifier_sub(pooled_output)
        logits_interv = self.classifier_interv(pooled_output)
        logits_priority = self.classifier_priority(pooled_output)

        loss = None
        if main_category_id is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_main = loss_fct(logits_main, main_category_id)
            loss_sub = loss_fct(logits_sub, sub_category_id)
            loss_interv = loss_fct(logits_interv, intervention_id)
            loss_priority = loss_fct(logits_priority, priority_id)
            loss = loss_main + loss_sub + loss_interv + loss_priority

        return (loss, logits_main, logits_sub, logits_interv, logits_priority) if loss else \
               (logits_main, logits_sub, logits_interv, logits_priority)

# === Load tokenizer and model ===
tokenizer = AutoTokenizer.from_pretrained(
    base_model_path,
    local_files_only=True,
    trust_remote_code=False
)
model = MultiTaskDistilBert.from_pretrained(
    base_model_path,
    num_main=len(main_categories),
    num_sub=len(sub_categories),
    num_interv=len(interventions),
    num_priority=len(priorities),
    local_files_only=True,
    trust_remote_code=False
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# === Inference function ===
def classify_case(narrative: str):
    text = narrative.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)

    inputs = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors="pt"
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits_main, logits_sub, logits_interv, logits_priority = model(**inputs)

    preds_main = np.argmax(logits_main.cpu().numpy(), axis=1)[0]
    preds_sub = np.argmax(logits_sub.cpu().numpy(), axis=1)[0]
    preds_interv = np.argmax(logits_interv.cpu().numpy(), axis=1)[0]
    preds_priority = np.argmax(logits_priority.cpu().numpy(), axis=1)[0]

    return {
        "main_category": main_categories[preds_main],
        "sub_category": sub_categories[preds_sub],
        "intervention": interventions[preds_interv],
        "priority": priorities[preds_priority]
    }
