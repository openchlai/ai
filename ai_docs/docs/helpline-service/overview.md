# Helpline Service - Overview

## What is the Helpline Service?

The **openCHS Helpline Case Management System** is a comprehensive, production-ready platform designed for child protection helplines, crisis centers, and call management services. It provides integrated case management, multi-channel communication handling, and AI-powered analytics to improve response efficiency and decision-making.

## Core Purpose

Transform how helplines operate by providing:
- **Integrated case management** with automated workflow
- **AI-assisted processing** for transcription, translation, and analysis
- **Real-time dashboards** for supervisors and managers
- **Data-driven insights** for child protection decisions
- **Multi-channel support** for calls, SMS, and web messages

## Key Features

### Case Management
- Create and track cases with detailed information
- Automatic case categorization and risk assessment
- Timeline tracking of all interactions
- File and document attachments
- Case status workflow (New → In Progress → Closed)

### Client Management
- Maintain comprehensive client profiles
- Track contacts and relationships
- Manage reporter and perpetrator information
- History of all interactions with clients

### Communication Handling
- **Phone/VoIP Integration**: Direct call handling with real-time transcription
- **SMS Support**: Send and receive SMS communications
- **Multi-channel Unified Inbox**: View all communications in one place
- **Message Archiving**: Complete communication history

### Agent & Team Management
- User roles: Agent, Supervisor, Admin
- Granular permission controls
- Agent availability tracking
- Call queue management
- Performance monitoring

### Dashboard & Analytics
- Real-time call statistics
- Agent performance metrics
- Case load distribution
- Response time tracking
- Data visualization and reporting

### AI Integration
When connected to the openCHS AI Service, the Helpline gains:
- **Automatic transcription** of phone calls
- **Real-time translation** between languages
- **Entity extraction** (names, locations, dates)
- **Case classification** and risk scoring
- **Call summarization** for case notes
- **Actionable insights** for decision-making

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | PHP REST API |
| **Frontend** | PHP, HTML, CSS, JavaScript |
| **Database** | MySQL 8.0+ |
| **Web Server** | Nginx |
| **Containerization** | Docker & Docker Compose |
| **AI Services** | Python, FastAPI, Celery, PyTorch |

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌──────────────────┴──────────────────┐
       ↓                                      ↓
┌──────────────────┐               ┌──────────────────┐
│  PHP Frontend    │               │   PHP REST API   │
│  (Web UI)        │               │   (Backend)      │
└──────────────────┘               └──────────────────┘
                                            ↓
                                    ┌──────────────────┐
                                    │   MySQL 8.0      │
                                    │   (Database)     │
                                    └──────────────────┘
       ┌─────────────────────────────────────┐
       ↓                                       ↓
┌─────────────────────┐           ┌──────────────────┐
│  VoIP/Phone System  │           │  AI Pipeline     │
│  (Optional)         │           │  (Optional)      │
└─────────────────────┘           └──────────────────┘
```

## Deployment Modes

### Development
- Local Docker setup for testing
- Hot-reload enabled
- Debug logging
- Sample data included

### Staging
- Full containerized deployment
- CI/CD pipeline integration
- Automated testing
- Access at: `http://192.168.10.119/helpline`

### Production
- Scaled container architecture
- Load balancing
- Backup and disaster recovery
- SSL/TLS encryption
- Full audit logging

## Use Cases

### Child Protection Services
- Receive and triage crisis calls
- Create and manage child protection cases
- Coordinate with field teams
- Document interventions and follow-ups

### Crisis Hotlines
- 24/7 call center operations
- Emergency case handling
- Rapid response coordination
- Real-time supervisor oversight

### NGO Case Management
- Client intake and assessment
- Service delivery tracking
- Outcome measurement
- Impact reporting

### Healthcare Facilities
- Patient intake
- Appointment management
- Follow-up tracking
- Service coordination

## Key Benefits

✅ **Centralized Management**: All cases, contacts, and communications in one system

✅ **Efficiency**: Automated workflows reduce manual data entry

✅ **Quality**: AI-assisted analysis improves case quality

✅ **Visibility**: Real-time dashboards for supervisors and managers

✅ **Scalability**: Docker-based deployment supports any scale

✅ **Integration**: Open API for third-party integrations

✅ **Security**: Role-based access control and audit trails

✅ **Compliance**: Supports data privacy and protection requirements

## Next Steps

1. **Get Started**: [Quick Start Guide](./quick-start.md)
2. **Deploy**: [Installation & Deployment](./installation/overview.md)
3. **Configure**: [Configuration Guide](./configuration.md)
4. **Develop**: [Developer Guide](./development.md)
5. **Learn**: [API Reference](./api-reference/overview.md)
