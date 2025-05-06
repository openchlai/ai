import json
import matplotlib.pyplot as plt
import numpy as np
from datasets import load_dataset
from evaluate import load
from transformers import pipeline, WhisperForConditionalGeneration, WhisperProcessor
import torch
import sacrebleu
from comet import download_model, load_from_checkpoint
from collections import defaultdict

# --- Config ---
LANGUAGES = {
    "lug": {"name": "Luganda", "family": "Bantu"},
    "sw_KE": {"name": "Swahili (Kenya)", "family": "Bantu"},
    "sw_TZ": {"name": "Swahili (Tanzania)", "family": "Bantu"},
    "teo": {"name": "Ateso", "family": "Nilotic"},
    "nyn": {"name": "Runyankore", "family": "Bantu"},
}

TEST_DATA_PATHS = {
    "structured": "data/01_swahili_ds/swa_eng.json",
    "unstructured": "data/01_swahili_ds/unstructured.json"
}

# --- Model Loading ---
def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = WhisperForConditionalGeneration.from_pretrained(
        "openai/whisper-large-v3"
    ).to(device)
    processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
    return model, processor

def load_nllb_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    translator = pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M",
        device=0 if device == "cuda" else -1
    )
    return translator

# --- Evaluation Metrics ---
def calculate_bleu(predictions, references):
    return sacrebleu.corpus_bleu(predictions, [references]).score

def calculate_comet(predictions, sources, references):
    model_path = download_model("Unbabel/wmt22-comet-da")
    comet_model = load_from_checkpoint(model_path)
    data = [{"src": src, "mt": pred, "ref": ref} for src, pred, ref in zip(sources, predictions, references)]
    return comet_model.predict(data, batch_size=8)["system_score"]

def calculate_wer(predictions, references):
    wer_metric = load("wer")
    return wer_metric.compute(predictions=predictions, references=references) * 100

# --- Data Loading ---
def load_test_data(file_path):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
    
    organized_data = defaultdict(list)
    if isinstance(raw_data, list):
        for item in raw_data:
            lang = item.get("language", "sw_TZ")
            organized_data[lang].append({
                "source": item["source"],
                "reference": item["reference"]
            })
        return organized_data
    return raw_data

# --- Whisper Evaluation ---
def evaluate_whisper(test_data, model, processor):
    results = defaultdict(dict)
    
    for lang, items in test_data.items():
        if lang not in LANGUAGES:
            continue
            
        sources = [item["source"] for item in items]
        references = [item["reference"] for item in items]
        predictions = []
        
        for source in sources:
            try:
                # Verify input is audio (numeric array)
                if isinstance(source, str):
                    raise ValueError("Whisper expects audio input, got text")
                
                input_features = processor(
                    source, 
                    return_tensors="pt", 
                    sampling_rate=16000
                ).input_features
                
                predicted_ids = model.generate(input_features)
                transcription = processor.batch_decode(
                    predicted_ids, 
                    skip_special_tokens=True
                )[0]
                predictions.append(transcription)
            except Exception as e:
                print(f"Whisper error processing {lang}: {str(e)}")
                predictions.append("")
        
        if predictions:
            results[lang] = {
                "BLEU": calculate_bleu(predictions, references),
                "COMET": calculate_comet(predictions, sources, references),
                "WER": calculate_wer(predictions, references)
            }
    
    return results

# --- NLLB Evaluation ---
def evaluate_nllb(test_data, translator):
    results = defaultdict(dict)
    
    for lang, items in test_data.items():
        if lang not in LANGUAGES:
            continue
            
        sources = [item["source"] for item in items]
        references = [item["reference"] for item in items]
        predictions = []
        
        for source in sources:
            try:
                # Verify input is text
                if not isinstance(source, str):
                    source = str(source)
                
                translation = translator(
                    source, 
                    src_lang="eng_Latn", 
                    tgt_lang=f"{lang}_Latn"
                )[0]["translation_text"]
                predictions.append(translation)
            except Exception as e:
                print(f"NLLB error translating to {lang}: {str(e)}")
                predictions.append("")
        
        if predictions:
            results[lang] = {
                "BLEU": calculate_bleu(predictions, references),
                "COMET": calculate_comet(predictions, sources, references)
            }
    
    return results

# --- Main Execution ---
def main():
    # Load data
    test_data = {}
    for data_type, path in TEST_DATA_PATHS.items():
        try:
            data = load_test_data(path)
            test_data.update(data)
        except Exception as e:
            print(f"Error loading {path}: {str(e)}")
    
    if not test_data:
        raise ValueError("No test data loaded")
    
    # Load models
    whisper_model, whisper_processor = load_whisper_model()
    nllb_translator = load_nllb_model()
    
    # Evaluate
    print("Evaluating Whisper...")
    whisper_results = evaluate_whisper(test_data, whisper_model, whisper_processor)
    
    print("\nEvaluating NLLB...")
    nllb_results = evaluate_nllb(test_data, nllb_translator)
    
    # Combine and save results
    final_results = {
        "Whisper": whisper_results,
        "NLLB": nllb_results
    }
    
    with open("results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print("Evaluation complete! Results saved to 'results.json'")

if __name__ == "__main__":
    main()