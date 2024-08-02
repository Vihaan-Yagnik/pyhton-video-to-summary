import os
import moviepy.editor as mp
import speech_recognition as sr

import google.generativeai as genai

from flask import Flask,jsonify

from dotenv import load_dotenv
import os

api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

prompt="""You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """
transcript = ""
uid = 0

promptQuestion = """From the given text generate a random question : """
promptOpt = """ : using the above paragraph Create 4 options for this question and give option : """
promptCorrect = """ : using the above paragraph tell the correct option of this question make sure to only give option number and option value :"""
question = ""
option = ""

def generate_gemini_content(transcript_text, promptQuestion):
    global question
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(promptQuestion + transcript_text)
    question = response.text
    return response.text 

def option_generator(prompOpt , question , text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text + promptOpt + question)
    option = response.text
    return response.text 

def correct_generator(option , question , text , promtCorrect):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text + promptCorrect + question +"\nhere are the options " + option)
    return response.text 

def question_generator(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text 

def video_to_text(video_path):
    global uid
    global text
    try:
        if not os.path.isfile(video_path):
            raise FileNotFoundError("Input video file not found.")
        
        # Extract audio from video
        video_clip = mp.VideoFileClip(video_path)
        audio_clip = video_clip.audio
        uid = uid + 1
        lcl_uid = uid
        audio_clip.write_audiofile(f"temp_audio${uid}.wav", codec='pcm_s16le')
        audio_clip.close()
        video_clip.close()

        # Perform speech recognition
        recognizer = sr.Recognizer()
        
        # while uid != 0:
        with sr.AudioFile(f"temp_audio${uid}.wav") as source:
            audio_data = recognizer.record(source)
            print("got audio")
            text = recognizer.recognize_google(audio_data)
            print("got text")
        
        os.remove(f"temp_audio${lcl_uid}.wav")  # Remove temporary audio file
        # uid = uid - 1
        return text
    except FileNotFoundError as e:
        print("Error:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def generate_quiz():
    quiz = [
        {
            "question": question_generator(text, promptQuestion),
            "options": option_generator(promptOpt , question, text),
            "correct_option": correct_generator(option,question,text,promptCorrect)
        }
    ]
    return quiz

app = Flask(__name__)

@app.route('/<filepath>')
def abc(filepath):
    text = video_to_text('Video/'+filepath)
    data = generate_gemini_content(text,prompt)
    # data = generate_quiz()
    return jsonify({ 'data': data })


if(__name__ == '__main__'):
    app.run(host='0.0.0.0')

