import argparse
import langid
import re
import torch
import gc
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# List of all NLLB supported languages
NLLB_LANGUAGES = [
    "ace_Arab", "ace_Latn", "acm_Arab", "acq_Arab", "aeb_Arab", "afr_Latn", "ajp_Arab", "aka_Latn", 
    "amh_Ethi", "apc_Arab", "arb_Arab", "ars_Arab", "ary_Arab", "arz_Arab", "asm_Beng", "ast_Latn", 
    "awa_Deva", "ayr_Latn", "azb_Arab", "azj_Latn", "bak_Cyrl", "bam_Latn", "ban_Latn", "bel_Cyrl", 
    "bem_Latn", "ben_Beng", "bho_Deva", "bjn_Arab", "bjn_Latn", "bod_Tibt", "bos_Latn", "bug_Latn", 
    "bul_Cyrl", "cat_Latn", "ceb_Latn", "ces_Latn", "cjk_Latn", "ckb_Arab", "crh_Latn", "cym_Latn", 
    "dan_Latn", "deu_Latn", "dik_Latn", "dyu_Latn", "dzo_Tibt", "ell_Grek", "eng_Latn", "epo_Latn", 
    "est_Latn", "eus_Latn", "ewe_Latn", "fao_Latn", "pes_Arab", "fij_Latn", "fin_Latn", "fon_Latn", 
    "fra_Latn", "fur_Latn", "fuv_Latn", "gla_Latn", "gle_Latn", "glg_Latn", "grn_Latn", "guj_Gujr", 
    "hat_Latn", "hau_Latn", "heb_Hebr", "hin_Deva", "hne_Deva", "hrv_Latn", "hun_Latn", "hye_Armn", 
    "ibo_Latn", "ilo_Latn", "ind_Latn", "isl_Latn", "ita_Latn", "jav_Latn", "jpn_Jpan", "kab_Latn", 
    "kac_Latn", "kam_Latn", "kan_Knda", "kas_Arab", "kas_Deva", "kat_Geor", "knc_Arab", "knc_Latn", 
    "kaz_Cyrl", "kbp_Latn", "kea_Latn", "khm_Khmr", "kik_Latn", "kin_Latn", "kir_Cyrl", "kmb_Latn", 
    "kon_Latn", "kor_Hang", "kmr_Latn", "lao_Laoo", "lvs_Latn", "lij_Latn", "lim_Latn", "lin_Latn", 
    "lit_Latn", "lmo_Latn", "ltg_Latn", "ltz_Latn", "lua_Latn", "lug_Latn", "luo_Latn", "lus_Latn", 
    "mag_Deva", "mai_Deva", "mal_Mlym", "mar_Deva", "min_Latn", "mkd_Cyrl", "plt_Latn", "mlt_Latn", 
    "mni_Beng", "khk_Cyrl", "mos_Latn", "mri_Latn", "zsm_Latn", "mya_Mymr", "nld_Latn", "nno_Latn", 
    "nob_Latn", "npi_Deva", "nso_Latn", "nus_Latn", "nya_Latn", "oci_Latn", "gaz_Latn", "ory_Orya", 
    "pag_Latn", "pan_Guru", "pap_Latn", "pol_Latn", "por_Latn", "prs_Arab", "pbt_Arab", "quy_Latn", 
    "ron_Latn", "run_Latn", "rus_Cyrl", "sag_Latn", "san_Deva", "sat_Beng", "scn_Latn", "shn_Mymr", 
    "sin_Sinh", "slk_Latn", "slv_Latn", "smo_Latn", "sna_Latn", "snd_Arab", "som_Latn", "sot_Latn", 
    "spa_Latn", "als_Latn", "srd_Latn", "srp_Cyrl", "ssw_Latn", "sun_Latn", "swe_Latn", "swh_Latn", 
    "szl_Latn", "tam_Taml", "tat_Cyrl", "tel_Telu", "tgk_Cyrl", "tgl_Latn", "tha_Thai", "tir_Ethi", 
    "taq_Latn", "taq_Tfng", "tpi_Latn", "tsn_Latn", "tso_Latn", "tuk_Latn", "tum_Latn", "tur_Latn", 
    "twi_Latn", "tzm_Tfng", "uig_Arab", "ukr_Cyrl", "umb_Latn", "urd_Arab", "uzn_Latn", "vec_Latn", 
    "vie_Latn", "war_Latn", "wol_Latn", "xho_Latn", "ydd_Hebr", "yor_Latn", "yue_Hant", "zho_Hans", 
    "zho_Hant", "zul_Latn"
]

