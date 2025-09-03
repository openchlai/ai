# # Case Classification Model Training Notebook
# This notebook trains a multi-label classification model for classifying cases repor in call center transcripts.
# 
# 

# ## 📦 Setup and Install Dependencies
# 

import os
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    DistilBertPreTrainedModel,
    DistilBertModel,
    TrainingArguments,
    Trainer,
    EvalPrediction
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import re
import torch.nn as nn
import json
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import mlflow
import mlflow.pytorch
import torch
import logging
import dvc.api


# ## ML Flow Experiment  initialization and Log configuration


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
logger.info(f"Using device: {device}")



mlflow.set_tracking_uri("http://192.168.8.18:5000")
mlflow.set_experiment("Multitask_Classification")


REPO_ROOT="/home/rogendo/Work/ai/ai_service"
DATASET_PATH = 'datasets/classification/cleaned_synthetic_cases_generated_data_v0005.json'

os.chdir(REPO_ROOT)

# ### Dataset Loading
# 
# In here we also Feature Engineer the Main-Category by mapping the subcategories against the pre-defined main categories

# %%

def load_dataset(dataset_path, version="HEAD", repo=''):
    """Load dataset from DVC"""
    # Get dataset path
    data_url = dvc.api.get_url(
        path = dataset_path,
        repo=repo,
    )


    return data_url


# load latest_version
dataset_path = load_dataset(dataset_path=DATASET_PATH,repo=REPO_ROOT)
print(dataset_path)
df = pd.read_json(dataset_path)


# df = pd.read_json("/home/rogendo/chl_scratch/synthetic_data/casedir/balanced_cases_generated_data_v0005.json")
# df = pd.read_json("/home/rogendo/chl_scratch/synthetic_data/casedir/cleaned_balanced_cases_generated_data_v0005.json")
sub_to_main_mapping = {
    "Bullying": "Advice and Counselling",
    "Child in Conflict with the Law": "Advice and Counselling",
    "Discrimination": "Advice and Counselling",
    "Drug/Alcohol Abuse": "Advice and Counselling",
    "Family Relationship": "Advice and Counselling",
    "HIV/AIDS": "Advice and Counselling",
    "Homelessness": "Advice and Counselling",
    "Legal issues": "Advice and Counselling",
    "Missing Child": "Advice and Counselling",  
    "Peer Relationships": "Advice and Counselling",
    "Physical Health": "Advice and Counselling",
    "Psychosocial/Mental Health": "Advice and Counselling",
    "Relationships (Boy/Girl)": "Advice and Counselling",
    "Relationships (Parent/Child)": "Advice and Counselling",
    "Relationships (Student/Teacher)": "Advice and Counselling",
    "School related issues": "Advice and Counselling",
    "Self Esteem": "Advice and Counselling",
    "Sexual & Reproductive Health": "Advice and Counselling",
    "Student/ Teacher Relationship": "Advice and Counselling",
    "Teen Pregnancy": "Advice and Counselling",
    "Adoption": "Child Maintenance & Custody",
    "Birth Registration": "Child Maintenance & Custody",
    "Custody": "Child Maintenance & Custody",
    "Foster Care": "Child Maintenance & Custody",
    "Maintenance": "Child Maintenance & Custody",
    "No Care Giver": "Child Maintenance & Custody",
    "Other": "Child Maintenance & Custody", 
    "Albinism": "Disability",
    "Hearing impairment": "Disability",
    "Hydrocephalus": "Disability",
    "Mental impairment": "Disability",
    "Multiple disabilities": "Disability",
    "Physical impairment": "Disability",
    "Speech impairment": "Disability",
    "Spinal bifida": "Disability",
    "Visual impairment": "Disability",
    "Emotional/Psychological Violence": "GBV",
    "Financial/Economic Violence": "GBV",
    "Forced Marriage Violence": "GBV",
    "Harmful Practice": "GBV",
    "Physical Violence": "GBV",
    "Sexual Violence": "GBV",
    "Child Abuse": "Information",
    "Child Rights": "Information",
    "Info on Helpline": "Information",
    "Legal Issues": "Information",
    "School Related Issues": "Information", 
    "Balanced Diet": "Nutrition",
    "Breastfeeding": "Nutrition",
    "Feeding & Food preparation": "Nutrition",
    "Malnutrition": "Nutrition",
    "Obesity": "Nutrition",
    "Stagnation": "Nutrition",
    "Underweight": "Nutrition",
    "Child Abduction": "VANE",
    "Child Labor": "VANE",
    "Child Marriage": "VANE",
    "Child Neglect": "VANE",
    "Child Trafficking": "VANE",
    "Emotional Abuse": "VANE",
    "Female Genital Mutilation": "VANE",
    "OCSEA": "VANE", 
    "Physical Abuse": "VANE",
    "Sexual Abuse": "VANE",
    "Traditional Practice": "VANE",
    "Unlawful Confinement": "VANE",
    "Other": "VANE"  # Final "Other" mapping
}



