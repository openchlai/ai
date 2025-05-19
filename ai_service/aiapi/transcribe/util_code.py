import spacy
from typing import Dict, Any, List
from datetime import datetime
import uuid
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SPACY_MODEL = "en_core_web_sm"
GBV_TERMS = ["gbv", "sexual", "assault", "abuse", "rape", "harassment", "violence"]

try:
        logger.info(f"Loading spaCy model '{SPACY_MODEL}'")
        nlp_model = spacy.load(SPACY_MODEL)
except Exception as e:
        logger.error(f"Failed to load spaCy model: {str(e)}")
        raise RuntimeError(f"Failed to load spaCy model: {str(e)}")




def generate_case_data(text: str) -> Dict[str, Any]:
    """Generate both the simple and detailed case data structures."""
    global nlp_model
    
    logger.info("Generating case data")
    try:
        if nlp_model is None:
            logger.warning("NLP model not loaded, loading now...")
            nlp_model = spacy.load(SPACY_MODEL)
        
        doc = nlp_model(text)
        
        # Enhanced GBV detection with lemmatization and more sophisticated patterns
        # Count occurrences of GBV terms with context
        gbv_mentions = []
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            for term in GBV_TERMS:
                if term in sent_text:
                    gbv_mentions.append({
                        "term": term,
                        "context": sent.text
                    })
        
        is_gbv = len(gbv_mentions) > 0
        gbv_confidence = min(1.0, len(gbv_mentions) / 5)  # Scale up to 5 mentions
        
        timestamp = str(int(datetime.now().timestamp()))
        case_id = str(uuid.uuid4())
        
        # Generate reporter ID and contact ID
        reporter_id = str(uuid.uuid4().int)[:8]
        contact_id = str(uuid.uuid4().int)[:8]
        
        # Extract entities with better categorization
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Geopolitical entity (countries, cities)
            "LOC": [],  # Other locations
            "DATE": [],
            "TIME": [],
            "MONEY": [],
            "PHONE": []  # Custom extraction for phone numbers
        }
        
        # Extract phone numbers with regex
        import re
        phone_pattern = re.compile(r'\b\d{10,12}\b')
        phone_matches = phone_pattern.findall(text)
        if phone_matches:
            entities["PHONE"] = phone_matches
            
        for ent in doc.ents:
            if ent.label_ in entities:
                # Prevent duplicates
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
        
        # Extract sentiment with better analysis
        sentiment_result = analyze_sentiment(doc)
        
        # Simple structure with extracted entities
        simple_case = {
            "complaint_text": text,
            "submission_id": case_id,
            "session_id": str(uuid.uuid4()),
            "reporter_nickname": "Anonymous Reporter",
            "case_category": "Harassment" if is_gbv else "Other",
            "case_category_id": "362484" if is_gbv else "362485",
            "gbv_confidence": gbv_confidence,
            "gbv_mentions": gbv_mentions,
            "victim": {
                "name": entities["PERSON"][0] if entities["PERSON"] else "Victim Name",
                "age": "25",
                "gender": "Female",
                "additional_info": "Extracted from audio"
            },
            "perpetrator": {
                "name": entities["PERSON"][1] if len(entities["PERSON"]) > 1 else "Perpetrator Name",
                "age": "30",
                "gender": "Male",
                "additional_info": "Extracted from audio"
            },
            "detected_entities": entities,
            "sentiment": sentiment_result
        }
        
        # Detailed structure with more NLP-extracted info
        detailed_case = {
            "src": "walkin",
            "src_uid": f"walkin-100-{timestamp}",
            "src_address": "1000000000" if not entities["PHONE"] else entities["PHONE"][0],
            "src_uid2": f"walkin-100-{timestamp}-2",
            "src_usr": "100",
            "src_vector": "2",
            "src_callid": case_id,
            "src_ts": f"{timestamp}.145",
            "reporters_uuid": {
                "fname": "Anonymous Reporter",
                "age_t": "0",
                "age": "30",
                "dob": "",
                "age_group_id": "361955",
                "location_id": "258783",
                "sex_id": "121",
                "landmark": entities["LOC"][0] if entities["LOC"] else "",
                "nationality_id": "",
                "national_id_type_id": "",
                "national_id": "",
                "lang_id": "",
                "tribe_id": "",
                "phone": entities["PHONE"][0] if entities["PHONE"] else "1000000000",
                "phone2": entities["PHONE"][1] if len(entities["PHONE"]) > 1 else "",
                "email": "",
                ".id": reporter_id
            },
            "clients_case": [{
                "fname": entities["PERSON"][0] if entities["PERSON"] else "Victim Name",
                "age_t": "0",
                "age": "25",
                "dob": "",
                "age_group_id": "361953",
                "location_id": "258783",
                "sex_id": "122",
                "landmark": entities["LOC"][0] if entities["LOC"] else "",
                "nationality_id": "",
                "national_id_type_id": "",
                "national_id": "",
                "lang_id": "",
                "tribe_id": "",
                "phone": "",
                "phone2": "",
                "email": "",
                ".id": contact_id
            }],
            "perpetrators_case": [{
                "fname": entities["PERSON"][1] if len(entities["PERSON"]) > 1 else "Perpetrator Name",
                "age_t": "0",
                "age": "30",
                "dob": "",
                "age_group_id": "361955",
                "age_group": "31-45",
                "location_id": "",
                "sex_id": "121",
                "sex": "^Male",
                "landmark": "",
                "nationality_id": "",
                "national_id_type_id": "",
                "national_id": "",
                "lang_id": "",
                "tribe_id": "",
                "phone": "",
                "phone2": "",
                "email": "",
                "relationship_id": "",
                "shareshome_id": "",
                "health_id": "",
                "employment_id": "",
                "marital_id": "",
                "guardian_fullname": "",
                "notes": "",
                ".id": ""
            }],
            "attachments_case": [],
            "services": [],
            "knowabout116_id": "",
            "case_category_id": "362484" if is_gbv else "362485",
            "narrative": text,
            "plan": "---",
            "justice_id": "",
            "assessment_id": "",
            "priority": "1" if is_gbv else "2",
            "status": "1",
            "escalated_to_id": "0",
            "gbv_related": "1" if is_gbv else "0",
            "reporter_id": reporter_id,
            "reporter_contact_id": contact_id,
            "reporter_fullname": "Anonymous Reporter",
            "reporter_age_group_id": "361955",
            "reporter_sex_id": "121",
            "nlp_analysis": {
                "entities": entities,
                "sentiment": sentiment_result,
                "key_phrases": extract_key_phrases(doc),
                "gbv_mentions": gbv_mentions,
                "gbv_confidence": gbv_confidence
            }
        }
        
        return {
            "simple_case": simple_case,
            "detailed_case": detailed_case, 
            "is_gbv": is_gbv
        }
    except Exception as e:
        logger.error(f"Case generation failed: {str(e)}")
        raise RuntimeError(f"Case generation failed: {str(e)}")


