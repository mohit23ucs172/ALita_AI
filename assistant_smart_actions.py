import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from dotenv import load_dotenv
load_dotenv()
import webbrowser
import datetime
import json

# --- Configuration ---
# Load API key from .env
API_KEY = os.getenv("API_KEY")

# --- Gemini Model Setup ---
genai.configure(api_key=API_KEY)

# --- PHASE 4: Define Our "Tools" (Python Functions) ---
# These are the "hands" that the AI can choose to use.

def get_current_time():
    """Gets the current time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p") # e.g., "05:32 PM"
    return f"The current time is {time_str}"

def open_google_search(search_query: str):
    """
    Opens a Google search in the web browser for a given query.
    Args:
        search_query (str): The term to search for.
    """
    url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(url)
    return f"I have opened Google and searched for {search_query}"

# --- End of Tool Definitions ---


# --- PHASE 4: Model Setup with Tools ---
system_prompt = (
    "You are my personal AI assistant. Your name is 'Jarvis'. "
    "You are witty, friendly, sarcastic but always helpful, and loyal. "
    "You are talking to your creator. Keep your responses concise. "
    "When you use a tool, briefly confirm the action before stating the result."
)

# This is the new part: We tell the model about our tools.
tools_list = [
    get_current_time,
    open_google_search,
]

model = genai.GenerativeModel(
    'models/gemini-pro-latest',  # <-- MAKE SURE THIS IS YOUR WORKING MODEL
    system_instruction=system_prompt,
    tools=tools_list  # <-- HERE IS THE UPGRADE!
)

# Start a chat session (this is different from Phase 1, it manages history automatically)
chat = model.start_chat(enable_automatic_function_calling=True)

# --- Voice Functions (Same as Phase 2/3) ---

def listen_to_user():
    """Captures audio from the microphone and converts it to text."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone(device_index=2) as source:  # <-- MAKE SURE TO USE YOUR INDEX
        print("Jarvis: Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Connection Error: {e}")
        speak("I seem to be having trouble connecting to my audio systems.")
        return None

def speak(text):
    """Converts text to speech and plays it."""
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
        audio_file = "jarvis_response.mp3"
        tts.save(audio_file)
        
        print(f"Jarvis: {text}")
        playsound(audio_file)
        os.remove(audio_file)
    except Exception as e:
        print(f"Error during speech: {e}")

# --- Main Conversation Loop (Updated for Phase 4) ---
def main():
    speak("Systems online. Core intelligence and tools are ready.")

    while True:
        # 1. Listen for user's command
        user_input = listen_to_user()
        
        if user_input:
            # 2. Check for the 'quit' command
            if "goodbye" in user_input.lower() or "quit" in user_input.lower():
                speak("Goodbye, sir.")
                break
            
            try:
                # 3. Send to Gemini (The magic happens here!)
                # We just send the text. The model decides if it's
                # a chat message OR a command to run a tool.
                # Because 'enable_automatic_function_calling=True',
                # the 'chat.send_message' will:
                #    1. See the AI wants to use a tool (e.g., get_current_time)
                #    2. AUTOMATICALLY run your Python function for you
                #    3. Send the result *back* to the AI
                #    4. Get the final, natural-language response.
                response = chat.send_message(user_input)
                
                # 4. Speak the AI's final response
                speak(response.text)
                
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                speak("Apologies, sir. I'm having a connection issue with my core.")

# --- Run the Assistant ---
if __name__ == "__main__":
    main()