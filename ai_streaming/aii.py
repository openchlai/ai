# aii.py  ----------------------------------------------------
import time
import numpy as np
import torch

from typing import Optional, Union, Tuple, List # , TYPE_CHECKING
from utils import exact_div #, format_timestamp, get_end, get_writer, make_safe, optional_float, optional_int, str2bool,
from tokenizer import get_tokenizer, LANGUAGES, TO_LANGUAGE_CODE
from decoding import DecodingOptions, DecodingResult, decode
from mel import log_mel_spectrogram, FRAMES_PER_SECOND, HOP_LENGTH, N_FRAMES, N_SAMPLES, SAMPLE_RATE
from model import Whisper, ModelDimensions

# model_name = "large-v3.pt" 
# model_alignment_heads = b"ABzY8gWO1E0{>%R7(9S+Kn!D~%ngiGaR?*L!iJG9p-nab0JQ=-{D1-g00"
	
model_name = "/usr/src/pt/tiny.pt" 
model_alignment_heads = b"ABzY8bu8Lr0{>%RKn9Fp%m@SkK7Kt=7ytkO"

def new_segment(tokenizer, *, start: float, end: float, tokens: torch.Tensor, result: DecodingResult):
	tokens = tokens.tolist()
	text_tokens = [token for token in tokens if token < tokenizer.eot]
	return {
			# "seek": seek,
			"start": start,
			"end": end,
			"text": tokenizer.decode(text_tokens),
			"tokens": tokens,
			"temperature": result.temperature,
			"avg_logprob": result.avg_logprob,
			"compression_ratio": result.compression_ratio,
			"no_speech_prob": result.no_speech_prob,
		}

def segments(model, tokenizer, options, all_tokens, tokens, result):
	#if no_speech_threshold is not None:    # no voice activity check
	#	should_skip = result.no_speech_prob > no_speech_threshold
	#	if (logprob_threshold is not None and result.avg_logprob > logprob_threshold):
	#		should_skip = False	# don't skip if the logprob is high enough, despite the no_speech_prob
	#	if should_skip:
	#		return False;  		# fast-forward to the next segment boundary

	seek 			= 0
	content_frames 		= 0 # mel.shape[-1] - N_FRAMES
	input_stride 		= exact_div(N_FRAMES, model.dims.n_audio_ctx)  # mel frames per output token: 2
	time_precision 		= (input_stride * HOP_LENGTH / SAMPLE_RATE)  # time per output token: 0.02 (seconds)
	segment_size 		= N_FRAMES # min(N_FRAMES, content_frames - seek, seek_clip_end - seek)
	segment_duration 	= segment_size * HOP_LENGTH / SAMPLE_RATE
	time_offset 		= float(seek * HOP_LENGTH / SAMPLE_RATE)
	all_segments 		= []
	current_segments 	= []

	timestamp_tokens: torch.Tensor = tokens.ge(tokenizer.timestamp_begin)	   # boolean mask of ts tokens
	single_timestamp_ending = timestamp_tokens[-2:].tolist() == [False, True]  # cmp last 2 items
	consecutive = torch.where(timestamp_tokens[:-1] & timestamp_tokens[1:])[0] # find indices where both true
	consecutive.add_(1)							   # add 1 inplace to each item
	if len(consecutive) > 0:
		# if the output contains two consecutive timestamp tokens
		slices = consecutive.tolist()
		if single_timestamp_ending:
			slices.append(len(tokens))

		last_slice = 0
		for current_slice in slices:
			sliced_tokens = tokens[last_slice:current_slice]
			start_timestamp_pos = (sliced_tokens[0].item() - tokenizer.timestamp_begin)
			end_timestamp_pos = (sliced_tokens[-1].item() - tokenizer.timestamp_begin)
			current_segments.append(
				new_segment(tokenizer, start=time_offset + start_timestamp_pos * time_precision,
				end=time_offset + end_timestamp_pos * time_precision,
				tokens=sliced_tokens,
				result=result,))
			last_slice = current_slice

		#if single_timestamp_ending:
		#	# single timestamp at the end means no speech after the last timestamp.
		#	seek += segment_size
		#else:
		#	# otherwise, ignore the unfinished segment and seek to the last timestamp
		#	last_timestamp_pos = (tokens[last_slice - 1].item() - tokenizer.timestamp_begin)
		#	seek += last_timestamp_pos * input_stride
	else:
		duration = segment_duration
		timestamps = tokens[timestamp_tokens.nonzero().flatten()]
		if (len(timestamps) > 0 and timestamps[-1].item() != tokenizer.timestamp_begin):
			# no consecutive timestamps but it has a timestamp; use the last one.
			last_timestamp_pos = (timestamps[-1].item() - tokenizer.timestamp_begin)
			duration = last_timestamp_pos * time_precision

		current_segments.append(
			new_segment(tokenizer, start=time_offset, end=time_offset + duration, tokens=tokens, result=result, ))

		# seek += segment_size

	# if a segment is instantaneous or does not contain text, clear it
	for i, segment in enumerate(current_segments):
		if segment["start"] == segment["end"] or segment["text"].strip() == "":
			segment["text"] = ""
			segment["tokens"] = []
			segment["words"] = []
		
	all_segments.extend([{"id": i, **segment} for i, segment in enumerate(current_segments, start=len(all_segments))])
	all_tokens.extend([token for segment in current_segments for token in segment["tokens"]])
	return all_segments

