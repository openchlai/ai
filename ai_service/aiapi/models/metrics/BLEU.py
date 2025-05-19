# from translate.translation import translate_file
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction

def compute_bleu_score(reference_file: str, candidate_file: str) -> float:
    """
    Computes BLEU score between a reference file and a candidate file.
    
    Args:
        reference_file (str): Path to the file containing the correct (human-translated) sentences.
        candidate_file (str): Path to the file containing the model-generated translations.
        
    Returns:
        float: BLEU score between 0 and 1.
    """
    # Read reference file
    try:
        with open(reference_file, 'r', encoding='utf-8') as ref_file:
            references = [[line.strip()] for line in ref_file.readlines()]
    except FileNotFoundError:
        print(f"Error: Reference file '{reference_file}' not found")
        return 0.0
    except Exception as e:
        print(f"Error reading reference file: {e}")
        return 0.0

    # Read candidate file
    try:
        with open(candidate_file, 'r', encoding='utf-8') as cand_file:
            candidates = [line.strip() for line in cand_file.readlines()]
    except FileNotFoundError:
        print(f"Error: Candidate file '{candidate_file}' not found")
        return 0.0
    except Exception as e:
        print(f"Error reading candidate file: {e}")
        return 0.0

    # Compute BLEU score
    smoothie = SmoothingFunction().method1
    try:
        bleu_nltk = corpus_bleu(references, candidates, smoothing_function=smoothie)
        # print(f"NLTK BLEU Score: {bleu_nltk}")
        bleu_score = []
        bleu_score.append({
            "NLTK BLEU Score": bleu_nltk
        })
    
        return bleu_score

        # return bleu_nltk
    except Exception as e:
        print(f"Error computing BLEU score: {e}")
        return 0.0

# Testing
reference_file = "reference.txt"
candidate_file = "candidate.txt"

bleu_score = compute_bleu_score(reference_file, candidate_file)
print(f"Computed BLEU Score: {bleu_score}") 





# # Translate the transcription
# translation_file = os.path.join(DONE_DIR, f"{base_name_no_ext}_NLLB_translation.txt")
# print(f"Translating transcription to English...")
# translate_file(
#     transcription_file,           # Input file path
#     translation_file,             # Output file path
#     src_lang=None,                # None to enable auto-detection (don't need to specify this parameter)
#     tgt_lang="eng_Latn",          # Default target is English
#     max_length=512,               # Max output sequence length
#     auto_detect=True,             # Enable language auto-detection
#     max_chunk_tokens=250,         # Smaller chunk size to prevent repetition issues
#     overlap_tokens=50,            # Add overlap between chunks for better coherence
#     num_beams=4                   # Use beam search for higher quality translations
# )