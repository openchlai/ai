from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.http import StreamingHttpResponse
from .models import AudioFile
from .serializers import AudioFileSerializer
from .pipeline import transcription, translation, ner, classifier, summarizer
from .utils import highlighter
from .pipeline.insights import generate_case_insights
import json
import logging
import traceback
import gc
import torch
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def detailed_gpu_memory_report():
    """Get detailed GPU memory information."""
    if not torch.cuda.is_available():
        return "CUDA not available"
    
    allocated = torch.cuda.memory_allocated()
    cached = torch.cuda.memory_reserved()
    
    return {
        "allocated_mb": allocated / 1024**2,
        "cached_mb": cached / 1024**2,
        "allocated_gb": allocated / 1024**3,
        "cached_gb": cached / 1024**3
    }

def find_gpu_tensors():
    """Find tensors currently on GPU."""
    if not torch.cuda.is_available():
        return []
    
    gpu_tensors = []
    for obj in gc.get_objects():
        try:
            if torch.is_tensor(obj) and obj.is_cuda:
                size_mb = obj.element_size() * obj.nelement() / 1024**2
                gpu_tensors.append({
                    'shape': tuple(obj.shape),
                    'dtype': obj.dtype,
                    'size_mb': size_mb,
                    'device': obj.device
                })
        except:
            pass
    
    # Sort by size
    gpu_tensors.sort(key=lambda x: x['size_mb'], reverse=True)
    return gpu_tensors

@contextmanager
def memory_tracker(step_name):
    """Context manager to track memory usage for a specific step."""
    logger.info(f"--- MEMORY TRACKER: {step_name} ---")
    
    # Before
    before = detailed_gpu_memory_report()
    if isinstance(before, dict):
        logger.info(f"BEFORE {step_name}: Allocated: {before['allocated_mb']:.1f} MB, Cached: {before['cached_mb']:.1f} MB")
    
    try:
        yield
    finally:
        # After
        after = detailed_gpu_memory_report()
        if isinstance(after, dict):
            delta_allocated = after['allocated_mb'] - before['allocated_mb'] if isinstance(before, dict) else 0
            delta_cached = after['cached_mb'] - before['cached_mb'] if isinstance(before, dict) else 0
            logger.info(f"AFTER {step_name}: Allocated: {after['allocated_mb']:.1f} MB (+{delta_allocated:.1f}), Cached: {after['cached_mb']:.1f} MB (+{delta_cached:.1f})")
            
            # Show top GPU tensors if memory is significant
            if after['allocated_mb'] > 100:
                tensors = find_gpu_tensors()
                if tensors:
                    logger.info(f"TOP GPU TENSORS after {step_name}:")
                    for i, tensor in enumerate(tensors[:3]):  # Top 3
                        logger.info(f"  {i+1}. Shape: {tensor['shape']}, Size: {tensor['size_mb']:.1f} MB")

def cleanup_resources():
    """Cleanup GPU and system resources."""
    try:
        # GPU cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # Force garbage collection
        gc.collect()
        
        # Force cleanup of individual modules if available
        modules_to_cleanup = [transcription, translation, ner, classifier, summarizer]
        for module in modules_to_cleanup:
            if hasattr(module, 'force_cleanup'):
                try:
                    module.force_cleanup()
                    logger.info(f"Cleaned up {module.__name__}")
                except Exception as e:
                    logger.warning(f"Error cleaning up {module.__name__}: {str(e)}")
        
        logger.info("Resources cleaned up successfully")
    except Exception as e:
        logger.warning(f"Error during resource cleanup: {str(e)}")

def emergency_gpu_cleanup():
    """Force cleanup of everything on GPU."""
    logger.info("EMERGENCY GPU CLEANUP...")
    
    # Clear Python cache
    gc.collect()
    
    # Clear CUDA cache
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        
        # Reset peak memory stats
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.reset_max_memory_allocated()
        torch.cuda.reset_max_memory_cached()
    
    logger.info("Emergency cleanup completed")