# ### 🧪 Dataset mapping and Train-Test Split
# 


# Create new column using the mapping dictionary
df['main_category'] = df['category'].map(sub_to_main_mapping)

# Handle unmapped categories (if any)
df['main_category'] = df['main_category'].fillna('Unknown')

# Preprocess labels
main_categories = sorted(df['main_category'].unique())
sub_categories = sorted(df['category'].unique())
interventions = sorted(df['intervention'].unique())
priorities = [1, 2, 3]

print(df[['category', 'main_category']].head())
logger.info(df[['category', 'main_category']].head())


# Create mappings
main_cat2id = {cat: i for i, cat in enumerate(main_categories)}
sub_cat2id = {cat: i for i, cat in enumerate(sub_categories)}
interv2id = {interv: i for i, interv in enumerate(interventions)}
priority2id = {p: i for i, p in enumerate(priorities)}

# Apply mappings
df['main_category_id'] = df['main_category'].map(main_cat2id)
df['sub_category_id'] = df['category'].map(sub_cat2id)
df['intervention_id'] = df['intervention'].map(interv2id)
df['priority_id'] = df['priority'].map(lambda x: priority2id[x])
df['text'] = df['narrative']

# Split dataset
train_df, test_df = train_test_split(
    df, 
    test_size=0.1, 
    random_state=42,
    stratify=df['sub_category_id']
)

# Create datasets
train_dataset = Dataset.from_pandas(train_df[['text', 'main_category_id', 'sub_category_id', 'intervention_id', 'priority_id']])
test_dataset = Dataset.from_pandas(test_df[['text', 'main_category_id', 'sub_category_id', 'intervention_id', 'priority_id']])

dataset = DatasetDict({
    "train": train_dataset,
    "test": test_dataset,
    "validation": test_dataset
})


# ### Model Head and Layers Setup

# %%
dataset['train'].shape

# %%
dataset['test'].shape

# %%
dataset['validation'].shape

# %%



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
        
        if loss is not None:
            return (loss, logits_main, logits_sub, logits_interv, logits_priority)
        else:
            return (logits_main, logits_sub, logits_interv, logits_priority)

    
    def get_embeddings(self, input_ids, attention_mask):
        return self.forward(
            input_ids=input_ids,
            attention_mask=attention_mask
        )[-1]






# ____ continuous fine-tuning and version control ____

# paths and loading existing metadata
model_output_dir = "/home/rogendo/chl_scratch/multitask_distilbert_version"
metadata_file = os.path.join(model_output_dir, "model_metadata.json")
os.makedirs(model_output_dir, exist_ok=True)

# Load metadata of the last best model
if os.path.exists(metadata_file):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
        print(metadata)
        logger.info(f"Model Version Metadata {metadata}")

    last_best_model_path = os.path.join(model_output_dir, metadata['last_best_model_dir'])
    print(last_best_model_path)
    print(f"Loading existing model from {last_best_model_path} for continuous fine-tuning.")
    logger.info(f"Loading existing model from {last_best_model_path} for continuous fine-tuning.")
   
    # Check if the directory exists
    if os.path.exists(last_best_model_path):
        model = MultiTaskDistilBert.from_pretrained(
            last_best_model_path,
            num_main=len(main_categories),
            num_sub=len(sub_categories),
            num_interv=len(interventions),
            num_priority=len(priorities)
        )
        tokenizer = AutoTokenizer.from_pretrained(last_best_model_path)
    else:
        # Fallback to base model if last best model directory is missing
        print(f"Warning: Last best model directory not found. Starting from base checkpoint.")
        logger.warning (f"Warning: Last best model directory not found. Starting from base checkpoint.")

        checkpoint = "distilbert-base-uncased"
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        model = MultiTaskDistilBert.from_pretrained(
            checkpoint,
            num_main=len(main_categories),
            num_sub=len(sub_categories),
            num_interv=len(interventions),
            num_priority=len(priorities)
        )