# ISO 639-1/3 language code mappings to NLLB format
LANG_MAP = {
    'en': 'eng_Latn',
    'fr': 'fra_Latn',
    'es': 'spa_Latn',
    'de': 'deu_Latn',
    'zh': 'zho_Hans',
    'ar': 'arb_Arab',
    'ru': 'rus_Cyrl',
    'pt': 'por_Latn',
    'it': 'ita_Latn',
    'ja': 'jpn_Jpan',
    'hi': 'hin_Deva',
    'sw': 'swh_Latn',  # Swahili is 'swh_Latn' in NLLB (not 'swa_Latn')
    'tr': 'tur_Latn',
    'pl': 'pol_Latn',
    'nl': 'nld_Latn',
    'ko': 'kor_Hang'
}

def detect_language(text):
    """
    Detect language of text and map it to NLLB format.
    Returns the detected language code in NLLB format.
    """
    # Detect language
    lang_code, confidence = langid.classify(text)
    print(f"Language detection: {lang_code} (confidence: {confidence:.2f})")
    
    # Map to NLLB format if possible
    if lang_code in LANG_MAP:
        nllb_code = LANG_MAP[lang_code]
        if nllb_code in NLLB_LANGUAGES:
            return nllb_code
        else:
            print(f"Warning: Mapped language '{nllb_code}' not in NLLB supported languages. Using English as fallback.")
            return 'eng_Latn'
    else:
        print(f"Warning: Detected language '{lang_code}' not mapped to NLLB format. Using English as fallback.")
        return 'eng_Latn'

