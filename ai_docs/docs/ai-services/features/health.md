# Health Monitoring

## 1. System Overview

The **AI Service Health Monitoring System** provides comprehensive real-time monitoring and diagnostics for all components of the BITZ AI Service pipeline. This system enables administrators and developers to monitor model readiness, system resources, task queues, and overall service health through a suite of RESTful API endpoints.

### Key Features
- **Real-time Model Status:** Monitor loading state, device allocation, and readiness of all ML models
- **Dependency Tracking:** Automatic detection of model dependencies and blocking issues
- **Resource Monitoring:** CPU, memory, GPU utilization, and disk space tracking
- **Task Queue Health:** Celery worker status and task queue metrics
- **System Capabilities:** ML framework detection and hardware capabilities
- **Multi-level Health Checks:** Basic, detailed, and component-specific health endpoints

### Architecture Components
The health monitoring system integrates with:
- **Model Loader:** Tracks model initialization, dependencies, and readiness states
- **Celery Workers:** Monitors background task processing and queue status
- **Resource Manager:** Tracks system resource utilization and availability
- **GPU Manager:** Monitors CUDA availability and GPU memory
- **Redis:** Health checks for cache and task queue connectivity

---

## 2. Health Monitoring Architecture

### 2.1. Configuration Layer

Health monitoring is configured through the central settings system (`app/config/settings.py`):

```python
class Settings(BaseSettings):
    # Performance and Monitoring
    enable_queue_metrics: bool = True
    alert_queue_size: int = 15
    alert_memory_usage: int = 90
    
    # Resource Management
    max_concurrent_gpu_requests: int = 1
    max_queue_size: int = 20
    request_timeout: int = 300
    queue_monitor_interval: int = 30
    
    # Model Configuration
    model_cache_size: int = 8192
    cleanup_interval: int = 3600
    enable_model_loading: bool = True
    
    # System
    site_id: str = "unknown-site"
    debug: bool = True
    log_level: str = "INFO"
```

**Docker Environment Detection:**

```python
def initialize_paths(self):
    """Initialize paths - automatically detect Docker environment"""
    self.docker_container = os.getenv("DOCKER_CONTAINER") is not None or os.path.exists("/.dockerenv")
    
    ...
```

### 2.2. Model Loader Integration

The health system integrates with the `ModelLoader` class to track model states:

```python
class ModelLoader:
    """Central model management with dependency tracking"""
    
    def __init__(self):
        self.models = {}
        self.model_status = {}
        self.dependencies = {
            "whisper": [],
            "translator": [],
            "classifier": ["translator"],
            "ner": ["translator"],
            "summarizer": ["translator"],
            "qa": ["translator"]
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get detailed status of all models"""
        
    
    def get_ready_models(self) -> List[str]:
        """Get list of models that are loaded and ready"""
        
    def get_implementable_models(self) -> List[str]:
        """Get models that CAN be loaded (no blocking dependencies)"""
       
    
    def get_blocked_models(self) -> List[str]:
        """Get models that CANNOT be loaded (have blocking dependencies)"""
        
    
    def is_model_ready(self, model_name: str) -> bool:
        """Check if model is loaded and all dependencies are ready"""
        
    
    def get_blocking_dependencies(self, model_name: str) -> List[str]:
        """Get list of dependencies that are blocking this model"""
        
```

### 2.3. Health Routes Implementation

Health endpoints are exposed through FastAPI routes (`app/api/endpoints/health_routes.py`):

### 2.4. Model Status States

The health system tracks three distinct model states:

**Ready Models:**
- Model is loaded in memory
- All dependencies are satisfied
- Available for inference requests

**Implementable Models:**
- Model can be loaded
- No blocking dependencies
- Not yet initialized

**Blocked Models:**
- Cannot be loaded
- Has unsatisfied dependencies
- Requires dependency resolution first

**Dependency Graph Example:**

```
whisper (no dependencies) → READY
    ↓
translator (no dependencies) → READY
    ↓
    ├── classifier (depends on translator) → READY
    ├── ner (depends on translator) → READY
    ├── summarizer (depends on translator) → READY
    └── qa (depends on translator) → READY
```

### 2.5. Alert System

The health monitoring system includes configurable alert thresholds:

