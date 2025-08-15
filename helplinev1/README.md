---
layout: doc
title: Helpline Getting Started
---

# Helpline Case Management System - Getting Started

The **openCHS Helpline Case Management System** is a comprehensive platform designed for child protection helplines and call centers. It combines **web-based case management** with **AI-assisted services** to improve response efficiency, case quality, and decision-making.

This guide walks you through setting up and accessing the system, from prerequisites to deployment.

---

## Key Features

- **Case Management:** Create, update, and track cases with detailed narratives, categorization, and status updates.  
- **Client & Contact Management:** Maintain records for clients, reporters, and perpetrators.  
- **Multi-channel Communication:** Handle calls (VoIP), SMS, and other message sources.  
- **User Roles & Permissions:** Agent, Supervisor, and Admin roles with specific access rights.  
- **Dashboard & Reporting:** Real-time and historical data visualization for calls, case loads, and agent performance.  
- **Call Center Operations:** Monitor agents, calls, and queue statuses.  
- **Authentication:** Secure OTP-based login.  
- **File Attachments:** Attach documents or media to cases.  
- **AI Integration:** Optional AI modules for transcription, translation, entity extraction, classification, summarization, and actionable insights.

---

## Technology Stack

- **Backend:** PHP (custom REST API)  
- **Frontend:** PHP, HTML, CSS, JavaScript  
- **Database:** MySQL 8.0  
- **Web Server:** Nginx  
- **Containerization:** Docker & Docker Compose  
- **AI Services:** Python, FastAPI, Celery, PyTorch, Whisper, spaCy, Transformers

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)  
- Optional GPU for AI acceleration (for transcription, translation, and NLP processing)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd helplinev1
2. Configure Environment
Copy the environment template and edit settings as needed:

bash
Copy
Edit
cp .env.example .env
nano .env
Configure database credentials, AI service URLs, and resource limits.

3. Start the Services
Run the following command to build and start all containers:

bash
Copy
Edit
docker-compose up -d
This will start:

Nginx web server

PHP-FPM backend

MySQL database (initialized with required schema)

Optional AI pipeline containers if enabled

4. Access the Application
Open your browser and navigate to:
http://localhost:8888

Log in with the default admin credentials (update on first login).

Project Structure
bash
Copy
Edit
/
├── application/        # Frontend (PHP, JS, CSS)
├── rest_api/           # Backend API (PHP)
│   ├── api/            # Endpoint logic
│   ├── lib/            # Core libraries (rest.php, session.php)
│   └── config/         # Database schemas & configuration
├── docker/             # Dockerfiles and service configs
│   ├── mysql/
│   ├── nginx/
│   └── php/
├── ai_service/         # AI pipeline (optional, FastAPI + Celery)
└── docker-compose.yml  # Orchestrates all containers
Integrating AI Services
If AI services are enabled, the system automatically connects to the openCHS AI pipeline to provide:

Real-time transcription and translation

Named Entity Extraction

Case Classification and Risk Scoring

Summarization of call narratives

Data-driven insights for dashboards and reporting

AI services can be deployed in separate containers or on a GPU-enabled server for performance.

API Documentation
The backend REST API provides full access to case data and system functions.
See the API Reference for endpoints, request/response formats, and data models.

Next Steps:

Configure user roles and permissions

Connect AI services if needed

Start logging calls and creating cases

Explore dashboards and reporting for actionable insights

vbnet
Copy
Edit

