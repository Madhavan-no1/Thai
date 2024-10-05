from huggingface_hub import InferenceClient
import speech_recognition as sr
import pyttsx3
import streamlit as st
import threading

# Direct API key
API_KEY = "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"

# Initialize the Inference Client
client = InferenceClient(api_key=API_KEY)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
tts_engine = pyttsx3.init()

# Set the voice to female
voices = tts_engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break

def speak(text):
    """Convert text to speech and play it in a separate thread."""
    def run_speech():
        tts_engine.say(text)
        tts_engine.runAndWait()

    # Start the speech in a new thread
    thread = threading.Thread(target=run_speech)
    thread.start()

def listen():
    """Listen to the user's voice input and convert it to text."""
    with sr.Microphone() as source:
        st.info("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results; {e}"

def get_response(user_question):
    """Get the chat model's response to the user's question."""
    try:
        domain_prompt = (
            f"You are a knowledgeable assistant specialized in answering questions "
            f"related to pregnancy, child care, nutrition, government schemes, and "
            f"other necessary topics concerning health and well-being of mothers and children. "
            f"Please provide helpful and concise responses that are specific to these topics.\n\n"
            f"User Question: '{user_question}'"
        )

        response_stream = client.chat_completion(
            model="microsoft/Phi-3-mini-4k-instruct",
            messages=[{"role": "user", "content": domain_prompt}],
            max_tokens=4000,
            stream=True,
        )

        response = ""
        for message in response_stream:
            if 'choices' in message and message['choices']:
                choice = message['choices'][0]
                if 'delta' in choice and 'content' in choice['delta']:
                    chunk = choice['delta']['content']
                    response += chunk

        return response

    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit interface
st.title("Pregnancy & Child Care Assistant")
st.write("This assistant is specialized in answering questions about pregnancy, child care, nutrients, schemes, and other necessary dependencies.")

# Initialize the chat messages in session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display the chat flow with improved formatting
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                    f"<strong>You:</strong><br>{msg['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: #d0f0c0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                    f"<strong>Assistant:</strong><br>{msg['assistant']}</div>", unsafe_allow_html=True)

# Button to start listening
if st.button("Start Listening"):
    user_question = listen()  # Listen for user input
    if user_question:
        st.success(f"You said: {user_question}")

        # Get the response from the model
        with st.spinner("Generating response..."):
            response = get_response(user_question)

        # Speak out the response
        if response:
            speak(response)
            # Append the conversation to session state to update the chat history
            st.session_state.messages.append({"user": user_question, "assistant": response})

            # Re-render the chat flow after adding the new message
            with chat_placeholder:
                for msg in st.session_state.messages:
                    st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                                f"<strong>You:</strong><br>{msg['user']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background-color: #d0f0c0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                                f"<strong>Assistant:</strong><br>{msg['assistant']}</div>", unsafe_allow_html=True)
    else:
        st.warning("No input detected.")
