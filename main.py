
import streamlit as st
import os
import sounddevice as sd
import wavio
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

# === LOAD API KEY FROM .env ===
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Error: AI key not found. Please set GEMINI_API_KEY in .env.")
    st.stop()

genai.configure(api_key=api_key)
model_name = "gemini-1.5-flash"

# AUDIO SETTINGS
DURATION = 5
SAMPLE_RATE = 44100
AUDIO_FILE = "audio/input.wav"

def record_audio():
    st.info("🎙️ Recording for 5 seconds...")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    os.makedirs(os.path.dirname(AUDIO_FILE), exist_ok=True)
    wavio.write(AUDIO_FILE, audio_data, SAMPLE_RATE, sampwidth=2)
    st.success("✅ Recording finished!")

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            return None

def chat_with_ai(prompt):
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "Sorry, I couldn't understand that."
    except Exception as e:
        return "Sorry, an error occurred."

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    if os.name == "nt":
        os.system("start response.mp3")
    elif os.uname().sysname == "Darwin":
        os.system("afplay response.mp3")
    else:
        os.system("mpg123 response.mp3")

# Streamlit UI
st.set_page_config(page_title="Adnan's AI Voice Assistant", page_icon="🎧")
st.title("🎧 Adnan's AI Voice Assistant")

st.markdown("Speak to your assistant and hear back a smart AI reply!")

if st.button("🎤 Record and Ask"):
    record_audio()
    user_prompt = transcribe_audio()

    if user_prompt:
        st.markdown(f"**You said:** {user_prompt}")
        ai_reply = chat_with_ai(user_prompt)
        st.markdown(f"**🤖 AI says:** {ai_reply}")
        speak(ai_reply)
    else:
        st.warning("❗ Sorry, I couldn't understand your voice.")
