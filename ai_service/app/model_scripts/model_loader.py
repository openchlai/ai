import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Optional ML library imports - gracefully handle if not available
AVAILABLE_LIBRARIES = {}

try:
    import torch
    AVAILABLE_LIBRARIES['torch'] = torch.__version__
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.info("PyTorch not available - GPU models disabled")

try:
    import transformers
    AVAILABLE_LIBRARIES['transformers'] = transformers.__version__
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.info("Transformers not available - transformer models disabled")

try:
    import spacy
    AVAILABLE_LIBRARIES['spacy'] = spacy.__version__
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.info("spaCy not available - NER models disabled")

try:
    import librosa
    AVAILABLE_LIBRARIES['librosa'] = librosa.__version__
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.info("Librosa not available - audio processing disabled")

try:
    import soundfile
    AVAILABLE_LIBRARIES['soundfile'] = soundfile.__version__
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.info("SoundFile not available - audio I/O disabled")

try:
    import sklearn
    AVAILABLE_LIBRARIES['sklearn'] = sklearn.__version__
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.info("Scikit-learn not available - some classification features disabled")

try:
    import numpy
    AVAILABLE_LIBRARIES['numpy'] = numpy.__version__
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.info("NumPy not available - numerical processing disabled")


class ModelStatus:
    def __init__(self, name: str):
        self.name = name
        self.loaded = False
        self.error = None
        self.load_time = None
        self.model_info = {}
        self.dependencies_available = False
        self.missing_dependencies = []


