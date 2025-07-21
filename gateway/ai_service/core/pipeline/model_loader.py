# core/pipeline/model_loader.py
import os
import yaml
import torch
import logging
import json
from pathlib import Path
from importlib.resources import files
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification
from core.utils.path_resolver import resolve_model_path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def load_model_config():
    """
    Loads the model configuration YAML file from environment variable or package.
    """
    try:
        config_path = os.getenv("MODEL_CONFIG_PATH")
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        else:
            config_file = files("ai_service").joinpath("config/model_config.yaml")
            with config_file.open("r") as f:
                config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise RuntimeError(f"Could not load model config: {e}")


def load_hf_model_and_tokenizer(model_key):
    config = load_model_config()
    if model_key not in config:
        raise KeyError(f"Model key not found in config: {model_key}")

    model_cfg = config[model_key]
    model_path = resolve_model_path(model_cfg["path"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    logger.info(f"[{model_key}] Loading model from {model_path} on device: {device}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)

    # Custom model handling
    if model_key in ["classifier_model", "multitask_distilbert"]:
        # For multitask_distilbert, labels are in the same directory as the model
        if model_key == "multitask_distilbert":
            label_path = model_path
        else:
            label_path = resolve_model_path(model_cfg["label_path"])

        with open(os.path.join(label_path, "main_categories.json")) as f:
            main_categories = json.load(f)
        with open(os.path.join(label_path, "sub_categories.json")) as f:
            sub_categories = json.load(f)
        with open(os.path.join(label_path, "interventions.json")) as f:
            interventions = json.load(f)
        with open(os.path.join(label_path, "priorities.json")) as f:
            priorities = json.load(f)

        model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=len(main_categories) + len(sub_categories) + len(interventions) + len(priorities)
        ).to(device)

        return model, tokenizer, device, {
            "main_categories": main_categories,
            "sub_categories": sub_categories,
            "interventions": interventions,
            "priorities": priorities
        }

    # Default HF model class
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
    return model, tokenizer, device
