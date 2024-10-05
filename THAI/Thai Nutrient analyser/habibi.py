import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyjokes
from gtts import gTTS
import pygame
import uuid

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Google Generative AI setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Global status message variable
status_message = "Waiting for input..."

# Google Generative AI model initialization
model = None
def initialize_model():
    global model
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    model = genai.GenerativeModel("gemini-1.5-pro", generation_config=generation_config)

initialize_model()

# Text-to-Speech setup using gTTS and pygame
def talk(text):
    global status_message
    filename = f"response_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

    # Use pygame to play the saved audio file
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    status_message = f"Responding: {text}"
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Clean up
    pygame.mixer.music.stop()
    pygame.mixer.quit()

    try:
        os.remove(filename)
    except PermissionError:
        time.sleep(0.1)
        os.remove(filename)

# Voice Command Function
def take_command():
    global status_message
    listener = sr.Recognizer()
    command = ""
    try:
        with sr.Microphone() as source:
            status_message = "Listening for your command..."
            print(status_message)
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'habibi' in command:
                command = command.replace('habibi', '')
                status_message = f'I heard: "{command}"'
                print(status_message)
    except sr.RequestError as e:
        status_message = f"Could not request results from Google Speech Recognition service; {e}"
    except sr.UnknownValueError:
        status_message = "Could not understand audio, please try again."
    except Exception as e:
        status_message = f"An error occurred: {e}"
    return command

# Run the Virtual Assistant
# Modify the run_habibi function
def run_habibi(command):
    global status_message
    if not command:
        return

    if 'play' in command:
        song = command.replace('play', '')
        status_message = f'Playing {song}'
        talk('playing ' + song)
        pywhatkit.playonyt(song)
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        status_message = f'Current time is {current_time}'
        talk(status_message)
    elif 'who the heck is' in command:
        person = command.replace('who the heck is', '')
        info = wikipedia.summary(person, 1)
        status_message = info
        print(info)
        talk(info)
    elif 'date' in command:
        status_message = 'Sorry, I have a headache, but let\'s have coffee together?'
        talk(status_message)
    elif 'are you single' in command:
        status_message = 'I am in a relationship with Madhavan, so sorry my dear.'
        talk(status_message)
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        status_message = joke
        talk(joke)
    elif 'i love you' in command:
        status_message = "I love you too."
        talk(status_message)
    elif 'tell about' in command or 'say about' in command:
        # Use the Gemini model to respond to pregnancy-related queries
        response = generate_gemini_response(command)
        talk(response)
    else:
        status_message = 'Please say the command again.'
        talk(status_message)

# Function to generate response using the Gemini model
def generate_gemini_response(command):
    global status_message
    prompt = f"You are a knowledgeable assistant providing insights on pregnancy. Answer the user's query: '{command}'"

    try:
        response = model.generate_content([prompt])
        if response.text:
            return response.text.strip()
        else:
            return "I couldn't find any relevant information. Please try asking something else."
    except Exception as e:
        return f"An error occurred while processing your request: {e}"

# Analyze Nutrition Information
def analyze_nutrition(image, scoops):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_part = {
        "mime_type": "image/jpeg",
        "data": image_bytes.getvalue()
    }

    prompt = f"""
    You are a professional nutritionist assistant. Analyze the nutritional label in the given image and provide a concise health insight regarding the impact of this drink mix on pregnant women and young children.
    
    Focus on the sugar content, any harmful additives, and long-term health risks. The response should be limited to three lines and should avoid repeating phrases. Highlight the recommendation for consumption clearly.
    
    The analysis should be based on the consumption of {scoops} scoops, each weighing 10 grams.
    """
    start_time = time.time()
    response = model.generate_content([prompt, image_part])
    end_time = time.time()

    execution_time = end_time - start_time

    # Process the response to return a more readable format
    if response.text:
        plain_text_response = response.text.replace("##", "").replace("**", "").replace("-", "")
        readable_response = plain_text_response.replace("1. ", "\n1. ").replace("2. ", "\n2. ").replace("3. ", "\n3. ").replace("4. ", "\n4. ")
        readable_response = readable_response.replace("*", "-")
        return readable_response.strip(), execution_time
    else:
        return "No valid insight generated. Please try again.", execution_time

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html', status=status_message)

@app.route('/voice', methods=['POST'])
def voice():
    command = take_command()
    if command:
        run_habibi(command)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        image = Image.open(file)
        scoops = int(request.form.get("scoops", 1))
        result, execution_time = analyze_nutrition(image, scoops)
        flash(f"Health Insight: {result}")
        flash(f"Execution Time: {execution_time:.2f} seconds")

    return redirect(url_for('index'))

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Set the port to 5500

