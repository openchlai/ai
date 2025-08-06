import numpy as np
import torch
from functools import lru_cache
from .utils import exact_div

# hard-coded audio hyperparameters
SAMPLE_RATE = 16000
N_FFT = 400
HOP_LENGTH = 160
CHUNK_LENGTH = 30
N_SAMPLES = SAMPLE_RATE * CHUNK_LENGTH   			# 480000 samples in a 30-second chunk
N_SAMPLES_BYTES = SAMPLE_RATE * CHUNK_LENGTH * 2  		# 960000 samples in a 30-second chunk
N_FRAMES = exact_div(N_SAMPLES, HOP_LENGTH)  			# 3000 frames in a mel spectrogram input
N_SAMPLES_PER_TOKEN = HOP_LENGTH * 2  				# the initial convolutions has stride 2
FRAMES_PER_SECOND = exact_div(SAMPLE_RATE, HOP_LENGTH)  	# 10ms per audio frame
TOKENS_PER_SECOND = exact_div(SAMPLE_RATE, N_SAMPLES_PER_TOKEN)	# 20ms per audio token

@lru_cache(maxsize=None)
def mel_filters(device, n_mels: int) -> torch.Tensor:
	"""
	load the mel filterbank matrix for projecting STFT into a Mel spectrogram.
	Allows decoupling librosa dependency; saved using:
	np.savez_compressed(
		"mel_filters.npz",
		mel_80=librosa.filters.mel(sr=16000, n_fft=400, n_mels=80),
		mel_128=librosa.filters.mel(sr=16000, n_fft=400, n_mels=128),
	)
	"""
	assert n_mels in {80, 128}, f"Unsupported n_mels: {n_mels}"
	filters_path = "assets/mel_filters.npz" #os.path.join(os.path.dirname(__file__), "assets", "mel_filters.npz")
	with np.load(filters_path, allow_pickle=False) as f:
		return torch.from_numpy(f[f"mel_{n_mels}"]).to(device)

def log_mel_spectrogram(device, audio: bytearray, n_mels: int = 80):  
	padding = N_SAMPLES - (len(audio)//2)
	audio = np.frombuffer(audio, np.int16).flatten().astype(np.float32) / 32768.0
	audio = torch.from_numpy (audio)  	# NumPy array into a PyTorch tensor (using same memory)
	audio = audio.to(device)
	if padding > 0:				# auto-pad to fit N_SAMPLES (30 seconds)
		audio = torch.nn.functional.pad(audio, (0, padding))
	# if padding < 0:			# truncate
	#	todo
	window 		= torch.hann_window(N_FFT).to(audio.device)
	stft 		= torch.stft(audio, N_FFT, HOP_LENGTH, window=window, return_complex=True)
	magnitudes 	= stft[..., :-1].abs() ** 2
	filters 	= mel_filters(audio.device, n_mels)
	mel_spec 	= filters @ magnitudes
	log_spec 	= torch.clamp(mel_spec, min=1e-10).log10()
	log_spec 	= torch.maximum(log_spec, log_spec.max() - 8.0)
	log_spec 	= (log_spec + 4.0) / 4.0
	# print(f"padding:{padding} audio:{audio.shape} mel:{log_spec.shape}")
	return log_spec
