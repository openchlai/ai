import argparse
import langid
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

def translate_file(input_file, output_file, src_lang=None, tgt_lang="eng_Latn", batch_size=8, max_length=200, auto_detect=False):
    """
    Translate text from a file and save the translation to another file.
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to save the translated text
        src_lang (str): Source language code (e.g., 'eng_Latn', 'swh_Latn')
        tgt_lang (str): Target language code (e.g., 'eng_Latn', 'fra_Latn')
        batch_size (int): Number of lines to translate at once
        max_length (int): Maximum length for translation output
        auto_detect (bool): Whether to auto-detect the source language
    """
    print(f"Loading NLLB model...")
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
        
    # Detect language if needed
    if auto_detect and (src_lang is None or src_lang == ""):
        # Use the first few lines for detection
        sample_text = " ".join([line.strip() for line in lines[:10] if line.strip()])
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
        translator = pipeline(
            'translation',
            model=model,
            tokenizer=tokenizer,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            max_length=max_length
        )
    except Exception as e:
        print(f"Error creating translation pipeline: {str(e)}")
        print("Translation failed. Please check the language codes and try again.")
        return
    
    # Process in batches
    translated_lines = []
    total_lines = len(lines)
    
    for i in range(0, total_lines, batch_size):
        batch = [line.strip() for line in lines[i:i+batch_size] if line.strip()]
        if not batch:
            continue
            
        print(f"Translating batch {i//batch_size + 1}/{(total_lines-1)//batch_size + 1}...")
        
        try:
            # Translate batch
            translations = translator(batch)
            
            # Extract translated text
            if isinstance(translations, list) and isinstance(translations[0], dict):
                # Handle pipeline output format
                batch_results = [item['translation_text'] for item in translations]
            else:
                # Direct result
                batch_results = translations
                
            translated_lines.extend(batch_results)
            
        except Exception as e:
            print(f"Error translating batch: {e}")
            # Add untranslated text with an error note
            translated_lines.extend([f"[TRANSLATION ERROR] {text}" for text in batch])
    
    # Write translations to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in translated_lines:
                f.write(line + '\n')
        print(f"Translation complete! Results saved to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

def display_available_languages():
    """Display all available language codes in the NLLB model"""
    print("Available NLLB language codes:")
    
    # Print in columns for better readability
    column_width = 12
    columns = 6
    for i in range(0, len(NLLB_LANGUAGES), columns):
        row = NLLB_LANGUAGES[i:i+columns]
        print("  " + "  ".join([code.ljust(column_width) for code in row]))
        
    print(f"\nTotal supported languages: {len(NLLB_LANGUAGES)}")
    
    # Show common language mappings
    print("\nCommon language code mappings:")
    mappings = {
        "English": "eng_Latn",
        "French": "fra_Latn",
        "Spanish": "spa_Latn",
        "German": "deu_Latn",
        "Chinese": "zho_Hans",
        "Arabic": "arb_Arab",
        "Russian": "rus_Cyrl",
        "Japanese": "jpn_Jpan",
        "Hindi": "hin_Deva",
        "Swahili": "swh_Latn",
        "Portuguese": "por_Latn"
    }
    for name, code in mappings.items():
        print(f"  {name.ljust(10)}: {code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate text files to English using NLLB")
    parser.add_argument("--input", "-i", help="Input text file path", required=True)
    parser.add_argument("--output", "-o", help="Output file path", required=True)
    parser.add_argument("--src_lang", "-s", help="Source language code (if not specified, auto-detection will be used)")
    parser.add_argument("--tgt_lang", "-t", help="Target language code (defaults to English)", default="eng_Latn")
    parser.add_argument("--batch_size", "-b", type=int, help="Batch size for translation", default=8)
    parser.add_argument("--max_length", "-m", type=int, help="Maximum output length", default=200)
    parser.add_argument("--list_languages", "-l", action="store_true", help="List available language codes")
    parser.add_argument("--auto_detect", "-a", action="store_true", help="Auto-detect source language")
    
    args = parser.parse_args()
    
    if args.list_languages:
        display_available_languages()
    else:
        translate_file(
            args.input, 
            args.output, 
            args.src_lang, 
            args.tgt_lang,
            args.batch_size,
            args.max_length,
            args.auto_detect or (args.src_lang is None)
        )