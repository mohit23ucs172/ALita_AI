import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# Load API key from .env
API_KEY = os.getenv("API_KEY")

# --- Gemini Model Setup ---
genai.configure(api_key=API_KEY)

system_prompt = (
    "You are my personal AI assistant. Your name is 'Jarvis'. "
    "You are witty, friendly, sarcastic but always helpful, and loyal. "
    "You are talking to your creator. Keep your responses concise and "
    "like a real conversation."
)

# !! IMPORTANT: Use the model name that worked for you in Phase 1 !!
# (e.g., 'models/gemini-pro-latest')
model = genai.GenerativeModel(
    'models/gemini-pro-latest',  # <-- MAKE SURE THIS IS YOUR WORKING MODEL
    system_instruction=system_prompt
)

# Start a chat session
chat = model.start_chat(history=[])

# --- Voice Functions ---

def listen_to_user():
    """Captures audio from the microphone and converts it to text."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Jarvis: Listening...")
        # Adjust for ambient noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        # Use Google's web speech API to recognize the audio
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        # This error means the recognizer couldn't understand the audio
        speak("My apologies, sir, I didn't quite catch that.")
        return None
    except sr.RequestError as e:
        # This error means it couldn't connect to Google's service
        print(f"Connection Error: {e}")
        speak("I seem to be having trouble connecting to my audio systems.")
        return None

def speak(text):
    """Converts text to speech and plays it."""
    try:
        # Create the text-to-speech object
        tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
        
        # Save the audio to a temporary file
        audio_file = "jarvis_response.mp3"
        tts.save(audio_file)
        
        # Print what Jarvis is saying
        print(f"Jarvis: {text}")
        
        # Play the audio file
        playsound(audio_file)
        
        # Clean up by removing the file
        os.remove(audio_file)
        
    except Exception as e:
        print(f"Error during speech: {e}")

# --- Main Conversation Loop ---
def main():
    speak("System online. How can I help you, sir?")

    while True:
        # 1. Listen for user's command
        user_input = listen_to_user()
        
        # 2. If we got input, process it
        if user_input:
            # 3. Check for the 'quit' command
            if "goodbye" in user_input.lower() or "quit" in user_input.lower():
                speak("Goodbye, sir.")
                break
                
            try:
                # 4. Send the user's text to the Gemini "brain"
                response = chat.send_message(user_input)
                
                # 5. Speak the AI's response
                speak(response.text)
                
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                speak("Apologies, sir. I'm having a connection issue with my core.")

# --- Run the Assistant ---
if __name__ == "__main__":
    main()