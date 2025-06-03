from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import AudioFile
from .serializers import AudioFileSerializer
from .pipeline import transcription, translation, ner, classifier, summarizer
from .utils import highlighter
from .pipeline.insights import generate_case_insights  # Import the new function
import logging
import traceback

logger = logging.getLogger(__name__)

class AudioUploadView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            audio_instance = serializer.save()

            try:
                # Step 1: Transcribe
                logger.info(f"Starting transcription of {audio_instance.audio.path}")
                transcript = transcription.transcribe(audio_instance.audio.path)
                audio_instance.transcript = transcript
                logger.info("Transcription completed successfully")
                response_data = {"transcript": transcript}

                # Step 2: Generate Insights
                logger.info("Generating case insights")
                insights = generate_case_insights(transcript)
                audio_instance.insights = insights  # Assuming you have a JSONField for insights
                response_data["insights"] = insights
                logger.info("Insights generation completed")

                # Step 3: NER (flat list for highlighter)
                logger.info("Starting named entity recognition")
                entities = ner.extract_entities(transcript, flat=True)
                logger.info(f"Extracted {len(entities)} entities.")
                response_data["entities"] = entities

                # Step 4: Classification
                logger.info("Starting classification")
                classification = classifier.classify_case(transcript)
                response_data["classification"] = classification

                # Step 5: Annotate
                logger.info("Annotating text with entities")
                annotated = highlighter.highlight_text(transcript, entities)
                audio_instance.annotated_text = annotated
                response_data["annotated_text"] = annotated

                # Save all enriched fields
                audio_instance.save()

                response_data["id"] = audio_instance.id

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                }
                logger.error(f"Processing failed: {error_details}")
                # Clean up the audio file if processing fails
                audio_instance.audio.delete()
                audio_instance.delete()
                return Response(
                    {"error": "Processing failed", "details": error_details},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)