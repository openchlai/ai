# API Gateway - AI-Powered Helpline System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview
The API Gateway serves as the central interface for our AI-powered helpline system, managing and routing requests for voice processing, transcription, translation, and case prediction services. It acts as a unified entry point for all client applications, ensuring secure and efficient communication between frontend applications and backend services.

## Features
- **Intelligent Route Management**
  - Dynamic routing for voice processing endpoints
  - Load balancing and traffic distribution
  - Service discovery and health checks
  - Automated failover handling

- **Security & Authentication**
  - JWT-based authentication
  - Role-based access control (RBAC)
  - API key management
  - Rate limiting and request throttling

- **Request Processing**
  - Input validation and sanitization
  - Request/response transformation
  - Error handling and standardization
  - Logging and monitoring integration

- **Backend Integration**
  - Seamless integration with voice processing services
  - Translation service coordination
  - Case prediction service routing
  - Real-time transcription handling

## Technical Requirements
- Python 3.11+
- Docker & Docker Compose
- Redis (for rate limiting and caching)
- Node.js 18+ (for development tools)
- Prometheus & Grafana (for monitoring)

## Installation & Setup

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/gateway.git
   cd gateway
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

5. Configure environment variables in `.env`:
   ```
   PORT=3000
   NODE_ENV=development
   AUTH_SECRET=your-secret-key
   RATE_LIMIT_WINDOW=15m
   RATE_LIMIT_MAX_REQUESTS=100
   ```

### Docker Deployment
1. Build the container:
   ```bash
   docker build -t helpline-gateway .
   ```

2. Run using Docker Compose:
   ```bash
   docker-compose up -d
   ```

## API Documentation
Detailed API documentation is available in the [API Reference](../API_REFERENCE.md) document. Below is a basic endpoint structure overview:

- `POST /api/v1/voice/process` - Submit voice data for processing
- `POST /api/v1/transcribe` - Request voice-to-text transcription
- `POST /api/v1/translate` - Translate transcribed text
- `POST /api/v1/cases/predict` - Get case prediction analysis

For detailed request/response schemas and authentication requirements, refer to the API Reference document.

## Development

### Testing
Run the test suite:
```bash
pytest tests/
```

For development best practices and guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).

### Code Style
This project follows PEP 8 guidelines. Format your code using:
```bash
black .
```

### Debugging
For local debugging, you can enable debug mode in your `.env`:
```
DEBUG=true
LOG_LEVEL=debug
```
Debug logs will be available in `logs/debug.log`

### Error Handling
The gateway implements standardized error responses following RFC 7807 (Problem Details for HTTP APIs). All error responses include:
- `type`: A URI reference identifying the error type
- `title`: A short, human-readable summary of the problem
- `status`: The HTTP status code
- `detail`: A human-readable explanation of the error
- `instance`: A URI reference that identifies the specific occurrence of the error

## Security
The gateway implements multiple security layers:

- **Authentication**: JWT-based authentication for all API endpoints
- **Authorization**: Role-based access control using standardized claims
- **Rate Limiting**: Configurable rate limiting per client/endpoint
- **Input Validation**: Strict request validation and sanitization
- **Logging**: Comprehensive security event logging

For detailed security practices and configurations, refer to [SECURITY.md](../SECURITY.md).

## Architecture
The gateway is part of our microservices architecture, serving as the entry point for all client requests. For detailed architecture information, see [ARCHITECTURE.md](../ARCHITECTURE.md).

## Contributing
We welcome contributions! Please read our [Contributing Guidelines](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the terms of the LICENSE file included in the repository root.

