# AI Transcription Service

This service automatically monitors a folder for audio files and transcribes them using two different models:
1. A fine-tuned Transformer-based Whisper model
2. The standard OpenAI Whisper model

## How It Works

1. The service runs as a background task through the Flask application
2. Every 30 seconds, it scans the `datasets/audio` folder for audio files (.wav, .mp3, .ogg, .flac)
3. When it finds audio files, it processes them one by one:
   - First with the fine-tuned Transformer model
   - Then with the standard Whisper model
4. After transcription, it moves the audio file to `datasets/audio_done`
5. Transcription results are saved as text files in the same folder

## Using the Service

1. **Place audio files in the correct folder**:
   ```
   /home/bitz/aidev/datasets/audio/
   ```

2. **Wait for processing**:
   The service checks for new files every 30 seconds.

3. **Retrieve transcription results**:
   ```
   /home/bitz/aidev/datasets/audio_done/
   ```
   
   For each audio file (e.g., `recording.wav`), you'll find:
   - The original audio file: `recording.wav`
   - Transformer model output: `recording_transformer.txt`
   - Whisper model output: `recording_whisper.txt`

## Monitoring

You can monitor the service's activity through the system logs:

```bash
sudo journalctl -u aidev -f
```

## Troubleshooting

If the service isn't working as expected:

1. Check if the service is running:
   ```bash
   sudo systemctl status aidev
   ```

2. Ensure the necessary directories exist:
   ```bash
   mkdir -p ~/aidev/datasets/audio
   mkdir -p ~/aidev/datasets/audio_done
   ```

3. Check permissions:
   ```bash
   sudo chown -R bitz:bitz ~/aidev/datasets
   ```

4. Restart the service:
   ```bash
   sudo systemctl restart aidev
   ```

## Notes

- The service uses GPU acceleration if available
- Each model is loaded and unloaded sequentially to conserve system resources
- Transcription may take several minutes depending on file length and system capabilities

## Transcription, to get unique ids
```sh
curl "localhost:50001/transcribe/data/casedata" \
-H "Content-Type: application/json" \
--data '{"task": "transcribe", "transcription_only": "true", "docs":100}'
```   