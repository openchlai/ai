# Progressive Processing Strategy for Real-Time Call Analysis

## Overview
This document outlines the progressive processing approach for handling substantial transcripts during live calls, including context-aware translation, evolving NER/classification, and end-of-call summarization.

## 🎯 **Processing Strategy**

### **Translation: Context-Aware Sliding Windows**
- **Window Size**: 30-60 seconds of transcript (~150-300 words)
- **Overlap**: 50 characters for context preservation  
- **Trigger**: Every 30 seconds OR when 150+ new characters accumulated
- **Output**: Both windowed translations + cumulative merged translation

### **NER/Classification: Progressive Updates**
- **Frequency**: After each translation window
- **Evolution Tracking**: Monitor how entities/predictions change over time
- **Confidence Building**: Higher accuracy as more context becomes available

### **Summarization: End-of-Call Only**
- **Trigger**: When call ends with substantial content (>100 words)
- **Input**: Full cumulative translation for maximum context
- **Output**: Comprehensive call summary with all available context

## 🏗️ **Architecture Components**

### 1. ProgressiveProcessor (`progressive_processor.py`)
**Core Logic:**
- **Window Management**: Creates overlapping processing windows
- **Smart Translation Merging**: Handles context preservation between windows
- **Evolution Tracking**: Monitors entity and classification changes
- **Memory Management**: Efficient processing with cleanup

**Key Methods:**
```python
process_if_ready(call_id, transcript) → Optional[ProcessingWindow]
finalize_call_analysis(call_id) → Dict[final_analysis]
```

### 2. CallSessionManager Integration
**Enhanced Features:**
- Triggers progressive processing on transcript updates
- Manages both transcript and progressive analysis lifecycle
- Coordinates end-of-call summarization

### 3. New API Endpoints
**Progressive Analysis Endpoints:**
- `GET /api/v1/calls/{call_id}/progressive-analysis` - Full analysis data
- `GET /api/v1/calls/{call_id}/translation` - Cumulative translation
- `GET /api/v1/calls/{call_id}/entity-evolution` - Entity changes over time
- `GET /api/v1/calls/{call_id}/classification-evolution` - Classification changes

## 📊 **Processing Flow**

### During Call (Real-time)
```
Transcript Segment → Cumulative Transcript → Check Window Threshold → 
Create Processing Window → Translation → NER → Classification → 
Store Results → Update Evolution Tracking
```

### End of Call
```
Call Ends → Finalize Progressive Analysis → Generate Summary → 
Trigger Full AI Pipeline → Store Final Results → Cleanup
```

## 🧠 **Smart Translation Strategy**

### Window Creation Logic
```python
# First window: Start from beginning
start_pos = 0
end_pos = min(len(transcript), 300)  # Target window size

# Subsequent windows: Overlap for context
start_pos = last_window.end_position - 50  # 50 char overlap
end_pos = len(transcript)
```

### Translation Merging Algorithm
```python
def _merge_translation(existing, new_translation, has_overlap):
    if has_overlap:
        # Find word-level overlap between translations
        # Remove duplicate words from new translation
        # Merge intelligently
    else:
        # Simple concatenation with separator
```

**Benefits:**
- **Context Preservation**: 50-character overlap maintains translation context
- **Quality Translation**: Sufficient context (150-300 words) for accurate translation
- **Efficiency**: Only process new content, not entire transcript each time

## 📈 **Evolution Tracking**

### Entity Evolution
Tracks how named entities are discovered and change:
```json
{
  "window_id": 3,
  "timestamp": "2025-08-01T12:45:30",
  "entities": {
    "PERSON": ["John Smith", "Mary Johnson"],
    "ORG": ["ABC Hospital"],
    "DATE": ["today", "next week"]
  },
  "entity_count": 5
}
```

### Classification Evolution  
Monitors how call classification changes with more context:
```json
{
  "window_id": 3,
  "main_category": "medical_emergency",
  "confidence": 0.89,
  "priority": "high"
}
```

**Use Cases:**
- **Early Warning**: Detect urgent situations before call ends
- **Context Building**: See how understanding improves with more information
- **Quality Assurance**: Track classification confidence over time

## ⚙️ **Configuration Parameters**

