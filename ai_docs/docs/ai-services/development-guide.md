# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.11+
- Git
- Docker (optional, for containerized development)
- NVIDIA drivers (for GPU development)

### Local Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai_service

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -r requirements-dev.txt
pip install -r requirements.txt

# 4. Download language models
python -m spacy download en_core_web_lg

# 5. Start Redis (if not using Docker)
redis-server

# 6. Start Celery worker (in separate terminal)
celery -A app.celery_app worker --loglevel=debug -E --pool=solo -Q model_processing,celery

# 7. Start API server (in separate terminal)
python -m app.main
```

## Project Structure

```
ai_service/
├── app/
│   ├── api/                 # REST API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py        # Main route definitions
│   │   └── models.py        # Pydantic request/response models
│   ├── tasks/               # Celery async tasks
│   │   ├── __init__.py
│   │   ├── audio_processing.py
│   │   └── notifications.py
│   ├── model_scripts/       # ML model inference
│   │   ├── __init__.py
│   │   ├── whisper.py       # Speech-to-text
│   │   ├── translator.py    # Translation
│   │   ├── ner.py           # Named entity recognition
│   │   ├── classifier.py    # Case classification
│   │   ├── summarizer.py    # Text summarization
│   │   └── qa.py            # Question-answering
│   ├── core/                # Core services
│   │   ├── __init__.py
│   │   ├── resource_manager.py
│   │   ├── processing_strategy.py
│   │   └── celery_monitor.py
│   ├── streaming/           # Real-time streaming
│   │   ├── __init__.py
│   │   ├── tcp_server.py    # TCP Asterisk integration
│   │   ├── websocket.py     # WebSocket connections
│   │   └── audio_buffer.py
│   ├── db/                  # Database models
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy models
│   │   └── session.py       # Database session
│   ├── config.py            # Configuration management
│   ├── celery_app.py        # Celery initialization
│   └── main.py              # Application entry point
├── tests/                   # Unit and integration tests
│   ├── test_api.py
│   ├── test_models.py
│   └── test_streaming.py
├── scripts/                 # Utility scripts
│   ├── quick_test_mock.sh
│   └── download_models.py
├── docker-compose.yml       # Multi-container setup
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example             # Environment template
└── README.md
```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_check
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Run integration tests
pytest tests/integration/ -v
```

### Test with Mock Data

```bash
# Copy test audio files
cp /path/to/audio/*.wav test_audio/

# Run quick test
./scripts/quick_test_mock.sh realtime 1

# Monitor logs
tail -f logs/ai-pipeline.log
```

## Adding New Features

### Adding a New API Endpoint

1. **Define request/response models** in `app/api/models.py`:

```python
from pydantic import BaseModel

class CustomRequest(BaseModel):
    input_text: str
    language: str = "en"

class CustomResponse(BaseModel):
    result: str
    confidence: float
```

2. **Create route** in `app/api/routes.py`:

```python
from fastapi import APIRouter
from app.api.models import CustomRequest, CustomResponse

router = APIRouter()

@router.post("/custom/process")
async def process_custom(request: CustomRequest) -> CustomResponse:
    # Implementation
    return CustomResponse(result="...", confidence=0.95)
```

3. **Register route** in `app/main.py`:

```python
from app.api.routes import router
app.include_router(router)
```

4. **Add tests** in `tests/test_api.py`:

```python
def test_custom_process():
    response = client.post("/custom/process", json={
        "input_text": "test",
        "language": "en"
    })
    assert response.status_code == 200
    assert response.json()["confidence"] > 0.5
```

### Adding a New ML Model

1. **Create model script** in `app/model_scripts/new_model.py`:

```python
from transformers import pipeline
from app.core.resource_manager import ResourceManager

class NewModel:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.device = self.resource_manager.get_device()
        self.model = pipeline("task-name", device=self.device)

    def predict(self, text: str):
        result = self.model(text)
        return result
```

2. **Add endpoint** in `app/api/routes.py`:

```python
from app.model_scripts.new_model import NewModel

model = NewModel()

@router.post("/new-model/predict")
async def predict(text: str):
    result = model.predict(text)
    return {"result": result}
```

3. **Add to processing pipeline** if needed:

Update `app/tasks/audio_processing.py` to include the new model in the pipeline.

## Debugging

### Enable Debug Logging

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run with verbose logging
python -m app.main --debug
```

### View Logs

```bash
# API server logs
tail -f logs/api.log

# Celery worker logs
tail -f logs/celery.log

# Combined logs
tail -f logs/*.log | grep ERROR
```

### Debug with Flower

```bash
# Start Flower (Celery monitoring)
celery -A app.celery_app flower --port=5555

# Access in browser
open http://localhost:5555
```

### Debug with Python Debugger

```python
# In your code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

## Code Quality

### Linting

```bash
# Check code style
flake8 app/

# Format code
black app/

# Type checking
mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Performance Profiling

### Profile CPU Usage

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

### Profile Memory Usage

```bash
# Install memory-profiler
pip install memory-profiler

# Profile a function
python -m memory_profiler your_script.py
```

## Documentation

### Update API Documentation

API documentation is automatically generated from docstrings. Format like this:

```python
@router.post("/endpoint")
async def endpoint_function(param: str) -> dict:
    """
    Process input and return result.

    Args:
        param: Input parameter description

    Returns:
        dict: Response with results
    """
```

### Generate Docs

```bash
# API docs available at
http://localhost:8125/docs

# Alternative docs
http://localhost:8125/redoc
```

## Release Process

1. **Update version** in `app/config.py`
2. **Update CHANGELOG**
3. **Create git tag**: `git tag v0.2.0`
4. **Push tag**: `git push origin v0.2.0`
5. **Docker image**: Automatically built and pushed by CI/CD

## Common Development Tasks

### Adding a New Language

Update language support in model configuration:

```bash
# In .env
HF_ASR_MODEL=openai/whisper-large-v3  # Already supports 99+ languages
```

### Updating Models

```bash
# Download new model versions
python scripts/download_models.py

# Update configuration
export HF_ASR_MODEL=new/model-name

# Restart workers
docker-compose restart celery-worker
```

### Monitoring Resource Usage

```bash
# Check GPU usage
nvidia-smi

# Check CPU and memory
top -b -n 1

# Monitor in Docker
docker stats celery-worker
```
