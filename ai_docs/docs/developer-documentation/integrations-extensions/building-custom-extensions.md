# Building Custom Extensions

## Overview

OpenCHS supports custom extensions to add new features, integrate with external services, or customize behavior without modifying the core codebase. This guide shows developers how to build extensions for both the Helpline service and AI service.

## Extension Types

### 1. PHP Plugins (Helpline Service)
Custom modules for case management, reporting, and workflows

### 2. AI Model Extensions (AI Service)
Additional AI models for specialized analysis

### 3. Frontend Widgets (User Interface)
Custom dashboard components and visualizations

### 4. API Middleware (Both Services)
Custom request/response processing

---

## PHP Plugin Extensions (Helpline Service)

### Plugin Structure

```
plugins/
└── custom-case-validator/
    ├── plugin.php          # Main plugin file
    ├── config.json         # Plugin configuration
    ├── hooks.php           # Event hooks
    ├── templates/          # HTML templates
    └── assets/            # CSS, JS files
```

### Basic Plugin Template

```php
<?php
/**
 * Plugin Name: Custom Case Validator
 * Description: Adds custom validation rules for cases
 * Version: 1.0.0
 * Author: Your Name
 */

class CustomCaseValidatorPlugin {
    private $config;
    
    public function __construct() {
        $this->config = $this->loadConfig();
        $this->registerHooks();
    }
    
    private function loadConfig() {
        $configPath = __DIR__ . '/config.json';
        return json_decode(file_get_contents($configPath), true);
    }
    
    private function registerHooks() {
        // Register hooks for plugin functionality
        add_hook('before_case_create', [$this, 'validateCase']);
        add_hook('after_case_create', [$this, 'notifyExternal']);
    }
    
    public function validateCase($caseData) {
        // Custom validation logic
        if (empty($caseData['reporter_phone']) && empty($caseData['reporter_email'])) {
            throw new ValidationException(
                'Either phone or email must be provided'
            );
        }
        
        // Custom business rules
        if ($caseData['priority'] === 'critical') {
            if (empty($caseData['description']) || strlen($caseData['description']) < 50) {
                throw new ValidationException(
                    'Critical cases require detailed description (min 50 characters)'
                );
            }
        }
        
        return $caseData;
    }
    
    public function notifyExternal($case) {
        // Send notification to external system
        if ($case['priority'] === 'critical') {
            $this->sendToExternalAPI($case);
        }
    }
    
    private function sendToExternalAPI($case) {
        $url = $this->config['external_api_url'];
        $apiKey = $this->config['external_api_key'];
        
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($case),
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                "Authorization: Bearer {$apiKey}"
            ],
            CURLOPT_RETURNTRANSFER => true
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return $response;
    }
}

// Initialize plugin
global $customCaseValidator;
$customCaseValidator = new CustomCaseValidatorPlugin();
?>
```

### Plugin Configuration (`config.json`)

```json
{
  "name": "Custom Case Validator",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Adds custom validation rules for cases",
  "requires": {
    "php": ">=8.2",
    "openchs": ">=1.0"
  },
  "settings": {
    "external_api_url": "https://external-system.com/api/cases",
    "external_api_key": "your-api-key",
    "enable_notifications": true
  },
  "hooks": [
    "before_case_create",
    "after_case_create",
    "before_case_update",
    "after_case_update"
  ]
}
```

### Available Hooks

```php
<?php
// Case hooks
add_hook('before_case_create', $callback);
add_hook('after_case_create', $callback);
add_hook('before_case_update', $callback);
add_hook('after_case_update', $callback);
add_hook('before_case_delete', $callback);
add_hook('case_status_changed', $callback);
add_hook('case_assigned', $callback);

// Communication hooks
add_hook('before_communication_create', $callback);
add_hook('after_communication_create', $callback);
add_hook('call_received', $callback);
add_hook('call_ended', $callback);

// AI processing hooks
add_hook('before_audio_process', $callback);
add_hook('after_audio_process', $callback);
add_hook('ai_prediction_complete', $callback);

// User hooks
add_hook('user_login', $callback);
add_hook('user_logout', $callback);

// System hooks
add_hook('daily_cleanup', $callback);
add_hook('report_generated', $callback);
?>
```

### Installing Plugins

