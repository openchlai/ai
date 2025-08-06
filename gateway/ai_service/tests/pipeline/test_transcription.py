
import pytest
from unittest.mock import patch, MagicMock
from core.pipeline.transcription import transcribe_audio, WhisperTranscriber

@pytest.mark.unit
@patch('core.pipeline.transcription.WhisperTranscriber')
def test_transcribe_audio(mock_transcriber_class):
    """
    Test the transcribe_audio function.
    """
    # Mock the WhisperTranscriber instance
    mock_transcriber_instance = MagicMock()
    mock_transcriber_instance.transcribe.return_value = "This is a test transcription."
    mock_transcriber_class.return_value = mock_transcriber_instance

    # Create a dummy audio file
    with open("test_audio.wav", "wb") as f:
        f.write(b'RIFF' + b'\x00'*1024 + b'WAVE')

    # Call the function
    transcription = transcribe_audio("test_audio.wav")

    # Check the result
    assert transcription == "This is a test transcription."

    # Check that the transcriber was instantiated and called correctly
    mock_transcriber_class.assert_called_once()
    mock_transcriber_instance.transcribe.assert_called_once_with("test_audio.wav")
