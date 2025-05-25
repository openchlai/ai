from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import AudioFile
from .serializers import AudioFileSerializer
from .pipeline import transcription, translation, ner, classifier, summarizer
from .utils import highlighter
import logging

logger = logging.getLogger(__name__)

class AudioUploadView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            audio_instance = serializer.save()

            try:
                # Step 1: Transcribe
                transcript = transcription.transcribe(audio_instance.audio.path)
                audio_instance.transcript = transcript

                # Step 2: Translate
                translated = translation.translate(transcript)
                audio_instance.translated_text = translated

                # Step 3: NER
                extracted = ner.extract_entities(translated)
                # Flatten entity structure
                entities = [{"text": ent, "label": label} for label, ents in extracted.items() for ent in ents]

                # Step 4: Classification
                classification = classifier.classify(translated)

                # Step 5: Annotate
                annotated = highlighter.highlight_text(translated, entities)
                audio_instance.annotated_text = annotated

                # Step 6: Summarize
                summary = summarizer.summarize(translated)
                audio_instance.summary = summary

                # Save enriched fields
                audio_instance.save()

                response_data = {
                    "id": audio_instance.id,
                    "transcript": transcript,
                    "translated_text": translated,
                    "entities": entities,
                    "classification": classification,
                    "annotated_text": annotated,
                    "summary": summary,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Processing failed: {str(e)}")
                return Response({"error": "Processing failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
