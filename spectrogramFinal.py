import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import hashlib
import os
import pygame
import time



def playAudio(file_path: str):
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((300, 200))  
    pygame.display.set_caption('Music Player')  

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if not pygame.mixer.music.get_busy(): 
                running = False 

            screen.fill((255, 255, 255))  
        
            font = pygame.font.Font(None, 36)
            filename = os.path.basename(file_path)
            text = font.render(filename, True, (50, 50, 0))
            screen.blit(text, (10, 10)) 

            pygame.display.update()
            pygame.time.Clock().tick(60) 

    except pygame.error as e:
        print(f"Unable to play music: {e}")
    finally:
        pygame.quit()


def compareToDatabase(file: str, folderPath: str, databaseGlobal: list[dict[str, str]]) -> bool: 
    checker_hash, fileValue = spectrogramHash(file)
    isFound: bool = False
    if databaseGlobal is not None: 
        for item in databaseGlobal:
            if item['key'] == checker_hash: 
                playAudio(item['file_name'])
                playAudio(fileValue)
                print("Found a matching entry in the database:", item['file_name'])
                isFound = True
                return True

    database: list[dict[str, str]] = toDatabase(folderPath) 
    saveDatabase(databaseGlobal, database)
    for entry in database:
        if entry['key'] == checker_hash: 
            playAudio(entry['file_name'])
            playAudio(fileValue)
            print("Found a matching entry in the database:", entry['file_name'])
            return True

    print("404 not found")
    return False

def toDatabase(folder: str) -> list[dict[str, str]]: 
    files = [file for file in os.listdir(folder) if (file.endswith('.wav') or file.endswith('.mp3'))] 
    database: list[dict[str, str]] = []

    for file in files: 
        file_path: str = os.path.join(folder, file) 
        truncated_Hash, filename = spectrogramHash(file_path) 
        entry: dict[str, str] = {'key': truncated_Hash, 'file_name': filename }
        database.append(entry)
    
    return database

def saveDatabase(databaseGlobal: list[dict[str, str]], database: list[dict[str, str]]): 
    databaseGlobal.extend(database)
    writeToDatabase(databaseGlobal)

def writeToDatabase(database: list[dict[str, str]]): 
    with open('./database/data.config', 'r+') as file: 
        for item in database: 
            file.write(f"key: {item['key']}, file_name: {item['file_name']}\n")

def readDatabase(path: str) -> list[dict[str, str]]: 
    read_data = []
    with open(path, 'r+') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(', ')
            data_dict = {}
            for part in parts:
                key, value = part.split(': ')
                data_dict[key.strip()] = value.strip()
            read_data.append(data_dict)

    return read_data


def spectrogramHash(audio_file: str, keyLength: int = 100) -> dict[str, str]:
    data, _ = sf.read(audio_file)

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
    
    return truncated_Hash, audio_file

checker: str = './sample2.wav'
data_folder: str = './data/bbc'
# database: list[dict[str, str]] = toDatabase(data_folder)
# for data in database: 
#     print(data)


globalDatabase = readDatabase('./database/data.config')

if __name__ == "__main__":
    start_time = time.time() 
    result = compareToDatabase(checker, data_folder, globalDatabase)
    end_time = time.time()   

    execution_time = end_time - start_time  
    print(f"Execution time: {execution_time} seconds")