import os
import warnings
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

warnings.filterwarnings("ignore", category=UserWarning, message=".*has_mps.*")

# Use a more powerful base model for future fine-tuning
MODEL_NAME = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Define summarizer pipeline (no device argument — let accelerate handle it)
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer
)

def chunk_text(text, max_token_length=1024):
    """Split long text into smaller chunks for summarization."""
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]
    chunks = []

    for i in range(0, len(input_ids), max_token_length):
        chunk_ids = input_ids[i:i + max_token_length]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunks.append(chunk_text)

    return chunks

def summarize(text, max_chunk_tokens=1024, min_length=30, max_length=150):
    """Summarize text, chunking it if needed."""
    try:
        chunks = chunk_text(text, max_chunk_tokens)
        summaries = []

        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            summaries.append(summary[0]['summary_text'])

        return " ".join(summaries)

    except Exception as e:
        raise RuntimeError(f"Summarization failed: {str(e)}")
