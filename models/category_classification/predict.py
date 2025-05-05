import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model and tokenizer
model_path = "./case_category_model"
model = DistilBertForSequenceClassification.from_pretrained(model_path).to(device)
tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)

# Get label mappings (you might need to save/load these properly)
id2label = model.config.id2label

def predict_category(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    
    pred_id = torch.argmax(outputs.logits, dim=1).item()
    return id2label[pred_id]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(f"Text: {text}")
        print(f"Predicted Category: {predict_category(text)}")
    else:
        print("Please provide text to classify as arguments")