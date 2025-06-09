import os
import warnings
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

warnings.filterwarnings("ignore", category=UserWarning, message=".*has_mps.*")

MODEL_NAME = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")

# Load tokenizer and model without specifying device
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Create summarizer pipeline (no device argument)
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer
)

def chunk_text(text, max_token_length=1024):
    """Split long text into smaller token-length chunks for summarization."""
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]
    chunks = []

    for i in range(0, len(input_ids), max_token_length):
        chunk_ids = input_ids[i:i + max_token_length]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunks.append(chunk_text)

    return chunks

def summarize(text, max_chunk_tokens=1024, min_length=30, max_length=150):
    """Safely summarize text with optional chunking and fallback error handling."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string.")

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

    except RuntimeError as e:
        if "CUDA error: device-side assert triggered" in str(e):
            # Retry on CPU if CUDA failed (rebuild pipeline without device param)
            cpu_summarizer = pipeline(
                "summarization",
                model=model.cpu(),
                tokenizer=tokenizer
            )
            summaries = []
            for chunk in chunks:
                summary = cpu_summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])
            return " ".join(summaries)

        raise RuntimeError(f"Summarization failed: {str(e)}")
