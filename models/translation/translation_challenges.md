# Key Challenges & Improvement Areas

This documentation covers some of the key translation limitations, challenges and improvement areas which include:

1. **Hallucination in NLLB Translation model** - At times, NLLB model generates incorrect or nonsensical text not grounded in the source input (e.g., inventing words, misrepresenting numbers, or adding phrases not in the source) when performing textual translation.
 **Example:**  
     - *Source (Swahili):* "Nlikuwa na deadline ya kumuona daktari."  
     - *Incorrect Translation:* "I had a **disease** and I consulted a doctor."
     - **Root Cause:** Model overgeneralizes low-resource language patterns.  

   **Solutions**
   - Fine-tune NLLB and Whisper models on in-domain data - Train on code-switched, noisy, and dialect-rich
datasets to align outputs with real-world inputs.
   - Human-in-the-loop validation - Deploy real-time correction tools for call-center agents
to fix hallucinations.

2. **Code-Switching and Mixed Languages** - Speakers switch between languages mid-sentence (e.g., Swahili + English + Sheng), confusing models trained on monolingual data.
Example: *"Nlikuwa na deadline ya kufanya assignment."*
    - **Root Cause:** Training data lacks code-switched examples.

   **Solutions**

   - Collect code-switched data from call transcripts, social media, or synthetic generation (mixing Swahili/English/Sheng sentences) and Label the data.
   - Fine-tune models (NLLB or Whisper) on this data to recognize language switches.

3. **Speaker Overlap and Turn-Taking Confusion** - Multiple people speaking simultaneously
causes Whisper to mix/drop words (e.g., merging "Nataka" [I want] and "Sawa" [OK] into
garbled text) and in turn mess with the translation model and the NLP processing models
for case summary, case prediction and case triaging.
   - **Root Cause:** Lack of diarization preprocessing.  

   **Solutions**
   - Speaker Diarization Preprocessing - Use tools like PyAnnotate to: Split audio into segments per speaker. Assign labels (e.g., "Speaker 1," "Agent").
   - Slice audio by speaker segments before feeding to Whisper.
   - Fine-tune models (NLLB) on this data to recognize language switches.

4. **Shrubbing (Phonetic Errors)** - Accent-driven mispronunciations lead to transcription errors (e.g., "lala" → "rara" or "nilienda" → "nirieda"). These variations create out-of-vocabulary (OOV) issues for translation models.
   - **Root Cause:** Whisper model is untrained on regional accents.  

   **Solutions**

   - Fine-tune Whisper on accented speech with phonetic variations (e.g., "rara" → "lala").
   - Use audio denoising tools (e.g., RNNoise) to improve input quality.
   - Post-Processing - Apply context-aware correction (e.g., lookup tables for common
mispronunciations or smart functions).

5. **Sheng Slang** - Informal slang terms (e.g., "mbao" = money) are mistranslated.  
   - **Example:**  
     - *Source:* "Nimechill."  
     - *Output:* "I am cold." (Should be "I’m relaxed.")  
   - **Root Cause:** Tokenizer lacks Sheng vocabulary.

    **Solutions**
   - Lexicon Development: Build a dynamic Sheng dictionary (e.g., "doh" = money) with community input. Use crowdsourcing/social media scraping to capture evolving terms.
   - Expand tokenizers to include Sheng terms and retrain models on augmented data.

### **Performance Gaps**

BLEU score gaps against targets for key language pairs:  

| Language Pair       | Current BLEU | Target BLEU | Gap  |  
|---------------------|--------------|-------------|------|  
| Swahili (KE)→English | __          | 75          | -__  |  
| Sheng→English       | __           | 60          | -__  |  
| Luganda → English   | __           |  75         | -__  |
| Swahili (TZ)→English | __          | 75          | -__ |
| Kinyarwanda→English | __           |  75          | -__ |
| Dholuo → English    | __           |  75          | -__ |
| Kamba → English     | __           |  75          | -__ |

### **Actionable Recommendations**

#### Priority Solutions

| Solution       | Urgency | Scope | Expected Outcome |  
|---------------------|--------------|------|--------|
| Speaker Diarization | P0           | Preprocess audio with PyAnnotate to split speakers |  Reduce overlap errors which bring about context loss.|
| Sheng Glossary      | P1           | Inject 200+ Sheng terms into tokenizer |  Fix most of slang mistranslations.|
| Audio Denoising     | P0           | Use RNNoise to clean call-center audio      |  Improve Whisper accuracy. |
| Code-Switch Tuning  | P0           |  Fine-tune NLLB and Whisper models on mixed-language data. |  Close the current BLEU metric gap. |
| Accent Training    | P1           |  Retrain Whisper on accented speech data.      |  Reduce shrubbing errors by 35%. |