else:
    logger.info("No existing model found. Starting from base checkpoint.")
    checkpoint = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = MultiTaskDistilBert.from_pretrained(
        checkpoint,
        num_main=len(main_categories),
        num_sub=len(sub_categories),
        num_interv=len(interventions),
        num_priority=len(priorities)
    )

# --- End  continuous fine-tuning and version control ---




# Tokenization function
def tokenize_function(batch):
    encoding = tokenizer(
        batch["text"], 
        padding="max_length", 
        truncation=True,
        max_length=512
    )
    return encoding

# Apply tokenization
encoded_dataset = dataset.map(tokenize_function, batched=True)
encoded_dataset.set_format("torch", columns=[
    "input_ids", "attention_mask", 
    "main_category_id", "sub_category_id", 
    "intervention_id", "priority_id"
])




def compute_metrics(p: EvalPrediction):
    logger.info("compute_metrics called")
    # p.predictions is a tuple of logits for each task
    # p.label_ids is a tuple of true labels for each task

    logits_main, logits_sub, logits_interv, logits_priority = p.predictions
    labels_main, labels_sub, labels_interv, labels_priority = p.label_ids

    preds_main = np.argmax(logits_main, axis=1)
    preds_sub = np.argmax(logits_sub, axis=1)
    preds_interv = np.argmax(logits_interv, axis=1)
    preds_priority = np.argmax(logits_priority, axis=1)

    metrics = {}

    # Helper function to compute and add metrics for each task
    def add_task_metrics(task_name, labels, preds):
        accuracy = accuracy_score(labels, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
        
        metrics[f"{task_name}_acc"] = accuracy
        metrics[f"{task_name}_precision"] = precision
        metrics[f"{task_name}_recall"] = recall
        metrics[f"{task_name}_f1"] = f1

    add_task_metrics("main", labels_main, preds_main)
    add_task_metrics("sub", labels_sub, preds_sub)
    add_task_metrics("interv", labels_interv, preds_interv)
    add_task_metrics("priority", labels_priority, preds_priority)

    # Calculate average metrics across all tasks
    avg_acc = np.mean([metrics[f"{task}_acc"] for task in ["main", "sub", "interv", "priority"]])
    avg_precision = np.mean([metrics[f"{task}_precision"] for task in ["main", "sub", "interv", "priority"]])
    avg_recall = np.mean([metrics[f"{task}_recall"] for task in ["main", "sub", "interv", "priority"]])
    avg_f1 = np.mean([metrics[f"{task}_f1"] for task in ["main", "sub", "interv", "priority"]])

    metrics["eval_avg_acc"] = avg_acc
    metrics["eval_avg_precision"] = avg_precision
    metrics["eval_avg_recall"] = avg_recall
    metrics["eval_avg_f1"] = avg_f1

    return metrics

class MultiTaskTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = {
            "main_category_id": inputs.pop("main_category_id"),
            "sub_category_id": inputs.pop("sub_category_id"),
            "intervention_id": inputs.pop("intervention_id"),
            "priority_id": inputs.pop("priority_id")
        }
        outputs = model(**inputs, **labels)
        # outputs is a tuple: (loss, logits_main, logits_sub, logits_interv, logits_priority)

        loss = outputs[0]
        if return_outputs:
            return (loss, *outputs[1:])
        else:
            return loss

    def prediction_step(self, model, inputs, prediction_loss_only=False, ignore_keys=None):
        # Remove labels from inputs
        label_keys = ["main_category_id", "sub_category_id", "intervention_id", "priority_id"]
        labels = {key: inputs.pop(key) for key in label_keys if key in inputs}

        # Forward pass without labels
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Extract logits (assumes model returns tuple: (logits_main, logits_sub, ...)) if no loss is returned
        # Or (loss, logits_main, logits_sub, ...) if loss is returned
        
        # Check if the first element is a tensor (likely loss)
        if isinstance(outputs[0], torch.Tensor) and outputs[0].dim() == 0: # Check if it's a scalar tensor
            loss = outputs[0]
            logits = outputs[1:] # Skip loss
        else:
            loss = None
            logits = outputs # All elements are logits

        # Handle label presence
        
        if labels:
            label_values = (labels["main_category_id"], labels["sub_category_id"],
                           labels["intervention_id"], labels["priority_id"])
        
        return (loss, logits, label_values)




# Training arguments
training_args = TrainingArguments(
    # output_dir="./results",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=14,
    weight_decay=0.01,
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_avg_acc",
    greater_is_better=True,
    logging_dir='./logs',
    logging_steps=100,
)

logger.info(len(encoded_dataset["test"]))
logger.info(len(encoded_dataset["train"]))

# Initialize trainer
trainer = MultiTaskTrainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset["train"],
    eval_dataset=encoded_dataset["test"],
    
    compute_metrics=compute_metrics,
)

