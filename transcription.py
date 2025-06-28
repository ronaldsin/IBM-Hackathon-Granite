import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
API_URL = os.getenv("IBM_API_URL")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

print("Testing API URL...")

import requests

API_URL = ""

try:
    r = requests.get(API_URL)
    print(f"GET {API_URL} => Status {r.status_code}")
    print(r.text)
except Exception as e:
    print("Error:", e)

# def transcribe_audio(file_path):
#     endpoint = f"{API_URL}/genai/v1/projects/{PROJECT_ID}/speech-to-text"
#     headers = {
#         "Content-Type": "audio/wav",
#         "Authorization": f"Bearer {API_KEY}",
#     }

#     with open(file_path, "rb") as f:
#         audio_data = f.read()

#     response = requests.post(endpoint, headers=headers, data=audio_data)

#     if response.status_code == 200:
#         result = response.json()
#         transcripts = []
#         for res in result.get("results", []):
#             for alt in res.get("alternatives", []):
#                 transcripts.append(alt.get("transcript", ""))
#         transcription = " ".join(transcripts)
#         print("Transcription:")
#         print(transcription)
#         return transcription
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None

# if __name__ == "__main__":
#     wav_file_path = r"C:\Users\David\Documents\GitHub\IBM-Hackathon-Granite\audio\converted_k.wav"
#     transcribe_audio(wav_file_path)
