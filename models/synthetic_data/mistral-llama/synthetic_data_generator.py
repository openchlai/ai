import csv
import random
import logging
from datetime import datetime
from llama_cpp import Llama

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load Mistral model
logging.info("🔁 Loading Mistral model...")
try:
    llm = Llama(
        model_path="/Users/mac/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        n_ctx=2048,
        n_threads=6,
        n_gpu_layers=16,
        verbose=False
    )
    logging.info("✅ Model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Failed to load model: {e}")
    exit(1)

# Load case categories
try:
    with open('case_categories_ke.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        case_categories = [row for row in reader]
    logging.info(f"📂 Loaded {len(case_categories)} case categories.")
except FileNotFoundError:
    logging.error("❌ case_categories_ke.csv not found.")
    exit(1)

def generate_narrative(client_name, client_age, client_sex, category, definition):
    prompt = f"""You are a child protection officer writing a case report.
Create a 3-sentence realistic case narrative for the following:

Client: {client_name}, a {client_age}-year-old {client_sex}
Case Category: {category}
Definition: {definition}

Narrative:"""
    try:
        output = llm.create_completion(prompt=prompt, max_tokens=120, stop=["\n", "###"])
        return output["choices"][0]["text"].strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to generate narrative: {e}")
        return "Narrative generation failed."

def generate_case_records(num_cases):
    cases = []
    for i in range(1, num_cases + 1):
        case_id = f"CASE-{i:04d}"
        category = random.choice(case_categories)

        client_name = random.choice(["Mary", "John", "Amina", "Peter", "Faith", "Samuel"])
        client_age = random.randint(4, 17)
        client_sex = random.choice(["Male", "Female"])

        logging.info(f"📝 Generating case {case_id} for {client_name}, {client_age}yo {client_sex} under '{category['Case_Category']}'...")
        narrative = generate_narrative(client_name, client_age, client_sex, category["Case_Category"], category["Definition"])

        case_plan = random.choice([
            "Immediate protection and psychosocial support",
            "Medical referral and legal support",
            "Community engagement and school reintegration",
            "Placement in temporary care and follow-up"
        ])

        cases.append({
            "case_id": case_id,
            "category_name": category["Case_Category"],
            "narrative": narrative,
            "case_plan": case_plan,
            "incident_date": datetime.now().strftime('%Y-%m-%d'),
            "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
    return cases

# Generate records
logging.info("🚀 Starting case generation...")
records = generate_case_records(1000)
logging.info("✅ Case generation completed.")

# Save to CSV
output_file = 'generated_child_protection_cases.csv'
try:
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['case_id', 'category_name', 'narrative', 'case_plan', 'incident_date', 'report_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    logging.info(f"📁 Saved {len(records)} records to {output_file}.")
except Exception as e:
    logging.error(f"❌ Failed to write CSV: {e}")