# Start training
trainer.train()

# Save model
trainer.save_model("CHS_tz_classifier_distilbert")
tokenizer.save_pretrained("CHS_tz_classifier_distilbert")
 

# Evaluate the model after training
new_metrics = trainer.evaluate(encoded_dataset["test"])
new_avg_acc = new_metrics.get('eval_avg_acc', 0)

logger.info(f"Model Performance results: {new_metrics}")

# Load previous best model's average accuracy
if os.path.exists(metadata_file):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    prev_avg_acc = metadata.get('eval_avg_acc', 0)
else:
    prev_avg_acc = -1

# Check if the new model is better
if new_avg_acc > prev_avg_acc:
    logger.info(" New model performance improved! Saving new version.")
    # Create new version directory
    version = len(os.listdir(model_output_dir)) -1
    new_model_dir = f"CHS_tz_classifier_distilbert{version}"
    new_model_path = os.path.join(model_output_dir, new_model_dir)

    # Save the model and tokenizer in the new version directory
    trainer.save_model(new_model_path)
    tokenizer.save_pretrained(new_model_path)

    # Update metadata file
    metadata = {
        "version": f"v{version}",
        "date_trained": str(datetime.datetime.now()),
        "eval_avg_acc": new_avg_acc,
        "last_best_model_dir": new_model_dir,
        "metrics": new_metrics
    }
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)
else:
    logger.info("Model performance did not improve. Not saving a new version.")




# %%

# Generate and save category embeddings
def generate_category_embeddings(categories, model, tokenizer, device):
    embeddings = []
    for category in categories:
        inputs = tokenizer(
            category, 
            padding="max_length", 
            truncation=True, 
            max_length=256, 
            return_tensors="pt"
        ).to(device)
        with torch.no_grad():
            emb = model.get_embeddings(**inputs).cpu().numpy()
        embeddings.append(emb[0])
    return np.array(embeddings)

# Generate embeddings for all categories
main_cat_embeddings = generate_category_embeddings(main_categories, model, tokenizer, device)
sub_cat_embeddings = generate_category_embeddings(sub_categories, model, tokenizer, device)

# Save embeddings
os.makedirs("embeddings", exist_ok=True)
np.save("embeddings/main_cat_embeddings.npy", main_cat_embeddings)
np.save("embeddings/sub_cat_embeddings.npy", sub_cat_embeddings)

# Save category lists
with open("main_categories.json", "w") as f:
    json.dump(main_categories, f)
with open("sub_categories.json", "w") as f:
    json.dump(sub_categories, f)
with open("interventions.json", "w") as f:
    json.dump(interventions, f)
with open("priorities.json", "w") as f:
    json.dump(priorities, f)

# Evaluation
metrics = trainer.evaluate(encoded_dataset["test"])
logger.info(f"Model Performance results: {metrics}")

