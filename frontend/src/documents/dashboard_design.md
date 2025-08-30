# Child Helpline AI-Enabled Dashboard Brief

## Purpose
The dashboard is the central interface for monitoring, managing, and analyzing the operations of the Child Helpline Call Center.  
It combines **real-time call data**, **case management insights**, and **AI-driven analytics** to support **agents, supervisors, and managers** in providing timely and effective child protection services.

---

## User Roles & Views
- **Agent View**
  - Personal call queue
  - AI-powered transcription and translation
  - Case history & follow-up reminders
- **Supervisor View**
  - Real-time call monitoring
  - Team performance tracking
  - Escalation management with AI summaries
- **Executive View**
  - High-level KPIs
  - Case distribution by type/severity
  - Geographic and trend insights

---

## Dashboard Sections

### 1. Real-Time Call Center Overview
- **Active Calls**: number of ongoing calls, wait times, queue length  
- **Agent Status**: available / on call / break / offline  
- **Call Volume Trends**: calls per hour/day, peak hours (line chart)  
- **Abandoned Calls**: count + %  
- **Geographic Map of Calls** (if location data available)  

### 2. Case Management Insights
- **New Cases Today** (by category)  
- **Case Severity Breakdown** (AI-driven: high / medium / low)  
- **Case Progress Funnel**: open → under review → referred → closed  
- **Repeat Caller Detection** (AI flagging)  
- **Pending Follow-ups** (reminders)  

### 3. AI Analytics & Automation
- **Live Transcriptions** (searchable)  
- **Language Translation Summaries**  
- **Case Prediction Tags** (e.g., GBV, child labor, neglect)  
- **Sentiment Analysis** (emotional tone of caller)  
- **Risk Heatmap** (high-risk cases in queue)  

### 4. Performance & KPIs
- **Daily/Weekly Reports**: calls handled, resolved, escalated  
- **Agent Metrics**: response time, resolved cases, satisfaction scores  
- **Resolution Times** (median, trend)  
- **Quality Monitoring**: AI-flagged cases for review  

### 5. Child Protection Metrics
- **Case Type Breakdown**: violence, neglect, trafficking, etc.  
- **Referral Outcomes**: % referred to police, social worker, medical support  
- **Follow-up Compliance** (% within SLA)  
- **Hotspot Map**: regions with recurring cases  

### 6. Privacy & Security Indicators
- **Anonymization Status** (% anonymized cases)  
- **Access Logs** (latest activity)  
- **Encryption/Masking Alerts**  

### 7. Supervisor Tools
- **Live Call Listening**  
- **Whisper Coaching** (private prompts for agents)  
- **AI Case Summaries** (fast escalation support)  
- **Workload Distribution**  

---

## Design Guidelines

### Layout
- **Top Navigation Bar**: role switcher (Agent / Supervisor / Executive)  
- **Left Sidebar**: quick navigation (Calls, Cases, AI Insights, Reports, Settings)  
- **Main Panel**: real-time widgets + visualizations  
- **Right Panel (Optional)**: alerts, notifications, reminders  

### Visual Style
- **Clean, minimal UI** with focus on readability  
- **Rounded cards (2xl)** with soft shadows  
- **Consistent spacing & grid layout** (4/8 px system)  
- **Typography**:  
  - Headlines: medium-large (e.g., 18–24px, bold)  
  - Body text: 14–16px, regular  
- **Color Scheme**:  
  - Neutral base (light/dark mode)  
  - Highlight colors for **status indicators** (Green = safe, Orange = medium, Red = urgent)  
  - Blue accents for active states and AI-driven insights  

### Visualization Components
- **Line Charts**: call trends over time  
- **Pie/Donut Charts**: case type distribution, referral outcomes  
- **Heatmaps**: high-risk areas or case density by geography  
- **Funnel Charts**: case lifecycle (open → closed)  
- **Word Clouds**: frequent keywords from transcripts  

### Interactivity
- **Hover tooltips** for metrics and charts  
- **Drill-down capabilities** (click a case type to view details)  
- **Filters**: time range, location, case type, severity  
- **Searchable transcriptions & cases**  

---

## Deliverables for UI/UX Designer
1. **Wireframes** for Agent, Supervisor, and Executive dashboards  
2. **UI Kit** with cards, charts, tables, and status indicators  
3. **Prototype (Figma/Sketch/XD)** for role-specific flows  
4. **Responsive Layout**: desktop-first, but adaptable to tablet  

---