def improved_chunk_text(text, tokenizer, src_lang, max_tokens=250, overlap_tokens=50):
    """
    Split text into chunks based on sentence boundaries while respecting token limits
    and implementing chunk overlap for better coherence.
    
    Args:
        text (str): The text to chunk
        tokenizer: The tokenizer to use for counting tokens
        src_lang (str): Source language code for tokenizer
        max_tokens (int): Maximum tokens per chunk
        overlap_tokens (int): Number of tokens to overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    # First, break text into sentences
    # This regex matches most common sentence end punctuation
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Get token counts for each sentence
    sentence_tokens = []
    for sentence in sentences:
        tokens = tokenizer.encode(sentence, add_special_tokens=False)
        sentence_tokens.append((sentence, len(tokens)))
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for sentence, token_count in sentence_tokens:
        # If this sentence alone exceeds the max, split it by words
        if token_count > max_tokens:
            # If we have a current chunk, add it to chunks
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_token_count = 0
            
            # Split the long sentence into words
            words = sentence.split()
            word_chunk = []
            word_token_count = 0
            
            for word in words:
                word_tokens = tokenizer.encode(word + " ", add_special_tokens=False)
                word_token_len = len(word_tokens)
                
                if word_token_count + word_token_len <= max_tokens:
                    word_chunk.append(word)
                    word_token_count += word_token_len
                else:
                    if word_chunk:
                        chunks.append(" ".join(word_chunk))
                    word_chunk = [word]
                    word_token_count = word_token_len
            
            if word_chunk:
                chunks.append(" ".join(word_chunk))
                
        # If adding this sentence would exceed the limit, start a new chunk
        elif current_token_count + token_count > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
                # If we need overlap, find sentences to repeat in the next chunk
                if overlap_tokens > 0 and len(current_chunk) > 0:
                    # Take sentences from the end of the current chunk until we reach desired overlap
                    overlap_count = 0
                    overlap_sentences = []
                    
                    for i in range(len(current_chunk) - 1, -1, -1):
                        overlap_sentence = current_chunk[i]
                        overlap_tokens_count = len(tokenizer.encode(overlap_sentence, add_special_tokens=False))
                        
                        if overlap_count + overlap_tokens_count <= overlap_tokens:
                            overlap_sentences.insert(0, overlap_sentence)
                            overlap_count += overlap_tokens_count
                        else:
                            break
                    
                    # Start new chunk with overlap sentences
                    current_chunk = overlap_sentences.copy()
                    current_token_count = overlap_count
                else:
                    current_chunk = []
                    current_token_count = 0
            
            # Add the current sentence to the new chunk
            current_chunk.append(sentence)
            current_token_count += token_count
        else:
            # Add to current chunk
            current_chunk.append(sentence)
            current_token_count += token_count
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def translate_text_improved(translator, text, tokenizer, src_lang, max_tokens=250, overlap_tokens=50, num_beams=4):
    """
    Translate text by breaking it into chunks with overlap and then combining the results.
    Uses beam search for better quality.
    
    Args:
        translator: The translation pipeline
        text (str): Text to translate
        tokenizer: Tokenizer for token counting
        src_lang (str): Source language code
        max_tokens (int): Maximum tokens per chunk
        overlap_tokens (int): Number of tokens to overlap between chunks
        num_beams (int): Number of beams for beam search
        
    Returns:
        str: Translated text
    """
    # Break text into manageable chunks with overlap
    chunks = improved_chunk_text(text, tokenizer, src_lang, max_tokens, overlap_tokens)
    
    # Keep track of progress
    total_chunks = len(chunks)
    print(f"Text split into {total_chunks} chunks for translation")
    
    # Store translations
    translated_chunks = []
    
    for i, chunk in enumerate(chunks):
        print(f"Translating chunk {i+1}/{total_chunks} ({len(chunk)} chars)...")
        
        try:
            # Skip empty chunks
            if not chunk.strip():
                continue
                
            # Set num_beams for better translation quality
            translator.model.config.num_beams = num_beams
            
            # Translate the chunk
            translation = translator(chunk)
            
            # Extract translated text
            if isinstance(translation, list) and isinstance(translation[0], dict):
                translated_text = translation[0]['translation_text']
            else:
                translated_text = translation
                
            translated_chunks.append(translated_text)
            
        except Exception as e:
            print(f"Error translating chunk {i+1}: {e}")
            # Add error note with original text
            translated_chunks.append(f"[TRANSLATION ERROR] {chunk}")
    
    # Remove duplicate content from overlapping chunks
    if len(translated_chunks) > 1 and overlap_tokens > 0:
        final_chunks = [translated_chunks[0]]
        
        for i in range(1, len(translated_chunks)):
            current_chunk = translated_chunks[i]
            prev_chunk = translated_chunks[i-1]
            
            # Try to find overlap between chunks
            # Start with 10-word overlap and decrease if not found
            for overlap_size in range(10, 3, -1):
                prev_words = prev_chunk.split()[-overlap_size:]
                if not prev_words:
                    break
                    
                prev_overlap = " ".join(prev_words)
                if prev_overlap in current_chunk:
                    # Found overlap, remove it from current chunk
                    overlap_index = current_chunk.find(prev_overlap)
                    clean_chunk = current_chunk[overlap_index + len(prev_overlap):].strip()
                    final_chunks.append(clean_chunk)
                    break
            else:
                # No overlap found, just add the chunk
                final_chunks.append(current_chunk)
        
        # Join the deduplicated chunks
        return " ".join(final_chunks)
    else:
        # Join the chunks with spaces if no overlap
        return " ".join(translated_chunks)

def translate_file(input_file, output_file, src_lang=None, tgt_lang="eng_Latn", 
                  max_length=512, auto_detect=False, max_chunk_tokens=250, 
                  overlap_tokens=50, num_beams=4):
    """
    Translate text from a file and save the translation to another file.
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to save the translated text
        src_lang (str): Source language code (e.g., 'eng_Latn', 'swh_Latn')
        tgt_lang (str): Target language code (e.g., 'eng_Latn', 'fra_Latn')
        max_length (int): Maximum length for translation output
        auto_detect (bool): Whether to auto-detect the source language
        max_chunk_tokens (int): Maximum tokens per chunk
        overlap_tokens (int): Number of tokens to overlap between chunks
        num_beams (int): Number of beams for beam search
    """
    print(f"Loading NLLB model...")
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    
    # Check if CUDA is available
    import torch
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    print(f"Using device: {device}")

    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
        
    # Detect language if needed
    if auto_detect and (src_lang is None or src_lang == ""):
        # Use the first part of the content for detection
        sample_text = content[:5000]  # First 5000 chars should be enough
        if sample_text:
            detected_lang = detect_language(sample_text)
            src_lang = detected_lang
            print(f"Using detected source language: {src_lang}")
        else:
            print("Warning: Empty input file or unable to detect language. Using English as fallback.")
            src_lang = "eng_Latn"
    elif src_lang is None or src_lang == "":
        print("No source language specified. Using English as default.")
        src_lang = "eng_Latn"
    
    # Validate language codes
    if src_lang not in NLLB_LANGUAGES:
        print(f"Error: Source language '{src_lang}' is not supported by NLLB.")
        print(f"Supported languages include: {', '.join(NLLB_LANGUAGES[:10])}... (total: {len(NLLB_LANGUAGES)})")
        return
        
    if tgt_lang not in NLLB_LANGUAGES:
        print(f"Error: Target language '{tgt_lang}' is not supported by NLLB. Using English instead.")
        tgt_lang = "eng_Latn"
    
    # Create the translation pipeline
    print(f"Creating translation pipeline from {src_lang} to {tgt_lang}...")
    try:
        # Use device object for proper device assignment
        translator = pipeline(
            'translation',
            model=model,
            tokenizer=tokenizer,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            max_length=max_length,
            device=0 if use_cuda else -1  # Use GPU if available, else CPU
        )
    except Exception as e:
        print(f"Error creating translation pipeline: {str(e)}")
        print("Translation failed. Please check the language codes and try again.")
        return
    
    # Set beam search for better quality
    translator.model.config.num_beams = num_beams
    
    # Process the text with improved chunking
    print("Starting improved chunked translation...")
    translated_text = translate_text_improved(
        translator, 
        content, 
        tokenizer, 
        src_lang, 
        max_tokens=max_chunk_tokens,
        overlap_tokens=overlap_tokens,
        num_beams=num_beams
    )
    
    # Write translated text to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        print(f"Translation complete! Results saved to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
    
    # Clean up GPU memory if using CUDA
    if use_cuda:
        import gc
        del model
        del translator
        torch.cuda.empty_cache()
        gc.collect()
        print("GPU memory released")

def display_available_languages():
    # [Keep same function from original script]
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate text files using NLLB with improved chunking")
    parser.add_argument("--input", "-i", help="Input text file path", required=True)
    parser.add_argument("--output", "-o", help="Output file path", required=True)
    parser.add_argument("--src_lang", "-s", help="Source language code (if not specified, auto-detection will be used)")
    parser.add_argument("--tgt_lang", "-t", help="Target language code (defaults to English)", default="eng_Latn")
    parser.add_argument("--max_length", "-m", type=int, help="Maximum output length", default=512)
    parser.add_argument("--list_languages", "-l", action="store_true", help="List available language codes")
    parser.add_argument("--auto_detect", "-a", action="store_true", help="Auto-detect source language")
    parser.add_argument("--chunk_size", "-c", type=int, help="Maximum tokens per chunk", default=250)
    parser.add_argument("--overlap", "-v", type=int, help="Overlap tokens between chunks", default=50)
    parser.add_argument("--beams", "-b", type=int, help="Number of beams for beam search", default=4)
    
    args = parser.parse_args()
    
    if args.list_languages:
        display_available_languages()
    else:
        translate_file(
            args.input, 
            args.output, 
            args.src_lang, 
            args.tgt_lang,
            args.max_length,
            args.auto_detect or (args.src_lang is None),
            args.chunk_size,
            args.overlap,
            args.beams
        )