import requests
from pydub import AudioSegment
import os

def convert_to_wav(filename):
    
    folder = r"C:\Users\David\Documents\GitHub\IBM-Hackathon-Granite\audio"
    
    
    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    
    output_path = os.path.join(folder, "converted.wav")
    audio.export(output_path, format="wav")
    
    print(f"Converted and saved to: {output_path}")
    return output_path
def convert_mp3_to_wav(input_file, output_file):
    try:
        # Load the MP3 file
        audio = AudioSegment.from_file(input_file, format="mp3")
        # Export as WAV
        audio.export(output_file, format="wav")
        print(f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    input_mp3 = r"C:\Users\David\Documents\GitHub\IBM-Hackathon-Granite\audio\k.mp3"
    output_wav = r"C:\Users\David\Documents\GitHub\IBM-Hackathon-Granite\audio\converted_k.wav"

    if not os.path.exists(input_mp3):
        print(f"Input file does not exist: {input_mp3}")
    else:
        convert_mp3_to_wav(input_mp3, output_wav)