```python
# Configuration in settings.py
alert_queue_size: int = 15          # Alert when task queue exceeds this
alert_memory_usage: int = 90        # Alert when memory usage exceeds this %
enable_queue_metrics: bool = True   # Enable task queue monitoring
```

**Alert Conditions:**

```python
"alerts": {
    "high_memory": memory.percent > settings.alert_memory_usage,
    "high_disk": disk.percent > 90,
    "high_cpu": cpu_average > 90,
    "high_queue": queue_size > settings.alert_queue_size
}
```

---

## 3. Health Endpoints Reference

### 3.1. Basic Health Check

**Endpoint:**
```
GET /health/
```

**Description:**  
Lightweight health check that returns 200 if the service is running. Use this for simple uptime monitoring and load balancer health checks.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/"
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T15:54:56.431002",
  "version": "0.1.0",
  "site_id": "unknown-site"
}

```

**Use Cases:**
- Load balancer health checks
- Simple uptime monitoring
- Service availability verification
- Kubernetes liveness probes

---

### 3.2. Detailed Health Check

**Endpoint:**
```
GET /health/detailed
```

**Description:**  
Comprehensive health check including system resources, GPU status, model readiness, and Redis connectivity. Use this for detailed system diagnostics.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/detailed"
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T15:55:46.595516",
  "version": "0.1.0",
  "site_id": "unknown-site",
  "issues": [],
  "system": {
    "platform": "Linux-6.14.0-33-generic-x86_64-with-glibc2.39",
    "cpu_count": 32,
    "memory_total": 33401266176,
    "memory_available": 21742706688,
    "memory_percent": 34.9,
    "disk_usage": 97
  },
  "gpu": {
    "gpu_available": true,
    "gpu_count": 1,
    "current_device": 0,
    "device_name": "NVIDIA GeForce RTX 4060 Ti",
    "memory_allocated": 5187596288,
    "memory_reserved": 5846859776,
    "memory_available": 16720723968
  },
  "queue": {
    "queue_size": 0,
    "max_queue_size": 100
  },
  "models": {
    "total": 6,
    "ready": 6,
    "implementable": 6,
    "blocked": 0,
    "ready_models": [
      "whisper",
      "ner",
      "classifier_model",
      "translator",
      "summarizer",
      "qa"
    ],
    "implementable_models": [
      "whisper",
      "ner",
      "classifier_model",
      "translator",
      "summarizer",
      "qa"
    ],
    "blocked_models": [],
    "details": {
      "whisper": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:15.618404",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "loaded": true,
          "variant": "large_v3",
          "strategy": "whisper_builtin",
          "model_path": "/home/ai/ai_service/models/whisper_large_v3",
          "supports_builtin_translation": true,
          "translation_strategy_active": "whisper_builtin",
          "model_info": {
            "model_name": "whisper",
            "model_path": "/home/ai/ai_service/models/whisper_large_v3",
            "fallback_model_id": "openchs/asr-whisper-helpline-sw-v1",
            "model_type": "speech-to-text",
            "framework": "transformers",
            "device": "cuda:0",
            "torch_dtype": "torch.float16",
            "is_loaded": true,
            "error": null,
            "supported_formats": [
              "wav",
              "mp3",
              "flac",
              "m4a",
              "ogg"
            ],
            "max_audio_length": "unlimited (chunked processing)",
            "sample_rate": "16kHz",
            "tasks_supported": "transcribe, translate",
            "languages": "multilingual (99+ languages)",
            "version": "large-v3",
            "current_model_id": "openchs/asr-whisper-helpline-sw-v1",
            "translation_enabled": true,
            "long_form_support": true,
            "supported_language_codes": [ "auto","en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi", "sw", "am", "lg", "rw", "so", "yo", "ig", "ha", "zu", "xh", "af", "ny"],
            "local_model_available": false
          }
        },
        "description": "Speech-to-text transcription"
      },
      "ner": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:16.536430",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "model_path": "./models/ner",
          "fallback_model_name": "en_core_web_lg",
          "hf_model_name": "spacy/en_core_web_lg",
          "hf_repo_id": "openchs/ner_distillbert_v1",
          "model_type": null,
          "loaded": true,
          "load_time": "2025-11-04T15:54:16.536326",
          "error": null,
          "transformers_available": true,
          "use_hf": true
        },
        "description": "Named Entity Recognition"
      },
      "classifier_model": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:19.204168",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "model_path": "./models/classifier",
          "loaded": true,
          "load_time": "2025-11-04T15:54:19.204055",
          "device": "cuda",
          "error": null,
          "max_length": 256,
          "chunking_supported": true,
          "aggregation_strategy": "weighted_voting",
          "priority_escalation": true,
          "num_categories": {
            "main": 7,
            "sub": 65,
            "intervention": 5,
            "priority": 3
          },
          "model_type": "MultiTaskDistilBert",
          "tokenizer": "DistilBertTokenizerFast"
        },
        "description": "Text classification"
      },
      "translator": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:21.201036",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "model_path": "./models/translation",
          "hf_repo_id": "openchs/sw-en-opus-mt-mul-en-v1",
          "device": "cuda",
          "loaded": true,
          "load_time": "2025-11-04T15:54:21.200934",
          "error": null,
          "max_length": 512,
          "chunking_supported": true,
          "fallback_strategies": [
            "chunked_translation",
            "memory_cleanup",
            "retry_logic"
          ]
        },
        "description": "Text translation"
      },
      "summarizer": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:22.953247",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "model_path": "./models/summarization",
          "device": "cuda",
          "loaded": true,
          "load_time": "2025-11-04T15:54:22.953182",
          "error": null,
          "task": "text-summarization",
          "framework": "transformers",
          "max_length": 512,
          "chunking_supported": true,
          "summarization_strategies": [
            "single_pass",
            "hierarchical"
          ],
          "fallback_strategy": "extractive_summary"
        },
        "description": "Text summarization"
      },
      "qa": {
        "loaded": true,
        "error": null,
        "load_time": "2025-11-04T15:54:25.265287",
        "dependencies_available": true,
        "missing_dependencies": [],
        "info": {
          "model_path": "/home/ai/ai_service/models/all_qa_distilbert_v1",
          "loaded": true,
          "load_time": "2025-11-04T15:54:25.265091",
          "device": "cuda",
          "error": null,
          "max_length": 512,
          "model_type": "MultiHeadQAClassifier",
          "qa_heads": [
            "opening",
            "listening",
            "proactiveness",
            "resolution",
            "hold",
            "closing"
          ]
        },
        "description": "QA scoring"
      }
    }
  },
  "capabilities": {
    "available_libraries": {
      "torch": "2.7.1+cu126",
      "transformers": "4.56.2",
      "spacy": "3.8.7",
      "librosa": "0.11.0",
      "soundfile": "0.13.1",
      "sklearn": "1.7.2",
      "numpy": "2.3.3"
    },
    "models_path": "/home/ai/ai_service/models",
    "total_models": 6,
    "loaded_models": 6,
    "ready_for_implementation": 6,
    "missing_dependencies": 0,
    "ml_capabilities": {
      "gpu_processing": true,
      "transformer_models": true,
      "audio_processing": true,
      "nlp_processing": true,
      "classical_ml": true,
      "numerical_computing": true
    }
  }
}
```

