from transformers import AutoTokenizer
import torch
import numpy as np
import re
import json
from transformers import (
    AutoTokenizer,
    DistilBertPreTrainedModel,
    DistilBertModel, 
)
import torch.nn as nn


# Import custom model class
class MultiTaskDistilBert(DistilBertPreTrainedModel):
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
        self.dropout = nn.Dropout(config.dropout)
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None, 
                main_category_id=None, sub_category_id=None, 
                intervention_id=None, priority_id=None):
        distilbert_output = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        hidden_state = distilbert_output.last_hidden_state 
        pooled_output = hidden_state[:, 0]                 
        pooled_output = self.pre_classifier(pooled_output) 
        pooled_output = nn.ReLU()(pooled_output)           
        pooled_output = self.dropout(pooled_output)        
        
        logits_main = self.classifier_main(pooled_output)
        logits_sub = self.classifier_sub(pooled_output)
        logits_interv = self.classifier_interv(pooled_output)
        logits_priority = self.classifier_priority(pooled_output)
        
        loss = None
        if main_category_id is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_main = loss_fct(logits_main, main_category_id)
            loss_sub = loss_fct(logits_sub, sub_category_id)
            loss_interv = loss_fct(logits_interv, intervention_id)
            loss_priority = loss_fct(logits_priority, priority_id)
            loss = loss_main + loss_sub + loss_interv + loss_priority
        
        # Return as tuple for Trainer compatibility
        if loss is not None:
            return (loss, logits_main, logits_sub, logits_interv, logits_priority)
        else:
            return (logits_main, logits_sub, logits_interv, logits_priority)

def classify_case(narrative):
    model_path = "/opt/chl_ai/models/ai_models/MultiClassifier/"

    # Load category lists (Labels needed for matching the classification predictions)
    with open(model_path + "main_categories.json") as f:
        main_categories = json.load(f)
    with open(model_path + "sub_categories.json") as f:
        sub_categories = json.load(f)
    with open(model_path + "interventions.json") as f:
        interventions = json.load(f)
    with open(model_path + "priorities.json") as f:
        priorities = json.load(f)

    # Load model and tokenizer
    model_path = model_path + './multitask_distilbert'
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = MultiTaskDistilBert.from_pretrained(
        model_path,
        num_main=len(main_categories),
        num_sub=len(sub_categories),
        num_interv=len(interventions),
        num_priority=len(priorities)
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    try:
        text = narrative.lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        inputs = tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=256,
            return_tensors="pt"
        ).to(device)
        
        with torch.no_grad():
            logits_main, logits_sub, logits_interv, logits_priority = model(**inputs)
        
        preds_main = np.argmax(logits_main.cpu().numpy(), axis=1)[0]
        preds_sub = np.argmax(logits_sub.cpu().numpy(), axis=1)[0]
        preds_interv = np.argmax(logits_interv.cpu().numpy(), axis=1)[0]
        preds_priority = np.argmax(logits_priority.cpu().numpy(), axis=1)[0]
        
        # Clean up intermediate tensors
        del inputs, logits_main, logits_sub, logits_interv, logits_priority
        
        return {
            "main_category": main_categories[preds_main],
            "sub_category": sub_categories[preds_sub],
            "intervention": interventions[preds_interv],
            "priority": priorities[preds_priority]
        }
        
    finally:
        # CRITICAL: Clean up model and free GPU memory
        model.cpu()  # Move model to CPU first
        del model    # Delete model
        del tokenizer # Delete tokenizer
        
        # Force GPU cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        import gc
        gc.collect()
        print("Classifier GPU memory cleaned up")  # For debugging

# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from joblib import load
# import torch
# import re

# model_path = "/opt/chl_ai/models/ai_models/CLASSIFICATION/case_classifier_model/"
# #model_path = "/Users/mac/MODELS/"


# # Load components(model, tokenizer)
# model = AutoModelForSequenceClassification.from_pretrained(model_path)
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# label_encoder = load(model_path +'/label_encoder.joblib')

# # Use GPU if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# def classify_case(narrative: str):
#     # Preprocess (match training cleaning)
#     text = narrative.lower().strip()
#     text = re.sub(r'[^a-z0-9\s]', '', text)  

#     # Tokenize
#     inputs = tokenizer(
#         text,
#         truncation=True,
#         padding='max_length',
#         max_length=256,
#         return_tensors="pt"
#     ).to(device)

#     # Predict
#     with torch.no_grad():
#         outputs = model(**inputs)

#     # Get probabilities
#     probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
#     top_prob, top_label = torch.max(probs, dim=1)

#     # Decode label
#     category = label_encoder.inverse_transform([top_label.cpu().item()])[0]

#     return {
#         "category": category,
#         "confidence": round(top_prob.item(), 4)
#     }


# narrative = "Mary called in to report about her husband who has been beating her for the past 3 months. She said he gets angry over small things and hits her with his fists. She is scared and wants to leave but doesn't know how to do it safely. She has two children aged 5 and 7 who are also affected by the violence. Mary is seeking help to find a safe place for herself and her children."
# result = classify_case(narrative)
# print(result)
# print(f"Predicted: {result['category']} (Confidence: {result['confidence']*100:.1f}%)")
