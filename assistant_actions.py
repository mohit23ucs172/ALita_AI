import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from dotenv import load_dotenv
load_dotenv()

# --- PHASE 3: NEW IMPORTS ---
import webbrowser
import datetime
# ------------------------------

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

# !! IMPORTANT: Use the model name that worked for you !!
model = genai.GenerativeModel(
    'models/gemini-pro-latest',  # <-- MAKE SURE THIS IS YOUR WORKING MODEL
    system_instruction=system_prompt
)
chat = model.start_chat(history=[])

# --- Voice Functions (Same as Phase 2) ---

def listen_to_user():
    """Captures audio from the microphone and converts it to text."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone(device_index=2) as source: # You can add (device_index=X) here if needed
        print("Jarvis: Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        # speak("My apologies, sir, I didn't quite catch that.") # We'll let the main loop be silent
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


# --- Main Conversation Loop (Updated for Phase 3) ---
def main():
    speak("System online. Actions and core intelligence are ready.")

    while True:
        # 1. Listen for user's command
        user_input = listen_to_user()
        
        # 2. If we got input, process it
        if user_input:
            
            # --- START OF PHASE 3 ACTION BLOCK ---
            # These 'if/elif' statements are the "hands."
            # They check for local commands first.

            # Command 1: Exit
            if "goodbye" in user_input.lower() or "quit" in user_input.lower():
                speak("Goodbye, sir.")
                break
            
            # Command 2: Get the Time
            elif "what's the time" in user_input.lower() or "what time is it" in user_input.lower():
                now = datetime.datetime.now()
                time_str = now.strftime("%I:%M %p") # e.g., "05:32 PM"
                speak(f"Sir, the current time is {time_str}")
            
            # Command 3: Get the Date
            elif "what's the date" in user_input.lower() or "date is it" in user_input.lower():
                now = datetime.datetime.now()
                date_str = now.strftime("%A, %B %d") # e.g., "Friday, November 07"
                speak(f"Today is {date_str}")
            
            # Command 4: Open a website (simple)
            elif "open google" in user_input.lower():
                speak("Opening Google, sir.")
                webbrowser.open("https://www.google.com")
            
            # Command 5: Open a website (advanced, with search)
            elif "search for" in user_input.lower():
                # This splits the string, e.g., "search for cats" -> "cats"
                search_term = user_input.lower().split("search for")[-1].strip()
                if search_term:
                    speak(f"Searching Google for {search_term}")
                    webbrowser.open(f"https://www.google.com/search?q={search_term}")
                else:
                    speak("What would you like me to search for?")

            # Command 6: Open an Application (Example: VS Code)
            elif "open my code editor" in user_input.lower() or "open code" in user_input.lower():
                speak("Opening Visual Studio Code.")
                # This command depends on your OS and if 'code' is in your PATH
                # For Windows, you might use: os.system("code")
                # For macOS: os.system("open -a 'Visual Studio Code'")
                # For Linux: os.system("code")
                try:
                    os.system("code") 
                except Exception as e:
                    speak(f"Apologies, I couldn't open the editor. Error: {e}")

            # --- END OF ACTION BLOCK ---

            # 7. If no local command matched, send it to the Gemini "brain"
            else:
                try:
                    # Send the user's text to the Gemini "brain"
                    response = chat.send_message(user_input)
                    
                    # Speak the AI's response
                    speak(response.text)
                    
                except Exception as e:
                    # Handle API errors (like quota)
                    print(f"Error with Gemini API: {e}")
                    # Don't speak, just print to avoid a loop if TTS fails
                    print("Jarvis: Apologies, sir. Connection issue with my core.")

# --- Run the Assistant ---
if __name__ == "__main__":
    main()