class AudioUploadView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        serializer = AudioFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_instance = serializer.save()

        def process_and_stream():
            response_data = {"id": audio_instance.id}
            
            try:
                # Log initial GPU memory state
                initial_report = detailed_gpu_memory_report()
                if isinstance(initial_report, dict):
                    logger.info(f"Initial GPU memory: {initial_report['allocated_mb']:.1f} MB allocated, {initial_report['cached_mb']:.1f} MB cached")

                # Step 1: Transcribe with memory tracking
                with memory_tracker("TRANSCRIPTION"):
                    logger.info(f"Transcribing audio: {audio_instance.audio.path}")
                    transcript = transcription.transcribe(
                        audio_instance.audio.path,
                        cleanup_after=True  # Ensure cleanup after transcription
                    )
                    audio_instance.transcript = transcript
                    response_data["transcript"] = transcript
                    yield json.dumps({"step": "transcription", "data": response_data}) + "\n"
                
                # Force cleanup after transcription (most memory intensive step)
                cleanup_resources()

                # Step 2: Translate with memory tracking
                with memory_tracker("TRANSLATION"):
                    logger.info("Translating transcript")
                    translated_transcript = translation.translate(transcript)
                    response_data["translated_transcript"] = translated_transcript
                    yield json.dumps({"step": "translation", "data": response_data}) + "\n"

                # Cleanup after translation
                cleanup_resources()

                # Step 3: Summarize with memory tracking
                with memory_tracker("SUMMARIZATION"):
                    logger.info("Summarizing translated transcript")
                    summary = summarizer.summarize(translated_transcript)
                    response_data["summary"] = summary
                    yield json.dumps({"step": "summarization", "data": response_data}) + "\n"

                # Cleanup after summarization
                cleanup_resources()

                # Step 4: NER with memory tracking
                with memory_tracker("NER"):
                    logger.info("Extracting named entities from summary")
                    summary_entities = ner.extract_entities(summary, flat=True)
                    response_data["summary_entities"] = summary_entities
                    yield json.dumps({"step": "ner", "data": response_data}) + "\n"

                # Cleanup after NER
                cleanup_resources()

                # Step 5: Classification with memory tracking
                with memory_tracker("CLASSIFICATION"):
                    logger.info("Classifying summarized case")
                    summary_classification = classifier.classify_case(summary)
                    response_data["summary_classification"] = summary_classification
                    yield json.dumps({"step": "classification", "data": response_data}) + "\n"

                # Cleanup after classification
                cleanup_resources()

                # Step 6: Generate Insights with memory tracking
                with memory_tracker("INSIGHTS"):
                    logger.info("Generating insights from summary")
                    insights = generate_case_insights(summary)
                    audio_instance.insights = insights
                    response_data["insights"] = insights
                    yield json.dumps({"step": "insights", "data": response_data}) + "\n"

                # Cleanup after insights
                cleanup_resources()

                # Step 7: Highlight transcript with memory tracking
                with memory_tracker("HIGHLIGHTING"):
                    logger.info("Highlighting original transcript")
                    annotated = highlighter.highlight_text(transcript, summary_entities)
                    audio_instance.annotated_text = annotated
                    response_data["annotated_text"] = annotated
                    yield json.dumps({"step": "highlighting", "data": response_data}) + "\n"

                # Save enriched data
                audio_instance.save()
                
                # Final memory check and detailed report
                final_report = detailed_gpu_memory_report()
                if isinstance(final_report, dict):
                    logger.info(f"Final GPU memory: {final_report['allocated_mb']:.1f} MB allocated, {final_report['cached_mb']:.1f} MB cached")
                    
                    # If significant memory remains, show what's on GPU
                    if final_report['allocated_mb'] > 50:
                        remaining_tensors = find_gpu_tensors()
                        if remaining_tensors:
                            logger.warning("REMAINING GPU TENSORS:")
                            for i, tensor in enumerate(remaining_tensors[:5]):
                                logger.warning(f"  {i+1}. Shape: {tensor['shape']}, Size: {tensor['size_mb']:.1f} MB, Device: {tensor['device']}")
                            
                            # Log CUDA memory summary for debugging
                            logger.info("CUDA Memory Summary:")
                            logger.info(torch.cuda.memory_summary())

            except Exception as e:
                # Log the full error details, including the stack trace, on the server
                logger.error(f"Processing failed: {type(e).__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Clean up on error
                try:
                    audio_instance.audio.delete()
                    audio_instance.delete()
                except:
                    pass  # Don't let cleanup errors mask the original error
                
                # Return a generic error message to the client
                yield json.dumps({"error": "Processing failed", "details": "An internal error occurred."}) + "\n"
                
            finally:
                # Always cleanup resources when done
                logger.info("Performing final resource cleanup")
                emergency_gpu_cleanup()
                
                # Final final check
                final_final_report = detailed_gpu_memory_report()
                if isinstance(final_final_report, dict):
                    logger.info(f"POST-CLEANUP GPU memory: {final_final_report['allocated_mb']:.1f} MB allocated, {final_final_report['cached_mb']:.1f} MB cached")

        return StreamingHttpResponse(
            process_and_stream(),
            content_type="application/json"
        )


# Alternative approach: Add cleanup middleware
class GPUMemoryCleanupMiddleware:
    """Middleware to ensure GPU memory is cleaned up after each request."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before request
        if torch.cuda.is_available():
            before_memory = torch.cuda.memory_allocated() / 1024**3
            logger.debug(f"Request started - GPU memory: {before_memory:.2f}GB")

        response = self.get_response(request)

        # After request - cleanup
        try:
            emergency_gpu_cleanup()
            if torch.cuda.is_available():
                after_memory = torch.cuda.memory_allocated() / 1024**3
                logger.debug(f"Request completed - GPU memory: {after_memory:.2f}GB")
        except Exception as e:
            logger.warning(f"Middleware cleanup error: {str(e)}")

        return response


# Management command for manual cleanup
class Command:
    """Management command to force GPU cleanup."""
    
    def handle(self, *args, **options):
        logger.info("Running manual GPU cleanup...")
        emergency_gpu_cleanup()
        
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            cached = torch.cuda.memory_reserved() / 1024**3
            print(f"After cleanup - Allocated: {allocated:.2f}GB, Cached: {cached:.2f}GB")
            
            # Show remaining tensors
            tensors = find_gpu_tensors()
            if tensors:
                print("Remaining tensors on GPU:")
                for i, tensor in enumerate(tensors[:5]):
                    print(f"  {i+1}. {tensor['size_mb']:.1f} MB - Shape: {tensor['shape']}")
        else:
            print("CUDA not available")


# Utility function for manual memory checking
def check_gpu_memory():
    """Utility function to check current GPU memory state."""
    report = detailed_gpu_memory_report()
    if isinstance(report, dict):
        print(f"Current GPU Memory:")
        print(f"  Allocated: {report['allocated_mb']:.1f} MB ({report['allocated_gb']:.2f} GB)")
        print(f"  Cached: {report['cached_mb']:.1f} MB ({report['cached_gb']:.2f} GB)")
        
        if report['allocated_mb'] > 50:  # If more than 50MB allocated
            tensors = find_gpu_tensors()
            print(f"Found {len(tensors)} tensors on GPU")
            for i, tensor in enumerate(tensors[:3]):  # Top 3
                print(f"  {i+1}. {tensor['size_mb']:.1f} MB - Shape: {tensor['shape']}")
    else:
        print(report)