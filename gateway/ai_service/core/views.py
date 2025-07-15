from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import AudioFile
from .serializers import AudioFileSerializer
from .pipeline import transcription, translation, ner, classifier, summarizer
from .utils import highlighter
from .pipeline.insights import generate_case_insights
import json
import logging
import traceback

# Set up logging for this module
logger = logging.getLogger(__name__)

# Disable CSRF protection for this view
@method_decorator(csrf_exempt, name='dispatch')
class AudioUploadView(APIView):
    # Allow multipart form data and form data for file uploads
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        # Validate the incoming data using the AudioFileSerializer
        serializer = AudioFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded audio file
        audio_instance = serializer.save()

        def process_and_stream():
            # Initialize response data with the audio instance ID
            response_data = {"id": audio_instance.id}

            try:
                # Step 1: Convert audio to text using transcription service
                logger.info(f"Transcribing audio: {audio_instance.audio.path}")
                transcript = transcription.transcribe_audio(audio_instance.audio.path)
                audio_instance.transcript = transcript
                response_data["transcript"] = transcript
                yield json.dumps({"step": "transcription", "data": response_data}) + "\n"

                # Step 2: Translate the transcript to target language
                logger.info("Translating transcript")
                translated_transcript = translation.translate(transcript)
                response_data["translated_transcript"] = translated_transcript
                yield json.dumps({"step": "translation", "data": response_data}) + "\n"

                # Step 3: Create a summary of the translated transcript
                logger.info("Summarizing translated transcript")
                summary = summarizer.summarize(translated_transcript)
                response_data["summary"] = summary
                yield json.dumps({"step": "summarization", "data": response_data}) + "\n"

                # Step 4: Extract named entities from the summary
                logger.info("Extracting named entities from summary")
                summary_entities = ner.extract_entities(translated_transcript, flat=True)
                response_data["summary_entities"] = summary_entities
                yield json.dumps({"step": "ner", "data": response_data}) + "\n"

                # Step 5: Classify the case based on the summary
                logger.info("Classifying summarized case")
                summary_classification = classifier.classify_case(translated_transcript)
                response_data["summary_classification"] = summary_classification
                yield json.dumps({"step": "classification", "data": response_data}) + "\n"

                # Step 6: Generate insights from the summary
                logger.info("Generating insights from summary")
                insights = generate_case_insights(summary)
                audio_instance.insights = insights
                response_data["insights"] = insights
                yield json.dumps({"step": "insights", "data": response_data}) + "\n"

                # Step 7: Highlight entities in the original transcript
                logger.info("Highlighting original transcript")
                annotated = highlighter.highlight_text(transcript, summary_entities)
                audio_instance.annotated_text = annotated
                response_data["annotated_text"] = annotated
                yield json.dumps({"step": "highlighting", "data": response_data}) + "\n"

                # Save all the processed data to the database
                audio_instance.save()

            except Exception as e:
                # Handle any errors during processing
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                }
                logger.error(f"Processing failed: {error_details}")
                # Clean up by deleting the audio file and instance if processing fails
                audio_instance.audio.delete()
                audio_instance.delete()
                yield json.dumps({"error": "Processing failed", "details": error_details}) + "\n"

        # Return a streaming response that processes the audio file and yields results
        return StreamingHttpResponse(process_and_stream(), content_type="application/json")
