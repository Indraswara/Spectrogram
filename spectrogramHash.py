import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import hashlib
import os


def toDatabase(folder: str) -> list[[dict[str, list[int]]]]: 
    files = [file for file in os.listdir(folder) if file.endswith('.wav')] 
    database: list[[dict[str, list[int]]]] = []

    for file in files: 
        file_path = os.path.join(folder, file) 
        truncated_Hash, spectrogram = spectrogramHash(file_path) 
        entry = {file: {'hash': truncated_Hash, 'spectrogram': spectrogram.tolist()}}
        database.append(entry)
    
    return database

def spectrogramHash(audio_file: str, keyLength: int = 10) -> dict[str, list[int]]:
    data, samplerate = sf.read(audio_file)

    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    window_size = 1024
    hop_size = 512
    
    n_samples = len(data)
    n_overlap = window_size - hop_size
    n_windows = (n_samples - n_overlap) // hop_size
    
    spectrogram = []
    
    for i in range(n_windows):
        start = i * hop_size
        end = start + window_size
        segment = data[start:end]
        windowed_segment = segment * np.hamming(window_size)
        spectrum = np.abs(np.fft.rfft(windowed_segment, window_size))
        spectrogram.append(spectrum)
    
    spectrogram_array = np.array(spectrogram)
    
    concatenated_hash = b''
    for row in spectrogram_array:
        row_bytes = row.tobytes()
        sha256_hash = hashlib.sha256(row_bytes).hexdigest().encode('utf-8')
        concatenated_hash += sha256_hash
    
    unique_hash = concatenated_hash.hex()
    truncated_Hash = unique_hash[:keyLength]
    
    return truncated_Hash, spectrogram_array

hashAudio = spectrogramHash("./data/1.wav")
print(f"Hash audio is {hashAudio}")

data = './data'
database = toDatabase(data)
print(database[1])