```bash
# Copy plugin to plugins directory
cp -r custom-case-validator /var/www/html/helpline/plugins/

# Set permissions
chown -R nginx:nginx /var/www/html/helpline/plugins/custom-case-validator
chmod -R 755 /var/www/html/helpline/plugins/custom-case-validator

# Enable plugin in database
mysql -e "INSERT INTO helpline.plugin_registry (name, path, is_active) 
          VALUES ('custom-case-validator', 'plugins/custom-case-validator', TRUE);"

# Restart PHP-FPM
sudo systemctl restart php8.2-fpm
```

---

## AI Model Extensions (AI Service)

### Adding Custom AI Models

Structure for custom AI models:

```
ai_service/
└── app/
    └── models/
        └── custom/
            ├── __init__.py
            ├── sentiment_analyzer.py
            └── emotion_detector.py
```

### Custom Model Example

```python
# app/models/custom/sentiment_analyzer.py
from typing import Dict, List
import torch
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Custom sentiment analysis for child protection calls"""
    
    def __init__(self):
        self.model = None
        self.loaded = False
    
    def load(self) -> bool:
        """Load sentiment analysis model"""
        try:
            logger.info("Loading sentiment analysis model...")
            
            self.model = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.loaded = True
            logger.info("Sentiment analysis model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self.loaded = False
            return False
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Run sentiment analysis
            result = self.model(text)[0]
            
            # Convert to our format
            sentiment_score = self._convert_score(result['label'])
            
            return {
                "sentiment": result['label'],
                "score": sentiment_score,
                "confidence": result['score'],
                "urgency_level": self._assess_urgency(sentiment_score)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise
    
    def _convert_score(self, label: str) -> float:
        """Convert label to numeric score (-1 to 1)"""
        mapping = {
            "1 star": -1.0,
            "2 stars": -0.5,
            "3 stars": 0.0,
            "4 stars": 0.5,
            "5 stars": 1.0
        }
        return mapping.get(label, 0.0)
    
    def _assess_urgency(self, score: float) -> str:
        """Assess urgency based on sentiment"""
        if score <= -0.7:
            return "critical"
        elif score <= -0.3:
            return "high"
        elif score <= 0.3:
            return "medium"
        else:
            return "low"
    
    def get_model_info(self) -> Dict:
        """Return model metadata"""
        return {
            "name": "Sentiment Analyzer",
            "version": "1.0.0",
            "description": "Multilingual sentiment analysis for call transcripts",
            "loaded": self.loaded
        }

# Initialize model instance
sentiment_analyzer = SentimentAnalyzer()
```

### Register Custom Model

```python
# app/models/model_loader.py
from app.models.custom.sentiment_analyzer import sentiment_analyzer

class ModelLoader:
    def __init__(self):
        # Existing models
        self.whisper_model = WhisperModel()
        self.translation_model = TranslationModel()
        
        # Register custom models
        self.sentiment_analyzer = sentiment_analyzer
        
        self.model_dependencies = {
            # ... existing dependencies
            "sentiment_analyzer": {
                "required": ["torch", "transformers"],
                "description": "Sentiment analysis for call transcripts"
            }
        }
    
    def load_all_models(self):
        """Load all models including custom ones"""
        # Load standard models
        self.whisper_model.load()
        self.translation_model.load()
        
        # Load custom models
        self.sentiment_analyzer.load()
```

### Add API Endpoint for Custom Model

```python
# app/api/custom_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.model_loader import model_loader

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    score: float
    confidence: float
    urgency_level: str

@router.post("/sentiment/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of text
    
    - **text**: Text to analyze (call transcript)
    """
    try:
        result = model_loader.sentiment_analyzer.analyze(request.text)
        return SentimentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include in main app
# app/main.py
from app.api.custom_routes import router as custom_router
app.include_router(custom_router, prefix="/custom", tags=["Custom Models"])
```

### Testing Custom Model

