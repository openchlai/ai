from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import torchaudio
import os
import re
import numpy as np
from threading import Thread
from time import sleep, time
from core import creds


def scribe_timer(data=False):
    pass
    try:
        i = 0
        while True:
            sleep(30)
            i += 1
            print("I've woken up", i)
            if i >= 10:
                break
    except Exception as e:
        raise e
    return


def transcribe(data):

    # ✅ Define the model directory
    model_path = "/home/k_nurf/voice_recognition/whisper-small-sw"

    # ✅ Load the processor & model
    processor = WhisperProcessor.from_pretrained(model_path)
    model = WhisperForConditionalGeneration.from_pretrained(model_path).to(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    # ✅ Set model to evaluation mode
    model.eval()
    model.generation_config.forced_decoder_ids = None  # Fix forced_decoder_ids warning

    # ✅ Load and preprocess audio
    audio_path = "/home/k_nurf/transcription_data_set_1/1737216594.179989.wav"
    speech_array, sampling_rate = torchaudio.load(audio_path)

    # ✅ Ensure 16kHz sampling rate
    from torchaudio.transforms import Resample

    if sampling_rate != 16000:
        resampler = Resample(orig_freq=sampling_rate, new_freq=16000)
        speech_array = resampler(speech_array)

    # ✅ Split the audio into 30-second chunks
    chunk_size = 30 * 16000  # 30 seconds * 16,000 samples per second
    total_samples = speech_array.shape[1]
    num_chunks = (total_samples // chunk_size) + 1

    transcriptions = []  # Store all transcriptions

    for i in range(num_chunks):
        start_sample = i * chunk_size
        end_sample = min((i + 1) * chunk_size, total_samples)

        if start_sample >= total_samples:
            break  # Stop if we've reached the end of the audio

        chunk = speech_array[:, start_sample:end_sample]  # Extract audio chunk

        # ✅ Convert chunk to model input format
        inputs = processor.feature_extractor(
            chunk.squeeze().numpy(), sampling_rate=16000, return_tensors="pt"
        )

        input_features = inputs.input_features.to(model.device)
        attention_mask = (
            inputs.attention_mask.to(model.device)
            if "attention_mask" in inputs
            else None
        )

        # ✅ Run inference with optimized parameters
        with torch.no_grad():
            predicted_ids = model.generate(
                input_features,
                attention_mask=attention_mask,
                max_length=225,
                num_beams=5,  # Beam search to improve output
                temperature=0.7,
                repetition_penalty=1.5,
            )

        # ✅ Decode and clean up transcription
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[
            0
        ]
        transcription = re.sub(
            r"[^a-zA-Z0-9\s.,?!]", "", transcription
        )  # Remove unwanted symbols
        transcription = re.sub(r"\s+", " ", transcription).strip()  # Clean spaces

        transcriptions.append(transcription)  # Save chunk result
        print(f"📝 Transcribed chunk {i + 1}/{num_chunks}: {transcription}")

    # ✅ Merge all transcriptions
    full_transcription = " ".join(transcriptions)

    print("\n🚀 **Final Full Transcription:**")
    print(full_transcription)
