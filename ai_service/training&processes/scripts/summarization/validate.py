import numpy as np
if not hasattr(np, "float"):
    np.float = float
if not hasattr(np, "int"):
    np.int = int
if not hasattr(np, "bool"):
    np.bool = bool

import json
import mlflow
from pathlib import Path
from tqdm import tqdm
import os


# Hugging Face
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Metrics
import bert_score
from moverscore_v2 import get_idf_dict, word_mover_score

# -------------------
# CONFIG
# -------------------
MODEL_PATH = os.path.abspath("/home/miriam/case-summarization-workspace/output/flan_t5_case_summarization/best_model")   
DATA_PATH = "/home/miriam/case-summarization-workspace/data/test_data1.jsonl" 
MLFLOW_TRACKING_URI = "http://localhost:5000" 
MLFLOW_EXPERIMENT = "Bert&MoverScore_Evaluation"

# -------------------
# Load Model
# -------------------
print(f"Loading model from: {MODEL_PATH}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, local_files_only=True)

summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# -------------------
# Load Data
# -------------------
print("Loading data...")
preds, refs = [], []
with open(DATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        transcript, summary = obj["transcript"], obj["summary"]
        gen = summarizer(transcript, max_length=128, min_length=30, do_sample=False)
        preds.append(gen[0]["summary_text"])
        refs.append(summary)

# -------------------
# Metrics
# -------------------
print("Computing metrics...")

# -------- COMPUTE BERTSCORE --------
print("Computing BERTScore...")
P, R, F1 = bert_score.score(preds, refs, lang="en", verbose=True)
avg_precision = P.mean().item()
avg_recall = R.mean().item()
avg_f1 = F1.mean().item()

print(f"\nBERTScore Results:\n Precision: {avg_precision:.4f}\n Recall: {avg_recall:.4f}\n F1: {avg_f1:.4f}")



# MoverScore
idf_dict_hyp = get_idf_dict(preds)
idf_dict_ref = get_idf_dict(refs)
mover_scores = word_mover_score(
    refs, preds, idf_dict_ref, idf_dict_hyp,
    stop_words=[], n_gram=1, remove_subwords=True
)
mover_avg = float(sum(mover_scores) / len(mover_scores))

# Print results
print(f"\n📊 Results:")
print(f"  MoverScore   : {mover_avg:.4f}")

# -------------------
# Log to MLflow
# -------------------

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT)

with mlflow.start_run():
    mlflow.log_param("model", MODEL_PATH)
    mlflow.log_metric("bert_precision", avg_precision)
    mlflow.log_metric("bert_recall", avg_recall)
    mlflow.log_metric("bert_f1", avg_f1)
    mlflow.log_metric("moverscore", mover_avg)

print("\n✅ Metrics logged to MLflow!")