### Processing Thresholds
```python
min_window_chars = 150        # Minimum chars to trigger processing
target_window_chars = 300     # Target window size
overlap_chars = 50           # Overlap between windows
processing_interval = 30s    # Minimum time between processing
```

### Translation Quality Settings
```python
context_preservation = True   # Enable smart overlap handling
merge_algorithm = "word_overlap"  # Translation merging strategy
quality_threshold = 0.8      # Minimum confidence for translations
```

## 🔄 **Processing Workflow**

### Example Call Processing Timeline

**00:30** - First window (150 chars)
- Translation: "Caller reporting chest pain..."
- Entities: {"PERSON": ["caller"], "CONDITION": ["chest pain"]}
- Classification: {"category": "medical", "confidence": 0.65}

**01:00** - Second window (300 chars with overlap)
- Translation: "...chest pain started 2 hours ago, severe..."
- Entities: {"PERSON": ["caller"], "CONDITION": ["chest pain"], "TIME": ["2 hours ago"]}
- Classification: {"category": "medical_emergency", "confidence": 0.78}

**01:30** - Third window
- Translation: "...severe pain, requesting ambulance immediately..."
- Entities: {"PERSON": ["caller"], "CONDITION": ["chest pain"], "TIME": ["2 hours ago"], "REQUEST": ["ambulance"]}
- Classification: {"category": "medical_emergency", "priority": "critical", "confidence": 0.92}

**Call End** - Final summarization
- Summary: "Emergency call regarding severe chest pain lasting 2 hours, ambulance requested"
- Final analysis stored with complete evolution history

## 🚀 **API Usage Examples**

### Monitor Real-time Translation
```bash
# Get current translation as call progresses
curl http://localhost:8123/api/v1/calls/1754051771.12/translation
```

### Track Entity Discovery
```bash
# See how entities are discovered over time
curl http://localhost:8123/api/v1/calls/1754051771.12/entity-evolution
```

### Monitor Classification Changes
```bash
# Watch how call classification evolves
curl http://localhost:8123/api/v1/calls/1754051771.12/classification-evolution
```

### Get Complete Analysis
```bash
# Full progressive analysis with all windows
curl http://localhost:8123/api/v1/calls/1754051771.12/progressive-analysis
```

## 🎯 **Benefits of This Approach**

### 1. **Real-time Insights**
- Get translation, entities, and classification as call progresses
- Early detection of urgent situations
- Progressive understanding building

### 2. **Context Preservation**
- Smart overlapping windows maintain translation quality
- No loss of context between processing windows
- Cumulative translation improves over time

### 3. **Efficient Processing** 
- Only process new content, not entire transcript
- Configurable thresholds prevent over-processing
- Memory-efficient with cleanup

### 4. **Quality Improvement**
- Longer windows (150-300 words) provide better translation context
- Evolution tracking shows confidence building
- End-of-call summary uses complete context

### 5. **Scalability**
- Independent processing per call
- Redis storage for persistence
- Async processing doesn't block transcription

## 🔧 **Monitoring and Debugging**

### Log Examples
```
🧠 [session] Progressive processing completed window 3 for call 1754051771.12
🌐 Translating window 3 for call 1754051771.12  
🏷️ Extracting entities from window 3 for call 1754051771.12
📊 Classifying window 3 for call 1754051771.12
📋 Finalized analysis for call 1754051771.12: 5 windows, 1247 chars translated
📝 Generated summary for call 1754051771.12: 156 chars
```

### Performance Metrics
- **Processing Time**: Average time per window (~2-5 seconds)
- **Window Count**: Number of processing windows per call
- **Translation Quality**: Context preservation effectiveness
- **Evolution Accuracy**: How classification confidence improves

## 🔮 **Future Enhancements**

### Planned Features
- **Dynamic Window Sizing**: Adjust window size based on content complexity
- **Multi-language Detection**: Handle code-switching within calls
- **Streaming WebSocket Updates**: Real-time progressive results
- **Custom Processing Rules**: Different strategies per call type
- **Quality Scoring**: Automatic assessment of translation/analysis quality

### Integration Possibilities
- **Real-time Dashboards**: Live view of call analysis progression
- **Alert Systems**: Immediate notifications for critical classifications
- **Call Routing**: Dynamic routing based on progressive analysis
- **Agent Assistance**: Real-time information for call center agents