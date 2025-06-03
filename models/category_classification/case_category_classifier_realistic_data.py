import os
import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Check for MPS availability and set device
if torch.backends.mps.is_available():
    torch.mps.empty_cache()
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

# -------- CONFIGURATION -------- #
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 256
BATCH_SIZE = 16
EPOCHS = 4
# ------------------------------- #



# 1. Load and preprocess the synthetic data
try:
    df = pd.read_csv('generated_child_protection_cases.csv')  # Update with your filename
except FileNotFoundError:
    raise FileNotFoundError("Could not find the CSV file. Please check the file path.")

# 2. Prepare text and label columns
print("Columns in your CSV:", df.columns.tolist())

# Use narrative as text input and category_name as label
df['text'] = df['narrative'].astype(str)
df['label'] = df['category_name']

# 3. Filter out rows with missing or invalid data
print(f"\nTotal rows before cleaning: {len(df)}")
df = df.dropna(subset=['text', 'label'])
df = df[df['text'].apply(lambda x: len(x.strip()) > 10)]  # Remove empty/short texts
df = df[df['label'].apply(lambda x: isinstance(x, str))]
print(f"Total rows after cleaning: {len(df)}")

# 4. Create Hugging Face Dataset
dataset = Dataset.from_pandas(df)

# 5. Split into train/test
split_dataset = dataset.train_test_split(test_size=0.2, shuffle=True)
train_dataset = split_dataset["train"]
test_dataset = split_dataset["test"]

print(f"\nTrain examples: {len(train_dataset)}")
print(f"Test examples: {len(test_dataset)}")
print("Sample training example:", train_dataset[0]['text'][:200] + "...")

# Encode labels
label_encoder = LabelEncoder()
label_encoder.fit(df['label'])

num_labels = len(label_encoder.classes_)
print(f"\nNumber of categories: {num_labels}")
print("Categories:", label_encoder.classes_)

id2label = dict(enumerate(label_encoder.classes_))
label2id = {v: k for k, v in id2label.items()}

def encode_labels(example):
    example["label"] = label2id[example["label"]]
    return example

train_dataset = train_dataset.map(encode_labels)
test_dataset = test_dataset.map(encode_labels)

# Tokenize texts
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize_function(example):
    return tokenizer(
        example["text"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH
    )

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Set format for PyTorch
train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
test_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# Load model
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id
).to(device)



# # Training arguments
# training_args = TrainingArguments(
#     output_dir='./case_category_model',
#     num_train_epochs=EPOCHS,
#     per_device_train_batch_size=BATCH_SIZE,
#     per_device_eval_batch_size=BATCH_SIZE,
#     weight_decay=0.01,
#     logging_dir='./logs',
#     logging_steps=10,
#     learning_rate=2e-5,
#     # evaluation_strategy="epoch",
#     # save_strategy="epoch",
#     load_best_model_at_end=True,
#     save_total_limit=2,
# )


training_args = TrainingArguments(
    output_dir='./case_category_model',
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    learning_rate=2e-5,
    save_total_limit=2,
    do_train=True,
    do_eval=True
)


def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

# Train the model
print("\nStarting training...")
trainer.train()

# Save the final model
trainer.save_model("./case_category_model")
tokenizer.save_pretrained("./case_category_model")
print("\n✅ Model and tokenizer saved to ./case_category_model")

# Inference Example
def predict_category(text, model, tokenizer, id2label):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    pred_id = torch.argmax(logits, dim=1).item()
    return id2label[pred_id]

# Example usage with synthetic-like examples
print("\nExample Predictions:")
test_cases = [
    "John was only 9 years old when she was forced into a marriage with a man who was 25 years old. The man had promised John's parents that he would take care of her and provide for her needs, but he has failed to do so.",
    "Samuel, a 9-year-old female, was sexually abused by her uncle, who attempted to penetrate her vagina with his finger. The abuse occurred on multiple occasions, and Samuel felt terrified and powerless to stop it.",
    "Peter, a 17-year-old female, was recently exploited through the use of technology. She met an individual online who manipulated and deceived her, leading to her involvement in online child abuse."
]

for text in test_cases:
    prediction = predict_category(text, model, tokenizer, id2label)
    print(f"Text: {text[:150]}...\nPredicted Category: {prediction}\n")