#mel.py (whisper/audio.py)---------------------------------------------

import numpy as np
import torch
from functools import lru_cache
from utils import exact_div

# hard-coded audio hyperparameters
SAMPLE_RATE = 16000
N_FFT = 400
HOP_LENGTH = 160
CHUNK_LENGTH = 30
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE  # 480000 samples in a 30-second chunk
N_FRAMES = exact_div(N_SAMPLES, HOP_LENGTH)  # 3000 frames in a mel spectrogram input

N_SAMPLES_PER_TOKEN = HOP_LENGTH * 2  # the initial convolutions has stride 2
FRAMES_PER_SECOND = exact_div(SAMPLE_RATE, HOP_LENGTH)  # 10ms per audio frame
TOKENS_PER_SECOND = exact_div(SAMPLE_RATE, N_SAMPLES_PER_TOKEN)  # 20ms per audio token

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

def log_mel_spectrogram(device, audio: np.ndarray, n_mels: int = 80, padding: int = 0): # read from socket // max 30 seconds // audio is np.int16 
	audio = audio.astype(np.float32) / 32768.0  # flatten copies  // flatten().
	audio = torch.from_numpy (audio)  # NumPy array into a PyTorch tensor (using same memory)
	audio = audio.to(device)
	if (padding > 0):
		audio = torch.nn.functional.pad(audio, (0, padding))
	window = torch.hann_window(N_FFT).to(audio.device)
	stft = torch.stft(audio, N_FFT, HOP_LENGTH, window=window, return_complex=True)
	magnitudes = stft[..., :-1].abs() ** 2
	filters = mel_filters(audio.device, n_mels)
	mel_spec = filters @ magnitudes
	log_spec = torch.clamp(mel_spec, min=1e-10).log10()
	log_spec = torch.maximum(log_spec, log_spec.max() - 8.0)
	log_spec = (log_spec + 4.0) / 4.0
	return log_spec

def pad_or_trim(array, length: int = N_SAMPLES, *, axis: int = -1):
	# Pad or trim the audio array to N_SAMPLES, as expected by the encoder.
	if torch.is_tensor(array):
		if array.shape[axis] > length:
			array = array.index_select(dim=axis, index=torch.arange(length, device=array.device))

		if array.shape[axis] < length:
			pad_widths = [(0, 0)] * array.ndim
			pad_widths[axis] = (0, length - array.shape[axis])
			array = torch.nn.functional.pad(array, [pad for sizes in pad_widths[::-1] for pad in sizes])
	else:
		if array.shape[axis] > length:
			array = array.take(indices=range(length), axis=axis)

		if array.shape[axis] < length:
			pad_widths = [(0, 0)] * array.ndim
			pad_widths[axis] = (0, length - array.shape[axis])
			array = np.pad(array, pad_widths)

	return array