**Status Values:**
- `healthy`: All systems operational, models ready
- `degraded`: Service running but some models not ready
- `unhealthy`: Critical failures detected

**Use Cases:**
- Dashboard monitoring
- System diagnostics
- Capacity planning
- Performance analysis
- Kubernetes readiness probes

---

### 3.3. Models Health Check

**Endpoint:**
```
GET /health/models
```

**Description:**  
Detailed status of all ML models including loading state, dependencies, and blocking issues. Critical for understanding model availability and troubleshooting loading problems.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/models"
```

**Response (200):**
```json
{
  "timestamp": "2025-11-04T16:00:21.173384",
  "system_capabilities": {
    "available_libraries": {
      "torch": "2.7.1+cu126",
      "transformers": "4.56.2",
      "spacy": "3.8.7",
      "librosa": "0.11.0",
      "soundfile": "0.13.1",
      "sklearn": "1.7.2",
      "numpy": "2.3.3"
    },
    "models_path": "/home/ai/ai_service/models",
    "total_models": 6,
    "loaded_models": 6,
    "ready_for_implementation": 6,
    "missing_dependencies": 0,
    "ml_capabilities": {
      "gpu_processing": true,
      "transformer_models": true,
      "audio_processing": true,
      "nlp_processing": true,
      "classical_ml": true,
      "numerical_computing": true
    }
  },
  "summary": {
    "total": 6,
    "ready": 6,
    "implementable": 6,
    "blocked": 0
  },
  "ready_models": [
    "whisper",
    "ner",
    "classifier_model",
    "translator",
    "summarizer",
    "qa"
  ],
  "implementable_models": [
    "whisper",
    "ner",
    "classifier_model",
    "translator",
    "summarizer",
    "qa"
  ],
  "blocked_models": [],
  "missing_dependencies": {},
  "details": {
    "whisper": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:15.618404",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "loaded": true,
        "variant": "large_v3",
        "strategy": "whisper_builtin",
        "model_path": "/home/ai/ai_service/models/whisper_large_v3",
        "supports_builtin_translation": true,
        "translation_strategy_active": "whisper_builtin",
        "model_info": {
          "model_name": "whisper",
          "model_path": "/home/ai/ai_service/models/whisper_large_v3",
          "fallback_model_id": "openchs/asr-whisper-helpline-sw-v1",
          "model_type": "speech-to-text",
          "framework": "transformers",
          "device": "cuda:0",
          "torch_dtype": "torch.float16",
          "is_loaded": true,
          "error": null,
          "supported_formats": [
            "wav",
            "mp3",
            "flac",
            "m4a",
            "ogg"
          ],
          "max_audio_length": "unlimited (chunked processing)",
          "sample_rate": "16kHz",
          "tasks_supported": "transcribe, translate",
          "languages": "multilingual (99+ languages)",
          "version": "large-v3",
          "current_model_id": "openchs/asr-whisper-helpline-sw-v1",
          "translation_enabled": true,
          "long_form_support": true,
          "supported_language_codes":[ "auto","en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi", "sw", "am", "lg", "rw", "so", "yo", "ig", "ha", "zu", "xh", "af", "ny"],
          
          "local_model_available": false
        }
      },
      "description": "Speech-to-text transcription"
    },
    "ner": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:16.536430",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "model_path": "./models/ner",
        "fallback_model_name": "en_core_web_lg",
        "hf_model_name": "spacy/en_core_web_lg",
        "hf_repo_id": "openchs/ner_distillbert_v1",
        "model_type": null,
        "loaded": true,
        "load_time": "2025-11-04T15:54:16.536326",
        "error": null,
        "transformers_available": true,
        "use_hf": true
      },
      "description": "Named Entity Recognition"
    },
    "classifier_model": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:19.204168",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "model_path": "./models/classifier",
        "loaded": true,
        "load_time": "2025-11-04T15:54:19.204055",
        "device": "cuda",
        "error": null,
        "max_length": 256,
        "chunking_supported": true,
        "aggregation_strategy": "weighted_voting",
        "priority_escalation": true,
        "num_categories": {
          "main": 7,
          "sub": 65,
          "intervention": 5,
          "priority": 3
        },
        "model_type": "MultiTaskDistilBert",
        "tokenizer": "DistilBertTokenizerFast"
      },
      "description": "Text classification"
    },
    "translator": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:21.201036",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "model_path": "./models/translation",
        "hf_repo_id": "openchs/sw-en-opus-mt-mul-en-v1",
        "device": "cuda",
        "loaded": true,
        "load_time": "2025-11-04T15:54:21.200934",
        "error": null,
        "max_length": 512,
        "chunking_supported": true,
        "fallback_strategies": [
          "chunked_translation",
          "memory_cleanup",
          "retry_logic"
        ]
      },
      "description": "Text translation"
    },
    "summarizer": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:22.953247",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "model_path": "./models/summarization",
        "device": "cuda",
        "loaded": true,
        "load_time": "2025-11-04T15:54:22.953182",
        "error": null,
        "task": "text-summarization",
        "framework": "transformers",
        "max_length": 512,
        "chunking_supported": true,
        "summarization_strategies": [
          "single_pass",
          "hierarchical"
        ],
        "fallback_strategy": "extractive_summary"
      },
      "description": "Text summarization"
    },
    "qa": {
      "loaded": true,
      "error": null,
      "load_time": "2025-11-04T15:54:25.265287",
      "dependencies_available": true,
      "missing_dependencies": [],
      "info": {
        "model_path": "/home/ai/ai_service/models/all_qa_distilbert_v1",
        "loaded": true,
        "load_time": "2025-11-04T15:54:25.265091",
        "device": "cuda",
        "error": null,
        "max_length": 512,
        "model_type": "MultiHeadQAClassifier",
        "qa_heads": [
          "opening",
          "listening",
          "proactiveness",
          "resolution",
          "hold",
          "closing"
        ]
      },
      "description": "QA scoring"
    }
  }
}
```

**Model States Explained:**

- **Ready Models**: Loaded and available for requests
- **Implementable Models**: Can be loaded (dependencies satisfied) but not yet initialized
- **Blocked Models**: Cannot load due to missing dependencies

**Use Cases:**
- Model loading troubleshooting
- Dependency resolution
- Service initialization monitoring
- Pre-request validation
- Automated testing

---

### 3.4. System Capabilities Check

**Endpoint:**
```
GET /health/capabilities
```

**Description:**  
Information about ML frameworks, hardware capabilities, and system configuration. Useful for verifying environment setup and compatibility.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/capabilities"
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T16:06:32.696717",
  "streaming_enabled": false,
  "resource_utilization": {
    "streaming": {
      "active_requests": 0,
      "max_slots": 2,
      "available_slots": 2,
      "utilization_pct": 0,
      "total_processed": 0,
      "avg_wait_time": 0
    },
    "batch": {
      "active_requests": 0,
      "max_slots": 1,
      "available_slots": 1,
      "utilization_pct": 0,
      "total_processed": 0,
      "avg_wait_time": 0
    },
    "active_request_ids": {
      "streaming": [],
      "batch": []
    }
  },
  "gpu_info": {
    "gpu_available": true,
    "gpu_count": 1,
    "current_device": 0,
    "device_name": "NVIDIA GeForce RTX 4060 Ti",
    "memory_allocated": 5187596288,
    "memory_reserved": 5846859776,
    "memory_available": 16720723968
  },
  "system_info": {
    "platform": "Linux-6.14.0-33-generic-x86_64-with-glibc2.39",
    "cpu_count": 32,
    "memory_total": 33401266176,
    "memory_available": 21723004928,
    "memory_percent": 35,
    "disk_usage": 97
  },
  "configuration": {
    "max_streaming_slots": 2,
    "max_batch_slots": 1,
    "streaming_port": 8300
  }
}

```

