import os
import moviepy.editor as mp
import speech_recognition as sr

import google.generativeai as genai
from dotenv import load_dotenv
import os

api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

prompt="""You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """
transcript = ""

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text 


def video_to_text(video_path):
    try:
        if not os.path.isfile(video_path):
            raise FileNotFoundError("Input video file not found.")
        
        # Extract audio from video
        video_clip = mp.VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile("temp_audio.wav", codec='pcm_s16le')
        audio_clip.close()
        video_clip.close()

        # Perform speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio_data = recognizer.record(source)
            print("got audio")
            text = recognizer.recognize_google(audio_data)
            print("got text")
        os.remove("temp_audio.wav")  # Remove temporary audio file

        return text
    except FileNotFoundError as e:
        print("Error:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

if __name__ == "__main__":
    video_path = "./Video/demo2.mp4"  # Change this to your input video file path
    text = video_to_text(video_path)
    if text:
        print("Transcribed text:")
        transcript = text
        summary = generate_gemini_content(transcript,prompt)