def decode_with_fallback(model, transcription_options, decode_options, segment: torch.Tensor) -> DecodingResult:
	decode_result = None
	for t in transcription_options["temperature"]:
		kwargs = {**decode_options}
		if t > 0: 	# disable beam_size and patience when t > 0
			kwargs.pop("beam_size", None)
			kwargs.pop("patience", None)
		else:		# disable best_of when t == 0
			kwargs.pop("best_of", None)
		options = DecodingOptions(**kwargs, temperature=t)
		decode_result = decode(model, segment, options)
		needs_fallback = False
		if (transcription_options["compression_ratio_threshold"] is not None 
			and decode_result.compression_ratio > transcription_options["compression_ratio_threshold"]):
			needs_fallback = True  # too repetitive
		if (transcription_options["logprob_threshold"] is not None 
			and decode_result.avg_logprob < transcription_options["logprob_threshold"]):
			needs_fallback = True  # average log probability is too low
		if (transcription_options["no_speech_threshold"] is not None 
			and decode_result.no_speech_prob > transcription_options["no_speech_threshold"] 
			and transcription_options["logprob_threshold"] is not None 
			and decode_result.avg_logprob < transcription_options["logprob_threshold"]):
                	needs_fallback = False  # silence
		if not needs_fallback:
			break
	return decode_result

def transcribe(model, tokenizer, options, decode_options, audio: bytearray):
	remaining_prompt_length = model.dims.n_text_ctx // 2 - 1
	prompt_reset_since = 0
	initial_prompt_tokens = []
	all_tokens = []

	if options["initial_prompt"]: # not an empty string
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
	result: DecodingResult = decode_with_fallback(model, options, decode_options, mel)
	tokens = torch.tensor(result.tokens)
	all_segments = segments(model, tokenizer, options, all_tokens, tokens, result)

	if not options["condition_on_previous_text"] or result.temperature > 0.5:
		# do not feed the prompt tokens if a high temperature was used
		prompt_reset_since = len(all_tokens)

	return dict(
		text=tokenizer.decode(all_tokens[len(initial_prompt_tokens) :]), 
		segments=all_segments, 
		language=decode_options["language"])

def load_model():
	ts0 = time.time()
	device = "cuda" if torch.cuda.is_available() else "cpu" 
	fp = open(model_name, "rb")
	checkpoint = torch.load(fp, map_location=device)
	dims = ModelDimensions(**checkpoint["dims"])
	model = Whisper(dims)
	model.load_state_dict(checkpoint["model_state_dict"])
	# model.set_alignment_heads(model_alignment_heads)
	model.to(device)
	ts1 = time.time()
	diff = round(ts1 - ts0,2) 

	print(f"Device: {device}")
	print(type(checkpoint))
	print(checkpoint.keys())
	print(dims)
	print(f"{diff} | model ready -----> {model.num_languages} languages {model.is_multilingual} ")

	options = {}
	options["dtype"]					= torch.float16
	options["temperature"]: Tuple[float, ...] 		= (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
	options["compression_ratio_threshold"]: float		= 2.4
	options["logprob_threshold"]: float 			= -1.0
	options["no_speech_threshold"]: float 			= 0.6
	options["condition_on_previous_text"]: bool 		= True
	options["initial_prompt"]: str 				= ""
	options["carry_initial_prompt"]: bool 			= False
	options["word_timestamps"]: bool 			= False
	options["prepend_punctuations"]: str 			= "\"'“¿([{-"
	options["append_punctuations"]: str 			= "\"'.。,，!！?？:：”)]}、"
	options["clip_timestamps"]: List[float] 		= [0]
	options["hallucination_silence_threshold"]: float 	= 0
	options["compression_ratio_threshold"]: float 		= 2.4
	options["logprob_threshold"]: float 			= -1.0
	options["no_speech_threshold"]: float 			= 0.6

	decode_options = {}
	decode_options["language"]: str				= "en"		# but model is multiligual so it will detect?
	decode_options["task"]: str				= "transcribe"
	decode_options["fp16"]: str				= True

	if model.device == torch.device("cpu"):
		options["dtype"] = torch.float32
		decode_options["fp16"] = False
		if torch.cuda.is_available():
			print("Performing inference on CPU when CUDA is available")

	tokenizer = get_tokenizer(
		model.is_multilingual, 
		num_languages 	= model.num_languages, 
		language	= decode_options["language"], 
		task		= decode_options["task"]
	) 

	return model, tokenizer, options, decode_options