**Use Cases:**
- Environment verification
- Compatibility checking
- Bug reporting
- Performance benchmarking
- Deployment validation

---

### 3.5. Resource Utilization Check

**Endpoint:**
```
GET /health/resources
```

**Description:**  
Detailed resource utilization including CPU, memory, disk, GPU, and process-level metrics. Essential for performance monitoring and capacity planning.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/resources"
```

**Response (200):**
```json
{
  "timestamp": "2025-10-21T12:05:27.726046",
  "cpu": {
    "count": 16,
    "frequency_mhz": 3600.0,
    "percent_total": 42.5,
    "percent_per_core": [38.2, 45.1, 40.8, 44.2, 41.5, 43.9, 39.7, 46.3, 42.1, 40.5, 44.8, 41.2, 43.5, 39.8, 45.7, 42.9]
  },
  "memory": {
    "total_mb": 32768.0,
    "available_mb": 18432.5,
    "used_mb": 14335.5,
    "percent": 43.8,
    "swap_total_mb": 8192.0,
    "swap_used_mb": 256.3,
    "swap_percent": 3.1
  },
  "disk": {
    "total_gb": 512.0,
    "used_gb": 247.3,
    "free_gb": 264.7,
    "percent": 48.3
  },
  "gpu": {
    "available": true,
    "devices": [
      {
        "device_id": 0,
        "name": "NVIDIA GeForce RTX 3090",
        "memory_allocated_mb": 3247.52,
        "memory_reserved_mb": 3584.0,
        "memory_total_mb": 24576.0
      }
    ]
  },
  "process": {
    "pid": 12345,
    "cpu_percent": 15.2,
    "memory_mb": 4523.8,
    "threads": 24,
    "open_files": 48
  },
  "alerts": {
    "high_memory": false,
    "high_disk": false,
    "high_cpu": false
  }
}
```

**Alert Thresholds:**
- `high_memory`: Memory usage > 90% (configurable)
- `high_disk`: Disk usage > 90%
- `high_cpu`: Average CPU usage > 90%

**Use Cases:**
- Performance monitoring
- Resource capacity planning
- Alert triggering
- Bottleneck identification
- Cost optimization

---

### 3.6. Celery Worker Status

**Endpoint:**
```
GET /health/celery/status
```

**Description:**  
Status of Celery background task workers. Important for monitoring asynchronous task processing and queue health.

**Request:**
```bash
curl -X GET "http://192.168.8.18:8123/health/celery/status"
```

**Response (200) - Workers Active:**
```json
{
  "timestamp": "2025-11-04T16:04:59.820732",
  "overall_status": "healthy",
  "issues": [],
  "event_monitoring": {
    "is_monitoring": true,
    "thread_alive": true,
    "active_tasks_count": 0,
    "workers_seen": 0,
    "status": "connected"
  },
  "celery_workers": {
    "available": true,
    "count": 1,
    "worker_names": [
      "celery@bitz-B760M-DS3H"
    ],
    "error": null,
    "ping_response": {
      "celery@bitz-B760M-DS3H": {
        "ok": "pong"
      }
    },
    "worker_stats": {
      "celery@bitz-B760M-DS3H": {
        "total": {},
        "pid": 5208,
        "clock": "638",
        "uptime": 663,
        "pool": {
          "implementation": "celery.concurrency.solo:TaskPool",
          "max-concurrency": 1,
          "processes": [
            5208
          ],
          "max-tasks-per-child": null,
          "put-guarded-by-semaphore": true,
          "timeouts": []
        },
        "broker": {
          "hostname": "localhost",
          "userid": null,
          "virtual_host": "0",
          "port": 6379,
          "insist": false,
          "ssl": false,
          "transport": "redis",
          "connect_timeout": 4,
          "transport_options": {},
          "login_method": null,
          "uri_prefix": null,
          "heartbeat": 120,
          "failover_strategy": "round-robin",
          "alternates": []
        },
        "prefetch_count": 1,
        "rusage": {
          "utime": 29.537863,
          "stime": 5.938335,
          "maxrss": 8149260,
          "ixrss": 0,
          "idrss": 0,
          "isrss": 0,
          "minflt": 1153603,
          "majflt": 15722,
          "nswap": 0,
          "inblock": 17499216,
          "oublock": 24,
          "msgsnd": 0,
          "msgrcv": 0,
          "nsignals": 0,
          "nvcsw": 60045,
          "nivcsw": 666
        }
      }
    }
  },
  "recommendations": {
    "scaling": "Single worker detected - consider scaling for production",
    "next_step": "System ready for audio processing"
  },
  "system_health": {
    "workers_healthy": true,
    "monitoring_healthy": true,
    "redis_healthy": true,
    "ready_for_processing": true
  },
  "explanation": {
    "healthy": "All critical systems operational",
    "degraded": "Critical systems working, monitoring features limited",
    "critical": "Core functionality impaired - immediate attention needed"
  }
}
```

**Response (200) - No Workers:**
```json
{
  "status": "no_workers",
  "message": "No Celery workers are running",
  "timestamp": "2025-10-21T12:05:27.726046"
}
```

**Response (200) - Error State:**
```json
{
  "status": "error",
  "message": "Failed to check Celery status: connection refused",
  "timestamp": "2025-10-21T12:05:27.726046"
}
```

**Status Values:**
- `healthy`: Workers are active and processing tasks
- `no_workers`: No workers detected (tasks will queue)
- `unavailable`: Redis task client not initialized
- `error`: Connection or query error

**Use Cases:**
- Background task monitoring
- Queue processing verification
- Worker deployment validation
- Task completion troubleshooting
- Scaling decisions

---

## 4. Integration Examples


### 4.1. Load Balancer Health Check

**NGINX Configuration:**

```nginx
upstream ai_service {
    server 192.168.8.18:8123 max_fails=3 fail_timeout=30s;
    server 192.168.8.19:8123 max_fails=3 fail_timeout=30s backup;
}

