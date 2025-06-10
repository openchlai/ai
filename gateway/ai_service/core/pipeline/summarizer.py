import os
import warnings
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import gc

warnings.filterwarnings("ignore", category=UserWarning, message=".*has_mps.*")

MODEL_NAME = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")

def chunk_text(text, max_token_length=1024):
    """Split long text into smaller token-length chunks for summarization."""
    # Create temporary tokenizer for chunking
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=False)
        input_ids = inputs["input_ids"][0]
        chunks = []

        for i in range(0, len(input_ids), max_token_length):
            chunk_ids = input_ids[i:i + max_token_length]
            chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
            chunks.append(chunk_text)

        return chunks
    finally:
        del tokenizer
        gc.collect()

def summarize(text, max_chunk_tokens=1024, min_length=30, max_length=150):
    """Safely summarize text with optional chunking and fallback error handling."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string.")

    # Load fresh model and tokenizer for each request
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Create summarizer pipeline
    summarizer = pipeline(
        "summarization",
        model=model,
        tokenizer=tokenizer,
        device=0 if device.type == "cuda" else -1
    )

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
            
            # Clean up intermediate results
            del summary

        return " ".join(summaries)

    except RuntimeError as e:
        if "CUDA error: device-side assert triggered" in str(e):
            # Retry on CPU if CUDA failed
            model_cpu = model.cpu()
            cpu_summarizer = pipeline(
                "summarization",
                model=model_cpu,
                tokenizer=tokenizer,
                device=-1
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
                del summary
            
            del cpu_summarizer
            return " ".join(summaries)

        raise RuntimeError(f"Summarization failed: {str(e)}")
    
    finally:
        # CRITICAL: Clean up all resources
        del summarizer
        
        # Move model to CPU then delete
        model.cpu()
        del model
        del tokenizer
        
        # Force GPU cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        gc.collect()
        print("Summarizer GPU memory cleaned up")  # For debugging