```python
# tests/test_sentiment_analyzer.py
import pytest
from app.models.custom.sentiment_analyzer import sentiment_analyzer

@pytest.fixture(scope="module")
def loaded_model():
    sentiment_analyzer.load()
    yield sentiment_analyzer

def test_sentiment_analysis_negative(loaded_model):
    """Test negative sentiment detection"""
    text = "I am very worried about this child, situation is terrible"
    result = loaded_model.analyze(text)
    
    assert result['score'] < 0
    assert result['urgency_level'] in ['high', 'critical']

def test_sentiment_analysis_positive(loaded_model):
    """Test positive sentiment detection"""
    text = "The child is safe now, family is receiving good support"
    result = loaded_model.analyze(text)
    
    assert result['score'] > 0
    assert result['urgency_level'] == 'low'

def test_sentiment_analysis_multilingual(loaded_model):
    """Test with Swahili text"""
    text = "Mtoto ana hali mbaya sana, anahitaji msaada haraka"
    result = loaded_model.analyze(text)
    
    assert 'sentiment' in result
    assert 'confidence' in result
```

---

## Frontend Widget Extensions

### Custom Dashboard Widget

```javascript
// frontend/src/widgets/CaseStatisticsWidget.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const CaseStatisticsWidget = () => {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    fetchStatistics();
  }, []);
  
  const fetchStatistics = async () => {
    try {
      const response = await fetch('/helpline/api/cases/statistics');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };
  
  if (!stats) return <div>Loading...</div>;
  
  const chartData = [
    { category: 'Abuse', count: stats.abuse_cases },
    { category: 'Neglect', count: stats.neglect_cases },
    { category: 'Education', count: stats.education_cases },
    { category: 'Health', count: stats.health_cases }
  ];
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Case Statistics (Last 30 Days)</Typography>
        <BarChart width={400} height={300} data={chartData}>
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </CardContent>
    </Card>
  );
};

export default CaseStatisticsWidget;
```

### Register Widget

```javascript
// frontend/src/dashboard/WidgetRegistry.js
import CaseStatisticsWidget from '../widgets/CaseStatisticsWidget';
import CustomAlertWidget from '../widgets/CustomAlertWidget';

export const widgetRegistry = {
  'case-statistics': {
    component: CaseStatisticsWidget,
    title: 'Case Statistics',
    defaultSize: { width: 6, height: 4 }
  },
  'custom-alerts': {
    component: CustomAlertWidget,
    title: 'Custom Alerts',
    defaultSize: { width: 4, height: 3 }
  }
};

// Usage in dashboard
// frontend/src/pages/Dashboard.jsx
import { widgetRegistry } from './WidgetRegistry';

const Dashboard = () => {
  const userWidgets = ['case-statistics', 'custom-alerts'];
  
  return (
    <Grid container spacing={2}>
      {userWidgets.map(widgetId => {
        const Widget = widgetRegistry[widgetId].component;
        return (
          <Grid item xs={12} md={6} key={widgetId}>
            <Widget />
          </Grid>
        );
      })}
    </Grid>
  );
};
```

---

## API Middleware Extensions

### Custom Request Middleware

```python
# ai_service/app/middleware/custom_auth.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class CustomAuthMiddleware(BaseHTTPMiddleware):
    """Custom authentication middleware for special integrations"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health endpoints
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Check for custom API key header
        api_key = request.headers.get("X-Custom-API-Key")
        
        if api_key:
            # Validate custom API key
            if self.validate_custom_key(api_key):
                # Add custom user info to request state
                request.state.auth_source = "custom"
                request.state.api_key_id = self.get_key_id(api_key)
                
                # Log usage
                logger.info(f"Custom API key used: {request.state.api_key_id}")
                
                return await call_next(request)
        
        # Fall through to default authentication
        return await call_next(request)
    
    def validate_custom_key(self, api_key: str) -> bool:
        """Validate custom API key against database"""
        # Implementation here
        return True
    
    def get_key_id(self, api_key: str) -> str:
        """Get key identifier for logging"""
        return api_key[:8] + "..."

# Register middleware
# app/main.py
from app.middleware.custom_auth import CustomAuthMiddleware
app.add_middleware(CustomAuthMiddleware)
```

### Response Transformation Middleware