server {
    listen 80;
    server_name ai-service.example.com;
    
    location /health/ {
        proxy_pass http://ai_service;
        proxy_connect_timeout 2s;
        proxy_read_timeout 2s;
        
        # Health check expects 200 response
        health_check interval=10s fails=3 passes=2;
    }
    
    location / {
        proxy_pass http://ai_service;
    }
}
```

### 4.2. Kubernetes Health Probes

**Deployment YAML:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-service
  template:
    metadata:
      labels:
        app: ai-service
    spec:
      containers:
      - name: ai-service
        image: openchs/ai-service:latest
        ports:
        - containerPort: 8123
        
        # Liveness probe - restart if failing
        livenessProbe:
          httpGet:
            path: /health/
            port: 8123
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - route traffic when ready
        readinessProbe:
          httpGet:
            path: /health/detailed
            port: 8123
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        
        # Startup probe - allow slow model loading
        startupProbe:
          httpGet:
            path: /health/models
            port: 8123
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30  # 5 minutes max startup time
        
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
```

---

## 5. Monitoring Best Practices

### Endpoint Usage Guidelines

**For Different Use Cases:**

| Use Case | Recommended Endpoint | Polling Interval |
|----------|---------------------|------------------|
| Load Balancer | `/health/` | 5-10 seconds |
| Basic Uptime | `/health/` | 30 seconds |
| Dashboard | `/health/detailed` | 30-60 seconds |
| Model Status | `/health/models` | 60 seconds |
| Resource Monitoring | `/health/resources` | 30-60 seconds |
| Capacity Planning | `/health/resources` | 5-15 minutes |
| Background Jobs | `/health/celery/status` | 60 seconds |
| Pre-deployment | `/health/capabilities` | On-demand |


