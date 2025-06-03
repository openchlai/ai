from transformers import AutoTokenizer, AutoModelForSequenceClassification
from joblib import load
import torch
import re

model_path = "/opt/chl_ai/models/ai_models/CLASSIFICATION/case_classifier_model/"
#model_path = "/Users/mac/MODELS/"


# Load components(model, tokenizer)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
label_encoder = load(model_path +'/label_encoder.joblib')

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def classify_case(narrative: str):
    # Preprocess (match training cleaning)
    text = narrative.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)  

    # Tokenize
    inputs = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors="pt"
    ).to(device)

    # Predict
    with torch.no_grad():
        outputs = model(**inputs)

    # Get probabilities
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    top_prob, top_label = torch.max(probs, dim=1)

    # Decode label
    category = label_encoder.inverse_transform([top_label.cpu().item()])[0]

    return {
        "category": category,
        "confidence": round(top_prob.item(), 4)
    }


# narrative  = "On November 7th, 2022, Daniel Kimeli from Mukutani Ward recognized a sign of distress in Violet Wakio (aged 10) and promptly reported the matter. The girl was spotted residing near an undisclosed landmark within Baringo County's Unknown Subcounty.\\\nDaniel stated that he suspected an incident of 'Torture or cruel treatment', having observed injuries and emotional turmoil in Violet, which were allegedly inflicted by her Step-parent, Jon Wanyama. The whereabouts of the perpetrator are currently unknown,\\\nbut immediate action is necessary to ensure Violet's safety from any further harm."

# result = classify_case(narrative)
# print(f"Predicted: {result['category']} (Confidence: {result['confidence']*100:.1f}%)")