```php
<?php
// helpline/middleware/ResponseTransformer.php

class ResponseTransformerMiddleware {
    public function handle($request, $next) {
        $response = $next($request);
        
        // Add custom headers
        $response->headers->set('X-OpenCHS-Version', '1.0.0');
        $response->headers->set('X-Request-ID', $request->id());
        
        // Transform response for legacy clients
        if ($request->header('X-Legacy-Client') === 'true') {
            $content = json_decode($response->getContent(), true);
            $transformed = $this->transformForLegacy($content);
            $response->setContent(json_encode($transformed));
        }
        
        return $response;
    }
    
    private function transformForLegacy($data) {
        // Transform new format to legacy format
        return [
            'status' => $data['success'] ? 'ok' : 'error',
            'result' => $data['data'],
            'timestamp' => time()
        ];
    }
}
?>
```

---

## Extension Best Practices

### 1. Version Compatibility

```json
// config.json
{
  "requires": {
    "openchs": ">=1.0.0 <2.0.0",
    "php": ">=8.2",
    "python": ">=3.11"
  },
  "compatibility": {
    "tested_with": ["1.0.0", "1.1.0", "1.2.0"]
  }
}
```

### 2. Error Handling

```python
class CustomExtension:
    def process(self, data):
        try:
            # Extension logic
            result = self.custom_processing(data)
            return {"success": True, "data": result}
            
        except ValueError as e:
            # Validation errors
            logger.warning(f"Validation error: {e}")
            return {"success": False, "error": str(e)}
            
        except Exception as e:
            # Unexpected errors - don't break main flow
            logger.error(f"Extension error: {e}", exc_info=True)
            return {"success": False, "error": "Extension processing failed"}
```

### 3. Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor extension performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log slow operations
            if duration > 1.0:
                logger.warning(
                    f"{func.__name__} took {duration:.2f}s (threshold: 1.0s)"
                )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {duration:.2f}s: {e}"
            )
            raise
    
    return wrapper

class MyExtension:
    @monitor_performance
    def expensive_operation(self, data):
        # Extension logic
        pass
```

### 4. Configuration Management

```python
import os
from typing import Dict

class ExtensionConfig:
    """Centralized configuration for extensions"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.validate_config()
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file and environment"""
        with open(config_file) as f:
            config = json.load(f)
        
        # Override with environment variables
        for key in config.get('env_vars', []):
            env_value = os.getenv(key)
            if env_value:
                config[key] = env_value
        
        return config
    
    def validate_config(self):
        """Validate required configuration"""
        required = self.config.get('required_settings', [])
        
        for setting in required:
            if setting not in self.config:
                raise ValueError(f"Required setting missing: {setting}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
```

---

## Testing Extensions

### Unit Tests

```python
# tests/test_custom_extension.py
import pytest
from app.extensions.custom import CustomExtension

@pytest.fixture
def extension():
    return CustomExtension()

def test_extension_initialization(extension):
    """Test extension initializes correctly"""
    assert extension is not None
    assert extension.loaded == True

def test_extension_processing(extension):
    """Test extension processes data correctly"""
    input_data = {"text": "test input"}
    result = extension.process(input_data)
    
    assert result['success'] == True
    assert 'data' in result

def test_extension_error_handling(extension):
    """Test extension handles errors gracefully"""
    invalid_data = None
    result = extension.process(invalid_data)
    
    assert result['success'] == False
    assert 'error' in result
```

### Integration Tests

```python
# tests/test_extension_integration.py
def test_extension_with_api(test_client):
    """Test extension works with API endpoints"""
    response = test_client.post(
        "/custom/analyze",
        json={"text": "test input"}
    )
    
    assert response.status_code == 200
    assert 'sentiment' in response.json()
```

---

## Publishing Extensions

### Extension Metadata

```json
{
  "name": "custom-extension",
  "version": "1.0.0",
  "description": "Custom extension for OpenCHS",
  "author": "Your Name",
  "license": "MIT",
  "homepage": "https://github.com/yourname/custom-extension",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourname/custom-extension.git"
  },
  "keywords": ["openchs", "extension", "custom"],
  "requires": {
    "openchs": ">=1.0.0"
  }
}
```

### Documentation Requirements

- README with installation instructions
- Configuration examples
- API documentation
- Usage examples
- Troubleshooting guide

### Submission Process

1. Test extension thoroughly
2. Document all features
3. Submit to extension registry
4. Respond to review feedback
5. Maintain and update

For more information on extension development, see the [API Reference](../api-reference/overview.md) and [Integration Guide](integrating-with-external-systems.md).