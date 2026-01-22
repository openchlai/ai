# OPENCHS

OPENCHS is a comprehensive case management and helpline system designed for efficient tracking, reporting, and analysis of children's helpline operations. The platform integrates communication tools, case processing, and AI-powered insights into a unified interface.

## Core Features

### Case Management
Centralized system for creating, tracking, and managing case records. Includes priority leveling, status tracking, and detailed history logs.

### Communication Tools
Integrated SIP Agent for call handling, alongside multi-channel messaging support for SMS and other digital platforms.

### AI Insights
Advanced analysis of call recordings including automated transcription, translation, case classification, and risk assessment indicators.

### Dashboard and Analytics
Real-time visualization of case statistics, source distribution, and priority metrics. Includes a wallboard for live monitoring of agent performance and call volumes.

### Quality Assurance
Automated and manual evaluation of call quality based on predefined metrics such as empathy, listening skills, and resolution effectiveness.

### User and Role Management
Comprehensive access control system for managing system users, roles (Administrator, Counseller, etc.), and permissions.

## Technical Architecture

The application is built using a modern frontend stack:
- Framework: Vue.js 3
- Styling: Tailwind CSS
- State Management: Pinia
- Routing: Vue Router
- Build Tool: Vite
- Icons: Iconify (Material Design Icons)

## Getting Started

### Prerequisites
- Node.js (Latest LTS version recommended)
- npm or yarn

### Installation
1. Clone the repository
2. Navigate to the finalui directory:
   cd finalui
3. Install dependencies:
   npm install

### Development
To start the development server:
npm run dev

### Build
To create a production build:
npm run build

## Project Structure

- src/components/: Reusable UI components organized by module (cases, calls, users, etc.)
- src/pages/: Main view components and route handlers
- src/store/: Global state management files
- src/assets/: Static assets and global styles
- src/layout/: Main application structure components (Sidebar, Header, etc.)

## Design System
The platform utilizes a customized theme featuring:
- Primary Color: Amber (Gold)
- Background: Black (Dark Mode) / White (Light Mode)
- Typography: System fonts with emphasis on clarity and high contrast
- Layout: Borderless aesthetic focused on depth through shadows and elevation
