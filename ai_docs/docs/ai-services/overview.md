---
layout: doc
title: AI Service Overview
---

# AI Service Overview

OPENCHS integrates **state-of-the-art AI services** to transform how child helplines operate — turning every conversation into **accurate, structured, and actionable case data** while dramatically reducing the administrative burden on caseworkers.

Our design philosophy blends **AI-powered automation** with **human-centered practice**, ensuring that:
- No call is lost  
- No survivor is left unsupported  
- Every decision is backed by **real-time, data-driven insights**

---

## The End-to-End AI Workflow

The OPENCHS AI pipeline operates from the **moment a call is received** to the **moment actionable intelligence reaches decision-makers**. Below is the sequence of AI-powered steps, alongside the direct **human impact** at each stage.

---

### **1. Call Reception & Transcription** *(ASR) Whisper*
**AI Step:** Speech-to-Text   
- Handles multiple languages and accents in real time  
- Produces time-stamped transcripts for indexing and search  

---

### **2. Automatic Translation** *(Helsinki/opus-mt-mul-en)*  
- Converts transcripts into the caseworker’s preferred language  

**Human Impact:**  
*"Language and accent barriers no longer block urgent help. Every word is captured and understood."*

---

### **3. Entity Extraction** *(DistilBERT-base-uncased)*
**AI Step:** Named Entity Recognition (NER)  
- Identifies and tags **names, genders, dates, institutions, locations, contact details**, and other structured information  
- Flags sensitive PII for secure handling  

**Human Impact:**  
*"Key facts are ready the moment the caseworker opens the record — no manual retyping, no details missed."*

---

### **4. Classification** *(DistilBERT-base-uncased)*
**AI Step:** Automatic categorization of the case  
- Classifies **case category, sub-category, intervention needed, referral type**, and other metadata  
- Uses domain-specific classification model trained on real helpline data  

**Human Impact:**  
*"From chaos to clarity: AI organizes information instantly so call agents can focus on care provision"*

---

### **5. Summarization** *(Flan-T5)*
**AI Step:** This step, condenses the transcribed and translated transcript into a summary of the case.
- Extracts the **translated transcript** of the call  
- Highlights **critical events, needs, and risk factors**  
- Reduces multi-minute conversations to a **readable, high-accuracy and brief** summary.

**Human Impact:**  
*"Call agents spend less than half the time on case documentation, freeing them to support more survivors."*

---

## Why This Matters

OPENCHS AI services are **not just software** — they are a **force multiplier** for social protection systems. By automating the repetitive and accelerating the critical, we enable:

- **Faster response times** — urgent cases routed in real time  
- **Reduced administrative load** — heelpline call agents regain hours per shift  
- **Higher-quality case data** — structured, standardized, and complete  
- **Better survivor outcomes** — more timely and appropriate interventions  
- **Data-driven policy change** — grounded in real-world evidence  

---

## Training & Capacity Building

Technology alone isn’t enough. OPENCHS invests in skills transfer and capacity building, ensuring that countries and organizations can deploy, adapt, and sustain these AI capabilities. 

Crucially, AI is designed to complement — not replace — call agents: it augments their judgement by automating routine tasks (transcription, data and entity capture), surfacing critical cues, and enabling faster, more informed decisions so agents can focus on empathetic support and complex casework.

Training emphasizes hands‑on use, human‑in‑the‑loop workflows, ethical handling of sensitive data, and continuous coaching and monitoring so teams retain control, build trust in AI outputs, and feed operational insights back into model improvement.

---

**From the first word spoken to the final policy decision — OPENCHS AI keeps child protection teams informed, focused, and effective.**
