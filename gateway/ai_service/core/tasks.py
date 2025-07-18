# core/tasks.py

from celery import shared_task
from .pipeline import transcription, translation, summarizer, ner, classifier
from .pipeline.insights import generate_case_insights
from .utils import highlighter
from .models import AudioFile
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_audio_pipeline(self, audio_id, audio_path):
    try:
        logger.info(f"🔁 Starting audio pipeline for audio_id={audio_id}")
        audio = AudioFile.objects.get(id=audio_id)

        logger.info("🎧 Transcribing...")
        transcript = transcription.transcribe_audio(audio_path)

        logger.info("🌍 Translating...")
        translated = translation.translate(transcript)

        logger.info("📝 Summarizing...")
        summary = summarizer.summarize(translated)

        logger.info("🔍 Extracting Entities...")
        entities = ner.extract_entities(translated, flat=True)

        logger.info("🧠 Classifying...")
        classification = classifier.classify_case(translated)

        logger.info("📊 Generating Insights...")
        insights = generate_case_insights(summary)

        logger.info("🖍️ Highlighting Text...")
        annotated = highlighter.highlight_text(transcript, entities)

        logger.info("💾 Saving to database...")
        audio.transcript = transcript
        audio.insights = insights
        audio.annotated_text = annotated
        audio.save()

        logger.info("✅ Pipeline completed successfully")

        return {
            "transcript": transcript,
            "translated": translated,
            "summary": summary,
            "entities": entities,
            "classification": classification,
            "insights": insights,
            "annotated": annotated,
        }

    except Exception as e:
        logger.exception("❌ Error during audio pipeline processing")
        raise self.retry(exc=e, countdown=10, max_retries=3)
