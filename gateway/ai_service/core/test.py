import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings

from .pipeline import transcription, translation, ner, classifier, summarizer
from .utils import highlighter

class PipelineModuleTests(TestCase):
    def test_transcription(self):
        # NOTE: Use a small sample audio file path in your test data or mock whisper call
        sample_audio = os.path.join(settings.BASE_DIR, 'core/tests/test_audio.wav')
        # Here, you would typically mock transcription for CI environments
        text = transcription.transcribe(sample_audio)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_translation(self):
        sample_text = "Bonjour"
        translated = translation.translate(sample_text)
        self.assertIsInstance(translated, str)
        self.assertIn("Hello", translated)  # or equivalent expected translation

    def test_ner(self):
        sample_text = "Barack Obama was the 44th President of the United States."
        entities = ner.extract_entities(sample_text)
        self.assertIsInstance(entities, list)
        self.assertTrue(any(ent['text'] == "Barack Obama" for ent in entities))

    def test_classification(self):
        sample_text = "This is a test"
        classification = classifier.classify(sample_text)
        self.assertIsInstance(classification, dict)
        self.assertIn("category", classification)

    def test_summarization(self):
        sample_text = ("The quick brown fox jumps over the lazy dog. " * 10)
        summary = summarizer.summarize(sample_text)
        self.assertIsInstance(summary, str)
        self.assertLess(len(summary), len(sample_text))

    def test_highlighter(self):
        text = "Alice went to Wonderland."
        entities = [{"text": "Alice", "label": "PERSON"}]
        highlighted = highlighter.highlight_text(text, entities)
        self.assertIn("[Alice|PERSON]", highlighted)


class AudioUploadAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_upload_audio_and_process(self):
        # Use a small test wav file under core/tests/test_audio.wav
        test_audio_path = os.path.join(settings.BASE_DIR, 'core/tests/test_audio.wav')
        with open(test_audio_path, 'rb') as audio_file:
            response = self.client.post(
                reverse('audio-upload'),
                {'audio': audio_file},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('transcript', data)
        self.assertIn('translated_text', data)
        self.assertIn('entities', data)
        self.assertIn('classification', data)
        self.assertIn('annotated_text', data)
        self.assertIn('summary', data)
