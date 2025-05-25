from transformers import pipeline

import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=".*has_mps.*")

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    revision="a4f8f3e"
)
def summarize(text):
    """Summarize text using a distilled BART model."""
    try:
        summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        raise RuntimeError(f"Summarization failed: {str(e)}")