class ModelLoader:
    """Manages loading and status of all models with optional dependencies"""
    
    def __init__(self, models_path: str = None):
        # Import settings here to avoid circular imports
        from ..config.settings import settings
        
        settings.initialize_paths()
        
        self.models_path = models_path or settings.models_path
        self.models: Dict[str, Any] = {}
        self.model_status: Dict[str, ModelStatus] = {}
        
        # Model dependency requirements
        self.model_dependencies = {
            "whisper": {
                "required": ["torch", "transformers", "librosa", "soundfile", "numpy"],
                "description": "Speech-to-text transcription"
            },
            "ner": {
                "required": ["spacy", "numpy"],
                "description": "Named Entity Recognition"
            },
            "classifier_model": {
                "required": ["torch", "transformers", "sklearn", "numpy"],
                "description": "Text classification"
            },
            "translator": {
                "required": ["torch", "transformers", "numpy"],
                "description": "Text translation"
            },
            "summarizer": {
                "required": ["torch", "transformers", "numpy"],
                "description": "Text summarization"
            }
        }
        
        # Initialize model status for all expected models
        for model_name in self.model_dependencies.keys():
            self.model_status[model_name] = ModelStatus(model_name)
            self._check_model_dependencies(model_name)
        
        logger.info(f"ModelLoader initialized with models_path={self.models_path}")
        logger.info(f"Available libraries: {list(AVAILABLE_LIBRARIES.keys())}")
    
    def _check_model_dependencies(self, model_name: str):
        """Check if model dependencies are available"""
        if model_name not in self.model_dependencies:
            return
        
        required_deps = self.model_dependencies[model_name]["required"]
        missing_deps = []
        
        # Map library names to availability flags
        lib_availability = {
            "torch": TORCH_AVAILABLE,
            "transformers": TRANSFORMERS_AVAILABLE,
            "spacy": SPACY_AVAILABLE,
            "librosa": LIBROSA_AVAILABLE,
            "soundfile": SOUNDFILE_AVAILABLE,
            "sklearn": SKLEARN_AVAILABLE,
            "numpy": NUMPY_AVAILABLE
        }
        
        for dep in required_deps:
            if not lib_availability.get(dep, False):
                missing_deps.append(dep)
        
        model_status = self.model_status[model_name]
        model_status.dependencies_available = len(missing_deps) == 0
        model_status.missing_dependencies = missing_deps
        
        if missing_deps:
            model_status.error = f"Missing dependencies: {', '.join(missing_deps)}"
            logger.info(f"Model {model_name} cannot load - missing: {missing_deps}")
        else:
            logger.info(f"Model {model_name} dependencies satisfied")
    
    async def load_all_models(self):
        """Load all models that have satisfied dependencies"""
        logger.info("Starting model loading process...")
        
        for model_name in self.model_status.keys():
            await self._load_model(model_name)
    
    async def _load_model(self, model_name: str):
        """Load a specific model if dependencies are available"""
        logger.info(f"Checking {model_name} model...")
        
        model_status = self.model_status[model_name]
        
        try:
            # Check if dependencies are available
            if not model_status.dependencies_available:
                logger.info(f"Skipping {model_name} - dependencies not available: {model_status.missing_dependencies}")
                return
            
            if model_name == "whisper":
                # Use WhisperModelManager for dynamic variant loading
                from ..core.whisper_model_manager import whisper_model_manager
                
                try:
                    success = await whisper_model_manager.load_whisper_model()
                    if success:
                        model_status.loaded = True
                        model_status.error = None
                        model_status.model_info = whisper_model_manager.get_loaded_variant_info()
                        # Store the actual whisper model instance for backward compatibility
                        self.models[model_name] = whisper_model_manager.whisper_model
                        logger.info(f"✅ Whisper model loaded successfully: {whisper_model_manager.current_variant.value}")
                    else:
                        model_status.error = "Failed to load Whisper model via WhisperModelManager"
                        logger.error(f"❌ Whisper model failed to load: {model_status.error}")
                except Exception as e:
                    model_status.error = f"WhisperModelManager error: {str(e)}"
                    logger.error(f"❌ Whisper model manager failed: {model_status.error}")
                
                model_status.load_time = datetime.now()
                return
            
            if model_name == "ner":
                from .ner_model import ner_model
                
                success = ner_model.load()
                if success:
                    model_status.loaded = True
                    model_status.error = None
                    model_status.model_info = ner_model.get_model_info()
                    self.models[model_name] = ner_model
                    logger.info(f"✅ NER model loaded successfully")
                else:
                    model_status.error = ner_model.error or "Failed to load NER model"
                    logger.error(f"❌ NER model failed to load: {model_status.error}")
                
                model_status.load_time = datetime.now()
                return
            
            elif model_name == "classifier_model":
                from .classifier_model import classifier_model
                success = classifier_model.load()
                if success:
                    model_status.loaded = True
                    model_status.error = None
                    model_status.model_info = classifier_model.get_model_info()
                    self.models[model_name] = classifier_model
                    logger.info(f"✅ {model_name} model loaded successfully")
                else:
                    model_status.error = classifier_model.error or "Failed to load classifier model"
                    logger.error(f"❌ {model_name} model failed to load: {model_status.error}")
                model_status.load_time = datetime.now()
                return
            
            if model_name == "translator":
                from .translator_model import translator_model

                success = translator_model.load()
                if success:
                    model_status.loaded = True
                    model_status.error = None
                    model_status.model_info = translator_model.get_model_info()
                    self.models[model_name] = translator_model
                    logger.info("✅ Translation model loaded successfully")
                else:
                    model_status.error = translator_model.error or "Failed to load translation model"
                    logger.error(f"❌ Translation model failed to load: {model_status.error}")

                model_status.load_time = datetime.now()
                return
            
            if model_name == "summarizer":
                from .summarizer_model import summarization_model

                success = summarization_model.load()
                if success:
                    model_status.loaded = True
                    model_status.error = None
                    model_status.model_info = summarization_model.get_model_info()
                    self.models[model_name] = summarization_model
                    logger.info("✅ Summarization model loaded successfully")
                else:
                    model_status.error = summarization_model.error or "Failed to load summarization model"
                    logger.error(f"❌ Summarization model failed to load: {model_status.error}")

                model_status.load_time = datetime.now()
                return
            
            # If we get here, the model isn't implemented yet
            model_status.error = f"Model loading implementation pending (dependencies available)"
            model_status.load_time = datetime.now()
            model_status.model_info = {
                "model_path": os.path.join(self.models_path, model_name),
                "dependencies_satisfied": True,
                "description": self.model_dependencies[model_name]["description"]
            }
            
            logger.info(f"Model {model_name} ready for implementation (dependencies satisfied)")
            
        except Exception as e:
            logger.error(f"Failed to prepare {model_name} model: {e}")
            model_status.error = str(e)
            model_status.load_time = datetime.now()
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        status = {}
        
        for model_name, model_status in self.model_status.items():
            status[model_name] = {
                "loaded": model_status.loaded,
                "error": model_status.error,
                "load_time": model_status.load_time.isoformat() if model_status.load_time else None,
                "dependencies_available": model_status.dependencies_available,
                "missing_dependencies": model_status.missing_dependencies,
                "info": model_status.model_info,
                "description": self.model_dependencies.get(model_name, {}).get("description", "Unknown model")
            }
        
        return status
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get overall system ML capabilities"""
        total_models = len(self.model_status)
        ready_for_implementation = len([m for m in self.model_status.values() if m.dependencies_available])
        missing_deps = len([m for m in self.model_status.values() if not m.dependencies_available])
        loaded_models = len([m for m in self.model_status.values() if m.loaded])
        
        return {
            "available_libraries": AVAILABLE_LIBRARIES,
            "models_path": self.models_path,
            "total_models": total_models,
            "loaded_models": loaded_models,
            "ready_for_implementation": ready_for_implementation,
            "missing_dependencies": missing_deps,
            "ml_capabilities": {
                "gpu_processing": TORCH_AVAILABLE and (torch.cuda.is_available() if TORCH_AVAILABLE else False),
                "transformer_models": TRANSFORMERS_AVAILABLE,
                "audio_processing": LIBROSA_AVAILABLE and SOUNDFILE_AVAILABLE,
                "nlp_processing": SPACY_AVAILABLE,
                "classical_ml": SKLEARN_AVAILABLE,
                "numerical_computing": NUMPY_AVAILABLE
            }
        }
    
    def is_model_ready(self, model_name: str) -> bool:
        """Check if a specific model is ready"""
        return (model_name in self.model_status and 
                self.model_status[model_name].loaded and 
                self.model_status[model_name].error is None)
    
    def can_implement_model(self, model_name: str) -> bool:
        """Check if a model can be implemented (dependencies available)"""
        return (model_name in self.model_status and 
                self.model_status[model_name].dependencies_available)
    
    def get_ready_models(self) -> List[str]:
        """Get list of ready models"""
        return [name for name, status in self.model_status.items() 
                if status.loaded and status.error is None]
    
    def get_implementable_models(self) -> List[str]:
        """Get list of models that can be implemented (have dependencies)"""
        return [name for name, status in self.model_status.items() 
                if status.dependencies_available]
    
    def get_blocked_models(self) -> List[str]:
        """Get list of models blocked by missing dependencies"""
        return [name for name, status in self.model_status.items() 
                if not status.dependencies_available]
    
    def get_missing_dependencies_summary(self) -> Dict[str, List[str]]:
        """Get summary of missing dependencies per model"""
        return {name: status.missing_dependencies 
                for name, status in self.model_status.items() 
                if not status.dependencies_available}

    def get_failed_models(self) -> List[str]:
        """Get list of failed models"""
        return [name for name, status in self.model_status.items() 
                if status.error is not None and status.dependencies_available]

# Global model loader instance
model_loader = ModelLoader()