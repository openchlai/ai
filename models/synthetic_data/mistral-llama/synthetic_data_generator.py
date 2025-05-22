import csv
import os
import random
import logging
from datetime import datetime
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# Download the model to HF cache
model_path = hf_hub_download(
    repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
)

# Now you can use this path in your llama_cpp initialization
print(f"Model downloaded to: {model_path}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load Mistral model
# Load Mistral model
logging.info("🔁 Loading Mistral model...")
try:
    cuda_available = False
    try:
        # Try to get CUDA_HOME environment variable
        cuda_home = os.environ.get('CUDA_HOME') or os.environ.get('CUDA_PATH')
        
        # Check if nvidia-smi exists and can be executed
        import subprocess
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cuda_available = result.returncode == 0
        
        if cuda_available:
            logging.info("✅ CUDA is available. Using GPU acceleration.")
        else:
            logging.warning("⚠️ CUDA is not available. Using CPU only.")
    except:
        logging.warning("⚠️ Failed to check CUDA availability. Using CPU only.")


    llm = Llama(
        model_path=model_path,  # Use the cached model path
        n_ctx=2048,
        n_threads=6,
        n_gpu_layers=-1,
        n_batch=512,
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

import random
from datetime import datetime

def generate_childline_case(client_name, client_age, client_sex, category, definition):
    """Generate CPIMS+ compliant narratives for Childline 116 reports"""
    
    # Kenyan child protection ecosystem
    COUNTY_PROFILES = {
        "Nairobi": {"risk_factors": ["Street families", "Sexual exploitation", "Drug abuse"], "response_team": "NCCG Rapid Response"},
        "Kakamega": {"risk_factors": ["Child labor", "Teen pregnancy", "FGM"], "response_team": "Luhya Child Network"},
        "Mandera": {"risk_factors": ["Early marriage", "Al-Shabaab recruitment", "Pastoralist neglect"], "response_team": "ASAL Protection Unit"}
    }
    
    # Age-specific interventions (aligned with Kenyan guidelines)
    AGE_GROUPS = {
        "0-5": {
            "indicators": ["Severe malnutrition (MUAC<11.5cm)", "Abandonment", "Developmental delays"],
            "actions": ["ECD referral", "Linda Mama nutrition", "Safe shelter placement"]
        },
        "6-12": {
            "indicators": ["School dropout", "Child labor", "Physical abuse marks"],
            "actions": ["Bursary referral", "Child labor rescue", "Counseling"]
        },
        "13-17": {
            "indicators": ["Teen pregnancy", "Substance abuse", "GBV"],
            "actions": ["Youth-friendly SRH", "Rehabilitation", "Vocational training"]
        }
    }
    
    # Auto-generate Kenyan details if missing
    county = random.choice(list(COUNTY_PROFILES.keys()))
    age_group = "0-5" if int(client_age) <=5 else "6-12" if int(client_age) <=12 else "13-17"
    
    if not client_name:
        client_name = random.choice(["Akinyi", "Kamau", "Chebet", "Kipchoge"]) + f" ({county})"
    
    # Childline-specific reporting metadata
    call_metadata = {
        "call_id": f"116/{datetime.now().strftime('%y%m%d')}/{random.randint(100,999)}",
        "call_time": f"{random.randint(8,20)}:{random.choice(['00','15','30','45'])}",
        "call_type": random.choice(["Child", "Bystander", "Professional referral"]),
        "risk_level": random.choice(["Immediate", "High", "Medium"])
    }
    
    # Build CPIMS+ compliant prompt
    prompt = f"""Generate a Childline 116 case report with:
    
**Call Details**:
- Call ID: {call_metadata['call_id']} | Time: {call_metadata['call_time']}HRS
- Reporter: {call_metadata['call_type']} | Risk: {call_metadata['risk_level']}
- County: {county} | Risk Factors: {random.choice(COUNTY_PROFILES[county]['risk_factors'])}

**Child Profile**:
- Name: {client_name} | Age: {client_age} ({age_group}) | Sex: {client_sex}
- Vulnerability: {random.choice(AGE_GROUPS[age_group]['indicators'])}

**Case Details**:
- Category: {category} ({definition})
- Childline Action: {random.choice(["Immediate rescue", "Referral to CCI", "Counseling"])}
- Legal Basis: {random.choice(["Children Act 2022 S.13", "Sexual Offences Act S.20", "Counter-Trafficking Act"])}

**Required Format**:
"Call 116/240515/123 at 14:30HRS from teacher reporting 9-year-old Wanjiru (Nairobi) with burn marks from domestic violence. Immediate rescue initiated with NCCG team. Case CPIMS/2405/456 opened under Children Act S.13 (Vulnerability Code P1.2)."

**Current Report**:"""
    
    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=200,
            temperature=0.3  # Low for factual accuracy
        )
        
        narrative = response["choices"][0]["text"].strip()
        
        # Add CPIMS+ footer
        footer = (
            f"\n\n**CPIMS+ Actions**\n"
            f"• Case ID: CPIMS/{datetime.now().strftime('%y%m')}/{random.randint(1000,9999)}\n"
            f"• Responder: {COUNTY_PROFILES[county]['response_team']}\n"
            f"• Intervention: {random.choice(AGE_GROUPS[age_group]['actions'])}\n"
            f"• Deadline: {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        return narrative + footer
        
    except Exception as e:
        return (
            f"🚨 Childline 116 Report Incomplete\n"
            f"Required follow-up:\n"
            f"- Verify {random.choice(['caregiver identity','school records','medical report'])}\n"
            f"- Contact {random.choice(['local chief','SCCO','CCI partner'])}"
        )

# Example usage
print(generate_childline_case("", "14", "female", "Sexual abuse", "Defilement by relative"))

def generate_case_records(num_cases):
    cases = []
    for i in range(1, num_cases + 1):
        case_id = f"CASE-{i:04d}"
        category = random.choice(case_categories)

        client_name = random.choice(["Mary", "John", "Amina", "Peter", "Faith", "Samuel"])
        client_age = random.randint(4, 17)
        client_sex = random.choice(["Male", "Female"])

        logging.info(f"📝 Generating case {case_id} for {client_name}, {client_age}yo {client_sex} under '{category['Case_Category']}'...")
        narrative = generate_childline_case(client_name, client_age, client_sex, category["Case_Category"], category["Definition"])

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
records = generate_case_records(10)
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
