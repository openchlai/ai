<<<<<<< HEAD
import time
import logging
from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
=======
# core/tasks.py

from celery import shared_task
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
from .pipeline import transcription, translation, summarizer, ner, classifier
from .pipeline.insights import generate_case_insights
from .utils import highlighter
from .models import AudioFile
<<<<<<< HEAD

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = get_task_logger(__name__)


def stream_to_frontend(task_id, step, message=None, data=None, progress=None, status="in_progress"):
    """Helper to send WebSocket messages to the frontend."""
    safe_group = f"task_{task_id}" .replace("-", "_")[:95]
    # safe_group = f"task_{task_id}"  # no .replace()

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        safe_group,
        {
            "type": "stream_output",
            "data": {
                "step": step,
                "status": status,
                "message": message,
                "progress": progress,
                "payload": data or {},
            }
        }
    )


@shared_task(bind=True)
def process_audio_pipeline(self, audio_id, audio_path):
    """Complete audio processing pipeline with logging and live streaming."""
    pipeline_start = time.time()
    task_id = self.request.id

    try:
        stream_to_frontend(task_id, "start", "🔄 Starting pipeline", progress=0)

        logger.info(f"""
        🚀 Starting audio pipeline
        Task ID: {task_id}
        Audio ID: {audio_id}
        Path: {audio_path}
        """)

        stream_to_frontend(task_id, "loading", "🔍 Loading audio file...", progress=5)
        audio = AudioFile.objects.get(id=audio_id)

        # Step 1: Transcription
        stream_to_frontend(task_id, "transcription", "🎧 Transcribing audio...", progress=10)
        transcript_start = time.time()
        transcript = transcription.transcribe_audio(audio_path)
        transcription_time = time.time() - transcript_start
        stream_to_frontend(task_id, "transcription", "✅ Transcription complete", {
            "duration": str(timedelta(seconds=transcription_time)),
            "text_sample": transcript[:200]
        }, progress=30)

        # Step 2: Translation
        stream_to_frontend(task_id, "translation", "🌍 Translating text...", progress=35)
        translated = translation.translate(transcript)
        stream_to_frontend(task_id, "translation", "✅ Translation complete", {
            "sample": translated[:200]
        }, progress=45)

        # Step 3: Summarization
        stream_to_frontend(task_id, "summarization", "📝 Summarizing content...", progress=50)
        summary = summarizer.summarize(translated)
        stream_to_frontend(task_id, "summarization", "✅ Summary generated", {
            "summary": summary
        }, progress=60)

        # Step 4: NER
        stream_to_frontend(task_id, "ner", "🔍 Extracting named entities...", progress=65)
        entities = ner.extract_entities(translated, flat=True)
        stream_to_frontend(task_id, "ner", "✅ Entities extracted", {
            "entities": entities[:5] if entities else []
        }, progress=70)

        # Step 5: Classification
        stream_to_frontend(task_id, "classification", "🧠 Classifying content...", progress=75)
        classification = classifier.classify_case(translated)
        stream_to_frontend(task_id, "classification", "✅ Classification complete", {
            "classification": classification
        }, progress=80)

        # Step 6: Insights
        stream_to_frontend(task_id, "insights", "📊 Generating insights...", progress=85)
        insights = generate_case_insights(summary)
        stream_to_frontend(task_id, "insights", "✅ Insights complete", {
            "insight_keys": list(insights.keys())
        }, progress=90)

        # Step 7: Highlighting
        stream_to_frontend(task_id, "highlighting", "🖍️ Highlighting entities...", progress=93)
        annotated = highlighter.highlight_text(transcript, entities)
        stream_to_frontend(task_id, "highlighting", "✅ Highlighting done", progress=95)

        # Save to DB
        audio.transcript = transcript
        audio.insights = insights
        audio.annotated_text = annotated
        audio.summary = summary
        audio.translated_text = translated
        audio.save()

        total_time = time.time() - pipeline_start
        stream_to_frontend(task_id, "done", "🎉 Processing complete", {
            "processing_time": str(timedelta(seconds=total_time)),
            "classification": classification,
            "entity_count": len(entities),
            "summary": summary,
        }, progress=100, status="done")

        logger.info(f"""
        🎉 Pipeline completed successfully!
        Task ID: {task_id}
        Audio ID: {audio_id}
        Processing time: {str(timedelta(seconds=total_time))}
        """)

        return {
            'status': 'SUCCESS',
            'processing_time': total_time,
            'transcription_time': transcription_time,
            'text_length': len(transcript),
            'entity_count': len(entities),
            'classification': classification,
            'insights': insights,
            'task_id': task_id
        }

    except Exception as e:
        logger.exception(f"❌ Pipeline failed: {str(e)}")
        stream_to_frontend(task_id, "error", f"❌ Error: {str(e)}", status="error", progress=0)
        raise self.retry(exc=e, countdown=min(10 * (self.request.retries + 1), 60), max_retries=3)
=======
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
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
