import sounddevice as sd
import wavio
import os
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

# === LOAD API KEY FROM .env ===
load_dotenv()  # Load .env file
api_key = os.getenv("GEMINI_API_KEY")  # Get the key securely

# --- IMPORTANT: Check if API key is loaded ---
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in your .env file.")
    print("Please create a .env file in the same directory as this script with the content:")
    print("GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY_HERE")
    exit() # Exit if API key is missing to prevent further errors

genai.configure(api_key=api_key)  # Set it in Gemini

# --- UPDATED MODEL NAME ---
# 'gemini-pro' might be deprecated or require a more specific version.
# 'gemini-1.5-flash' is a commonly available and efficient model for chat.
# If 'gemini-1.5-flash' still gives a 404, try 'gemini-1.0-pro' or 'gemini-1.5-pro'.
model_name = "gemini-1.5-flash"

# === AUDIO SETTINGS ===
DURATION = 5  # seconds
SAMPLE_RATE = 44100
AUDIO_FILE = "audio/input.wav"

def record_audio():
    print("🎤 Recording... Speak now!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    os.makedirs(os.path.dirname(AUDIO_FILE), exist_ok=True)
    wavio.write(AUDIO_FILE, audio_data, SAMPLE_RATE, sampwidth=2)
    print(f"✅ Recording saved as: {AUDIO_FILE}")

def transcribe_audio():
    print("📝 Transcribing...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"📜 Transcript: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"❌ Could not request results from Google Speech Recognition service; {e}")
            return None

def chat_with_gemini(prompt):
    print(f"🤖 Asking Gemini ({model_name})...")
    try:
        # The model is initialized here, using the global model_name
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        if response.text:
            print("🧠 Gemini says:", response.text)
            return response.text
        else:
            print("🧠 Gemini did not return any text.")
            # You can print the full response object for more debugging info if needed:
            # print("Full Gemini response object:", response)
            return "Sorry, I couldn't get a response from Gemini."
    except Exception as e:
        print(f"❌ An error occurred while chatting with Gemini:\n{e}")
        return "Sorry, I encountered an error while processing your request."

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    if os.name == "nt":
        os.system("start response.mp3")
    elif os.uname().sysname == "Darwin":
        os.system("afplay response.mp3")
    else:
        os.system("mpg123 response.mp3") # Ensure mpg123 is installed on Linux

def main():
    print("🎙️ Welcome to Gemini Voice Assistant!")
    record_audio()
    prompt = transcribe_audio()
    if prompt:
        reply = chat_with_gemini(prompt)
        speak(reply)
    else:
        print("⚠️ No valid prompt to send to Gemini.")

if __name__ == "__main__":
    main()