# Save metrics
with open("multilabel_model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

logger.info(" Model performance on test set:", metrics)


# MODEL EVALUATION ---UNCOMMENT TO RUN EVALUATION ONLY ---

# Load trained model
# model_path = '/opt/chl_ai/models/raw-models/ai_models/MultiClassifier/multitask_distilbert'
model_path = f"/home/rogendo/Work/ai/ai_service/CHS_tz_classifier_distilbert{version}"
# model_path = new_model_path
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
model.eval()  # Set to evaluation mode


def classify_multitask_case_return_indices(narrative):
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
        outputs = model(**inputs)
        logits_main, logits_sub, logits_interv, logits_priority = outputs
        preds_main = torch.argmax(logits_main, dim=1).cpu().numpy()[0]
        preds_sub = torch.argmax(logits_sub, dim=1).cpu().numpy()[0]
        preds_interv = torch.argmax(logits_interv, dim=1).cpu().numpy()[0]
        preds_priority = torch.argmax(logits_priority, dim=1).cpu().numpy()[0]
    
    return preds_main, preds_sub, preds_interv, preds_priority


test_data = dataset['validation']
print(test_data)
# Collect true and predicted labels
true_main, pred_main = [], []
true_sub, pred_sub = [], []
true_interv, pred_interv = [], []
true_priority, pred_priority = [], []

for example in test_data:
    # Get true indices directly from IDs
    true_main.append(example["main_category_id"])
    true_sub.append(example["sub_category_id"])
    true_interv.append(example["intervention_id"])
    
    # Append priority_id directly, since it matches the output indices
    priority_val = example["priority_id"]
    true_priority.append(priority_val)
    
    # Get predictions
    main_idx, sub_idx, interv_idx, priority_idx = classify_multitask_case_return_indices(
        example["text"]
    )
    pred_main.append(main_idx)
    pred_sub.append(sub_idx)
    pred_interv.append(interv_idx)
    pred_priority.append(priority_idx)



def plot_enhanced_confusion_matrix(true, pred, classes, title, filename, figsize=(12, 10)):
    cm = confusion_matrix(true, pred, labels=range(len(classes)))
    
    plt.figure(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, 
                yticklabels=classes,
                cbar_kws={'shrink': 0.8})
    plt.title(f'Confusion Matrix - {title}', fontsize=16, pad=20)
    plt.ylabel('True Label', fontsize=14)
    plt.xlabel('Predicted Label', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    #  accuracy 
    accuracy = np.trace(cm) / np.sum(cm) if np.sum(cm) > 0 else 0
    plt.figtext(0.5, 0.01, f'Accuracy: {accuracy:.2%}', ha='center', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {filename}")

#  output directory
os.makedirs("confusion_matrices", exist_ok=True)

#  save confusion matrices
plot_enhanced_confusion_matrix(true_main, pred_main, main_categories,
                     "Main Category", "confusion_matrices/main_category.png")

plot_enhanced_confusion_matrix(true_sub, pred_sub, sub_categories,
                     "Sub Category", "confusion_matrices/sub_category.png")

plot_enhanced_confusion_matrix(true_interv, pred_interv, interventions,
                     "Intervention", "confusion_matrices/intervention.png")

plot_enhanced_confusion_matrix(true_priority, pred_priority, [str(p) for p in priorities],
                     "Priority", "confusion_matrices/priority.png", figsize=(10, 8))


def print_compact_report(true, pred, classes, title):
    print(f"\n{'='*60}")
    print(f"CLASSIFICATION REPORT: {title}")
    print(f"{'='*60}")
    
    # Get the classification report as a dictionary
    report = classification_report(
        true, pred, 
        labels=range(len(classes)),
        target_names=classes,
        output_dict=True,
        zero_division=0
    )
    
    # Print only classes that appear in the test data or have predictions
    present_classes = set(true) | set(pred)
    
    print(f"Classes present in test data: {len(present_classes)}/{len(classes)}")
    print("\nPerformance on present classes:")
    print(f"{'Class':30} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    
    for i in present_classes:
        class_name = classes[i]
        print(f"{class_name:30} {report[class_name]['precision']:>10.3f} "
              f"{report[class_name]['recall']:>10.3f} "
              f"{report[class_name]['f1-score']:>10.3f} "
              f"{report[class_name]['support']:>10.0f}")
    
    print(f"\nOverall Accuracy: {report['accuracy']:.3f}")
    print(f"Macro Avg F1: {report['macro avg']['f1-score']:.3f}")
    print(f"Weighted Avg F1: {report['weighted avg']['f1-score']:.3f}")

# Print compact reports
print_compact_report(true_main, pred_main, main_categories, "Main Category")
print_compact_report(true_sub, pred_sub, sub_categories, "Sub Category")
print_compact_report(true_interv, pred_interv, interventions, "Intervention")
print_compact_report(true_priority, pred_priority, [str(p) for p in priorities], "Priority")



# Additional analysis
print(f"\n{'='*60}")
print("ADDITIONAL ANALYSIS")
print(f"{'='*60}")
print(f"Test samples: {len(test_data)}")
print(f"Main categories in test data: {set([main_categories[i] for i in true_main])}")
print(f"Main categories not in test data: {set(main_categories) - set([main_categories[i] for i in true_main])}")

# Calculate and display per-task accuracy
tasks = [
    ("Main Category", true_main, pred_main),
    ("Sub Category", true_sub, pred_sub),
    ("Intervention", true_interv, pred_interv),
    ("Priority", true_priority, pred_priority)
]

print(f"\n{'Task':20} {'Accuracy':>10} {'Correct/Total':>15}")
for name, true, pred in tasks:
    correct = sum(1 for t, p in zip(true, pred) if t == p)
    accuracy = correct / len(true)
    print(f"{name:20} {accuracy:>10.2%} {f'{correct}/{len(true)}':>15}")

# %%

# {
#     "narrative": "On 15 November 2022, the helpline received a call from Salum Mwinyi, 17, in Korogwe District, Tanga Region. He wanted to understand why drug use among youth is harmful. The counselor explained the physical, social, and legal risks involved with abusing drugs, both legal drugs and illegal drugs. The counselor explained in detail about what each of the effects of the drugs and advised Salum not to get herself involveed with any drugs. Salum expressed appreciation for the advice.",
#     "main_category": "Information",
#     "sub_category": "Drug/Alcohol Abuse",
#     "intervention": "Counselling",
#     "priority": 2
# },
{
    "narrative": "On 16 November 2022, the helpline was contacted by Jafari Said, 25, from Kilombero District, Morogoro Region. He asked how to provide a safe home environment for his two young sisters. The counselor advised him on good parenting practices and protecting them from abuse.",
    "main_category": "Advice and Counselling",
    "sub_category": "Relationships (Parent/Child)",
    "intervention": "Counselling",
    "priority": 2
},
# narrative =  "On 15 November 2022, the helpline received a call from Salum Mwinyi, 17, in Korogwe District, Tanga Region. He wanted to understand why drug use among youth is harmful. The counselor explained the physical, social, and legal risks involved with abusing drugs, both legal drugs and illegal drugs. The counselor explained in detail about what each of the effects of the drugs and advised Salum not to get herself involveed with any drugs. Salum expressed appreciation for the advice.",


# %%
# narrative=" On <DATE_TIME> a girl <PERSON> (<DATE_TIME> ) from <LOCATION> district, <LOCATION> region called on 116 to report of the injustices done to her by a person who was to take care of her wellbeing. She reported that her stepfather raped her and abused her sexually and she was 2 months pregnant and is forced to abort as the stepfather threatened her that He will kill her if she does not abort. She reported that she was not the only one who was abused by the stepfather but her mother was also abused by the stepfather. "
narrative= "On 16 November 2022, the helpline was contacted by Jafari Said, 25, from Kilombero District, Morogoro Region. He asked how to provide a safe home environment for his two young sisters. The counselor advised him on good parenting practices and protecting them from abuse.",

main_idx, sub_idx, interv_idx, priority_idx = classify_multitask_case_return_indices(
    narrative[0]
)
pred_main.append(main_idx)
pred_sub.append(sub_idx)
pred_interv.append(interv_idx)
pred_priority.append(priority_idx)

print("Predicted Main Category:", main_categories[main_idx])
print("Predicted Sub Category:", sub_categories[sub_idx])
print("Predicted Intervention:", interventions[interv_idx])
print("Predicted Priority:", priorities[priority_idx])
