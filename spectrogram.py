import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def spectrogram(audio_file):
    rate, data = wavfile.read(audio_file)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    window_size = 1024
    hop_size = 512
    
    n_samples = len(data)
    n_overlap = window_size - hop_size
    n_windows = (n_samples - n_overlap) // hop_size
    
    spectrogram = np.zeros((n_windows, window_size // 2 + 1))
    
    for i in range(n_windows):
        start = i * hop_size
        end = start + window_size
        segment = data[start:end]
        windowed_segment = segment * np.hamming(window_size)
        spectrum = np.abs(np.fft.rfft(windowed_segment, window_size))
        spectrogram[i] = spectrum
    
    plt.figure(figsize=(7, 5))
    plt.imshow(np.log1p(spectrogram.T), aspect='auto', origin='lower')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.show()

audio_file_path = './data/file_example_WAV_2MG.wav'
spectrogram(audio_file_path)
