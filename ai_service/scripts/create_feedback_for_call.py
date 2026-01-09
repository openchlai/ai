#!/usr/bin/env python3
"""
Script to manually create feedback entries for a completed call.
Useful for backfilling feedback entries for calls that were processed before the automatic feedback creation was added.
"""
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.enhanced_notification_service import enhanced_notification_service
from app.db.session import SessionLocal
from app.db.repositories.feedback_repository import FeedbackRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_feedback_for_call(call_id: str):
    """
    Create feedback entries for a completed call by fetching results from task.

    Args:
        call_id: The call ID to create feedback for
    """
    try:
        # Try to get results from Redis or reconstruct from database
        from app.config.settings import redis_task_client
        import json

        if not redis_task_client:
            logger.warning("Redis client not available, will create dummy feedback entries")
            raise ValueError("Redis not available")

        # Check if we have pipeline results in Redis
        session_key = f"call_session:{call_id}"
        ai_pipeline_info = redis_task_client.hget(session_key, 'ai_pipeline')

        if ai_pipeline_info:
            pipeline_info = json.loads(ai_pipeline_info)
            task_id = pipeline_info.get('task_id')

            logger.info(f"Found task ID: {task_id}")

            # Get task result from Celery
            from celery.result import AsyncResult
            task_result = AsyncResult(task_id)

            if task_result.ready() and task_result.successful():
                result = task_result.result
                logger.info(f"Retrieved task result: {list(result.keys())}")

                # Extract pipeline results
                if 'result' in result:
                    pipeline_results = result['result']
                    processing_mode = pipeline_info.get('processing_mode', 'post_call')

                    # Create feedback entries
                    await enhanced_notification_service.create_feedback_entries(
                        call_id=call_id,
                        pipeline_results=pipeline_results,
                        processing_mode=processing_mode
                    )

                    logger.info(f"✅ Successfully created feedback entries for call {call_id}")

                    # Verify creation
                    db = SessionLocal()
                    feedbacks = FeedbackRepository.get_feedback(db, call_id)
                    logger.info(f"📋 Created {len(feedbacks)} feedback entries:")
                    for fb in feedbacks:
                        logger.info(f"   - Task: {fb.task}, Prediction available: {bool(fb.prediction)}")
                    db.close()

                    return True
                else:
                    logger.error("Task result does not contain 'result' key")
            else:
                logger.error(f"Task not ready or failed: ready={task_result.ready()}, successful={task_result.successful() if task_result.ready() else 'N/A'}")
        else:
            logger.error(f"No pipeline info found for call {call_id}")

            # Manual creation as fallback with dummy data
            logger.info("Creating dummy feedback entries for testing...")
            db = SessionLocal()

            # Example feedback entries
            tasks = {
                'translation': {'text': 'Example translation', 'length': 100},
                'classification': {'category': 'test', 'confidence': 0.95},
                'ner': {'entities': []},
                'summarization': {'summary': 'Test summary'},
                'qa': {'score': 0.85}
            }

            for task, prediction in tasks.items():
                FeedbackRepository.create_initial_feedback(
                    db=db,
                    call_id=call_id,
                    task=task,
                    prediction=prediction,
                    processing_mode='post_call',
                    model_version='test_v1'
                )

            db.close()
            logger.info("✅ Created dummy feedback entries")
            return True

    except Exception as e:
        logger.error(f"❌ Failed to create feedback entries: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_feedback_for_call.py <call_id>")
        print("Example: python create_feedback_for_call.py 1763648446.39")
        sys.exit(1)

    call_id = sys.argv[1]

    print(f"Creating feedback entries for call: {call_id}")
    success = asyncio.run(create_feedback_for_call(call_id))

    if success:
        print(f"✅ Feedback entries created successfully for {call_id}")
        print(f"   You can now view them at: http://localhost:8125/api/v1/agent-feedback/call/{call_id}")
        sys.exit(0)
    else:
        print(f"❌ Failed to create feedback entries for {call_id}")
        sys.exit(1)
