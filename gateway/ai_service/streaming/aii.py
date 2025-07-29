import time
import torch
import numpy as np

from typing import Optional, Union, Tuple, List
from .utils import exact_div
from .tokenizer import get_tokenizer, LANGUAGES, TO_LANGUAGE_CODE
from .decoding import DecodingOptions, DecodingResult, DecodingTask
from .mel import log_mel_spectrogram, FRAMES_PER_SECOND, HOP_LENGTH, N_FRAMES, N_SAMPLES, SAMPLE_RATE
from .model import Whisper, ModelDimensions


def new_segment(tokenizer, *, start: float, end: float, tokens: torch.Tensor):
    tokens = tokens.tolist()
    text_tokens = [token for token in tokens if token < tokenizer.eot]
    return {
        "start": start,
        "end": end,
        "text": tokenizer.decode(text_tokens),
        "tokens": tokens
    }


def segments(model, tokenizer, tokens, result):
    seek = 0
    input_stride = exact_div(N_FRAMES, model.dims.n_audio_ctx)
    time_precision = input_stride * HOP_LENGTH / SAMPLE_RATE
    segment_size = N_FRAMES
    segment_duration = segment_size * HOP_LENGTH / SAMPLE_RATE
    time_offset = float(seek * HOP_LENGTH / SAMPLE_RATE)
    current_segments = []

    timestamp_tokens: torch.Tensor = tokens.ge(tokenizer.timestamp_begin)
    single_timestamp_ending = timestamp_tokens[-2:].tolist() == [False, True]
    consecutive = torch.where(timestamp_tokens[:-1] & timestamp_tokens[1:])[0]
    consecutive.add_(1)

    if len(consecutive) > 0:
        slices = consecutive.tolist()
        if single_timestamp_ending:
            slices.append(len(tokens))
        last_slice = 0
        for current_slice in slices:
            sliced_tokens = tokens[last_slice:current_slice]
            start_timestamp_pos = (sliced_tokens[0].item() - tokenizer.timestamp_begin)
            end_timestamp_pos = (sliced_tokens[-1].item() - tokenizer.timestamp_begin)
            current_segments.append(
                new_segment(
                    tokenizer,
                    start=time_offset + start_timestamp_pos * time_precision,
                    end=time_offset + end_timestamp_pos * time_precision,
                    tokens=sliced_tokens
                )
            )
            last_slice = current_slice
    else:
        duration = segment_duration
        timestamps = tokens[timestamp_tokens.nonzero().flatten()]
        if len(timestamps) > 0 and timestamps[-1].item() != tokenizer.timestamp_begin:
            last_timestamp_pos = (timestamps[-1].item() - tokenizer.timestamp_begin)
            duration = last_timestamp_pos * time_precision
        current_segments.append(
            new_segment(tokenizer, start=time_offset, end=time_offset + duration, tokens=tokens)
        )

    return current_segments


def decode_with_fallback(model, tokenizer, transcription_options, decode_options, mel: torch.Tensor) -> DecodingResult:
    decode_result = None
    for t in transcription_options["temperature"]:
        kwargs = {**decode_options}
        if t > 0:
            kwargs.pop("beam_size", None)
            kwargs.pop("patience", None)
        else:
            kwargs.pop("best_of", None)
        options = DecodingOptions(**kwargs, temperature=t)
        with torch.no_grad():
            decode_result = DecodingTask(model, tokenizer, options).run(mel)[0]

        needs_fallback = False
        if (
            transcription_options["compression_ratio_threshold"] is not None
            and decode_result.compression_ratio > transcription_options["compression_ratio_threshold"]
        ):
            needs_fallback = True
        if (
            transcription_options["logprob_threshold"] is not None
            and decode_result.avg_logprob < transcription_options["logprob_threshold"]
        ):
            needs_fallback = True
        if (
            transcription_options["no_speech_threshold"] is not None
            and decode_result.no_speech_prob > transcription_options["no_speech_threshold"]
            and transcription_options["logprob_threshold"] is not None
            and decode_result.avg_logprob < transcription_options["logprob_threshold"]
        ):
            needs_fallback = False
        if not needs_fallback:
            break
    return decode_result


def transcribe(model, tokenizer, options, decode_options, audio: bytearray):
    remaining_prompt_length = model.dims.n_text_ctx // 2 - 1
    prompt_reset_since = 0
    initial_prompt_tokens = []
    all_tokens = []

    if options["initial_prompt"]:
        initial_prompt_tokens = tokenizer.encode(" " + options["initial_prompt"].strip())
        all_tokens.extend(initial_prompt_tokens)
        remaining_prompt_length -= len(initial_prompt_tokens)

    if options["carry_initial_prompt"]:
        nignored = max(len(initial_prompt_tokens), prompt_reset_since)
        remaining_prompt = all_tokens[nignored:][-remaining_prompt_length:]
        decode_options["prompt"] = initial_prompt_tokens + remaining_prompt
    else:
        decode_options["prompt"] = all_tokens[prompt_reset_since:]

    mel = log_mel_spectrogram(model.device, audio, model.dims.n_mels)
    mel.to(model.device).to(options["dtype"])
    mel = mel.unsqueeze(0)

    result: DecodingResult = decode_with_fallback(model, tokenizer, options, decode_options, mel)
    tokens = torch.tensor(result.tokens)
    current_segments = segments(model, tokenizer, tokens, result)

    if not options["condition_on_previous_text"] or result.temperature > 0.5:
        prompt_reset_since = len(tokens)

    return current_segments


def load_model(model_path: str) -> Tuple[Whisper, any, dict, dict]:
    ts0 = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint = torch.load(model_path, map_location=device)

    dims = ModelDimensions(**checkpoint["dims"])
    model = Whisper(dims)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    ts1 = time.time()
    print(f"Device: {device}")
    print(dims)
    print(f"{round(ts1 - ts0, 2)}s | model ready -----> {model.num_languages} languages, multilingual={model.is_multilingual}")

    options = {
        "dtype": torch.float16 if device == "cuda" else torch.float32,
        "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        "compression_ratio_threshold": 2.4,
        "logprob_threshold": -1.0,
        "no_speech_threshold": 0.6,
        "condition_on_previous_text": True,
        "initial_prompt": "",
        "carry_initial_prompt": False,
        "word_timestamps": False,
        "prepend_punctuations": "\"'“¿([{-",
        "append_punctuations": "\"'.。,，!！?？:：”)]}、",
        "clip_timestamps": [0],
        "hallucination_silence_threshold": 0,
    }

    decode_options = {
        "language": "en",
        "task": "transcribe",
        "fp16": device == "cuda",
    }

    tokenizer = get_tokenizer(
        model.is_multilingual,
        num_languages=model.num_languages,
        language=decode_options["language"],
        task=decode_options["task"]
    )

    return model, tokenizer, options, decode_options
