import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from celery.result import AsyncResult
from .models import AudioFile

logger = logging.getLogger(__name__)

class AudioProcessingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.task_group_name = f'task_{self.task_id}'
        self.safe_group = self.task_group_name.replace("-", "_")[:95]

        # Join task group
        await self.channel_layer.group_add(
            self.safe_group,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected for task {self.task_id}")

        # Send initial status
        await self.send_task_status()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.safe_group,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for task {self.task_id}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'status_request')

            if message_type == 'status_request':
                await self.send_task_status()
            elif message_type == 'result_request':
                audio_id = text_data_json.get('audio_id')
                if audio_id:
                    await self.send_audio_result(audio_id)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    async def send_task_status(self):
        """Send current task status to WebSocket"""
        try:
            result = AsyncResult(self.task_id)

            status_data = {
                'type': 'task_status',
                'task_id': self.task_id,
                'status': result.status,
                'timestamp': result.date_done.isoformat() if result.date_done else None,
            }

            if result.status == 'SUCCESS':
                status_data.update({
                    'result': result.result,
                    'completed': True,
                    'progress': 100
                })
            elif result.status == 'FAILURE':
                status_data.update({
                    'error': str(result.result),
                    'completed': False,
                    'progress': 0
                })
            elif result.status == 'PENDING':
                status_data.update({
                    'message': 'Task is queued and waiting to start',
                    'completed': False,
                    'progress': 0
                })
            elif result.status == 'RETRY':
                status_data.update({
                    'message': 'Task is retrying after an error',
                    'completed': False,
                    'progress': 25
                })
            elif result.status == 'PROGRESS':
                if hasattr(result, 'info') and result.info:
                    status_data.update({
                        'meta': result.info,
                        'progress': result.info.get('progress', 50),
                        'stage': result.info.get('stage', 'processing'),
                        'message': f"Processing: {result.info.get('stage', 'processing')}"
                    })
                else:
                    status_data.update({
                        'progress': 50,
                        'message': 'Task is in progress'
                    })
                status_data['completed'] = False

            await self.send(text_data=json.dumps(status_data))

        except Exception as e:
            logger.error(f"Error sending task status: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Failed to retrieve task status'
            }))

    @database_sync_to_async
    def get_audio_file(self, audio_id):
        """Get audio file from database"""
        try:
            return AudioFile.objects.get(id=audio_id)
        except AudioFile.DoesNotExist:
            return None

    async def send_audio_result(self, audio_id):
        """Send audio processing result to WebSocket"""
        try:
            audio_file = await self.get_audio_file(audio_id)
            if not audio_file:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': 'Audio file not found'
                }))
                return

            is_processed = bool(
                audio_file.transcript and 
                audio_file.insights and 
                audio_file.summary
            )

            result_data = {
                'type': 'audio_result',
                'audio_id': audio_id,
                'audio_url': audio_file.audio.url if audio_file.audio else None,
                'transcript': audio_file.transcript,
                'translated_text': audio_file.translated_text,
                'annotated_text': audio_file.annotated_text,
                'summary': audio_file.summary,
                'insights': audio_file.insights,
                'created_at': audio_file.created_at.isoformat(),
                'updated_at': audio_file.updated_at.isoformat(),
                'is_processed': is_processed,
                'has_transcript': bool(audio_file.transcript),
                'has_insights': bool(audio_file.insights),
                'has_summary': bool(audio_file.summary),
                'has_translation': bool(audio_file.translated_text),
                'has_annotations': bool(audio_file.annotated_text),
            }

            await self.send(text_data=json.dumps(result_data))

        except Exception as e:
            logger.error(f"Error sending audio result: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Failed to retrieve audio result'
            }))

    async def task_update(self, event):
        """Handle task update messages from group"""
        await self.send(text_data=json.dumps(event['data']))

    async def processing_progress(self, event):
        """Handle processing progress updates"""
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            **event['data']
        }))

    async def processing_complete(self, event):
        """Handle processing completion"""
        await self.send(text_data=json.dumps({
            'type': 'processing_complete',
            **event['data']
        }))

    async def stream_output(self, event):
        """Handle real-time streamed steps from the Celery task"""
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            **event['data']
        }))
