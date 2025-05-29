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
                logger.info(f"Starting transcription of {audio_instance.audio.path}")
                transcript = transcription.transcribe(audio_instance.audio.path)
                audio_instance.transcript = transcript
                logger.info("Transcription completed successfully")
                response_data = {"transcript": transcript}
                Response(response_data, status=status.HTTP_200_OK)

                # Step 2: Translate
                # logger.info("Starting translation to eng_Latn")
                # translated = translation.translate(transcript)
                # audio_instance.translated_text = translated
                # logger.info("Translation completed successfully")
                # response_data["translated_text"] = translated
                # Response(response_data, status=status.HTTP_200_OK)

                # Step 3: NER (flat list for highlighter)
                logger.info("Starting named entity recognition")
                entities = ner.extract_entities(transcript, flat=True)
                logger.info(f"Extracted {len(entities)} entities.")
                response_data["entities"] = entities
                Response(response_data, status=status.HTTP_200_OK)

                # Step 4: Classification
                logger.info("Starting classification")
                classification = classifier.classify_case(transcript)
                response_data["classification"] = classification
                Response(response_data, status=status.HTTP_200_OK)

                # Step 5: Annotate
                logger.info("Annotating text with entities")
                annotated = highlighter.highlight_text(transcript, entities)
                audio_instance.annotated_text = annotated
                response_data["annotated_text"] = annotated
                Response(response_data, status=status.HTTP_200_OK)

                # Step 6: Summarize
                # logger.info("Generating summary")
                # summary = summarizer.summarize(transcript)
                # audio_instance.summary = summary
                # response_data["summary"] = summary
                # Response(response_data, status=status.HTTP_200_OK)

                # Save enriched fields
                audio_instance.save()

                response_data["id"] = audio_instance.id

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Processing failed: {str(e)}")
                return Response({"error": "Processing failed", "details": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)