---
## 6. Troubleshooting

### 6.1. Common Issues

**Models Not Ready:**

```bash
# Check which models are blocked
curl http://192.168.8.18:8123/health/models | jq '.blocked_models'

# Check dependency graph
curl http://192.168.8.18:8123/health/models | jq '.dependencies'

# Solution: Ensure dependencies are loaded first
# Example: translator must load before classifier
```

**High Memory Usage:**

```bash
# Check resource usage
curl http://192.168.8.18:8123/health/resources | jq '.memory'

# Check GPU memory if applicable
curl http://192.168.8.18:8123/health/resources | jq '.gpu.devices'

# Solution: Restart service or scale horizontally
```

**Celery Workers Not Running:**

```bash
# Check Celery status
curl http://192.168.8.18:8123/health/celery/status

# Solution: Start Celery workers
# celery -A app.celery_app worker --loglevel=info
```

**Redis Connection Failed:**

```bash
# Check Redis in detailed health
curl http://192.168.8.18:8123/health/detailed | jq '.redis'

# Solution: Verify Redis is running and accessible
# docker ps | grep redis
# redis-cli ping
```

### 6.2. Debug Mode

**Enable Debug Logging:**

```python
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Or in code
settings.debug = True
settings.log_level = "DEBUG"
```

**Debug Output:**

```bash
# Start service with debug output
uvicorn app.main:app --reload --log-level debug

# Watch health checks in real-time
watch -n 5 'curl -s http://192.168.8.18:8123/health/detailed | jq .'
```

---

## 7. API Response Codes

All health endpoints follow standard HTTP status codes:

| Code | Description | When It Occurs |
|------|-------------|----------------|
| 200 | OK | Health check successful, data returned |
| 500 | Internal Server Error | Unexpected error during health check |
| 503 | Service Unavailable | Critical component failure |

**Note:** Health endpoints return 200 even when status is "degraded" or "unhealthy". Check the response body `status` field for actual health state.

---

## 8. Security Considerations

### 8.1. Endpoint Access Control

Health endpoints expose system information that could be sensitive:

```python
# Recommended: Restrict health endpoints to internal network
# NGINX configuration
location /health/ {
    allow 10.0.0.0/8;     # Internal network
    allow 192.168.0.0/16;  # Internal network
    deny all;              # Block external access
    
    proxy_pass http://ai_service;
}
```

### 8.2. Information Disclosure

Detailed health endpoints expose:
- System resource utilization
- GPU device names and memory
- Model loading status
- Internal IP addresses
- Process IDs

---