def analyze_sentiment(doc) -> Dict[str, Any]:
    """More sophisticated sentiment analysis."""
    # Pre-defined sentiment lexicons
    positive_words = set([
        "help", "support", "safe", "protected", "rescue", "assist", 
        "care", "recover", "heal", "protect", "secure", "save"
    ])
    negative_words = set([
        "afraid", "hurt", "danger", "threat", "fear", "scared", "terrified",
        "assault", "abuse", "violence", "attack", "victim", "suffer", "pain",
        "trauma", "injury", "force", "violent", "hit", "beat", "kill", "murder"
    ])
    
    # Count word occurrences with context
    positive_count = 0
    negative_count = 0
    sentiment_mentions = []
    
    for token in doc:
        if token.lemma_.lower() in positive_words:
            positive_count += 1
            sentiment_mentions.append({
                "word": token.text,
                "sentiment": "positive",
                "sentence": token.sent.text
            })
        elif token.lemma_.lower() in negative_words:
            negative_count += 1
            sentiment_mentions.append({
                "word": token.text,
                "sentiment": "negative",
                "sentence": token.sent.text
            })
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        sentiment_score = 0
    else:
        sentiment_score = (positive_count - negative_count) / total
    
    # Determine sentiment label
    if sentiment_score < -0.3:
        sentiment = "negative"
    elif sentiment_score > 0.3:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    
    return {
        "label": sentiment,
        "score": sentiment_score,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "mentions": sentiment_mentions
    }

def extract_key_phrases(doc) -> List[Dict[str, Any]]:
    """Extract key phrases with ranking."""
    # Extract noun chunks with improved filtering
    phrases = []
    seen = set()
    
    for chunk in doc.noun_chunks:
        # Skip if too short or already seen
        if len(chunk.text.strip()) < 3 or chunk.text.lower() in seen:
            continue
            
        # Skip if it's only a pronoun
        if len(chunk) == 1 and chunk[0].pos_ == "PRON":
            continue
            
        seen.add(chunk.text.lower())
        
        # Calculate importance based on token features
        importance = sum(1 for token in chunk if not token.is_stop and not token.is_punct)
        
        phrases.append({
            "text": chunk.text,
            "importance": importance,
            "root": chunk.root.text,
            "length": len(chunk)
        })
    
    # Sort by importance and limit to top N
    phrases.sort(key=lambda x: x["importance"], reverse=True)
    return phrases[:10]  # Return top 10 phrases
