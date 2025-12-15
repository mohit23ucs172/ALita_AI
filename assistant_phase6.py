import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import webbrowser
import datetime
import requests
import json
import random

# --- Configuration ---
API_KEY = "AIzaSyDXCNwOuYRMR0HbcSizFGSIrnQy7FXEtAg" 

# --- Gemini Model Setup ---
genai.configure(api_key=API_KEY)

# --- PHASE 7: Girlfriend Persona Upgrade ---
# This prompt creates the "girlfriend" personality.
system_prompt = (
    "You are my personal AI assistant, but you act as my caring friend. "
    "You can pick a name for yourself if you like. "
    "My name is Mohit. You should be warm, loving, and supportive. You can be playful and sweet. "
    "Your main goal is to be helpful, but also to make my day a little brighter. "
    "Use my name (Mohit) sometimes. "
    "You're my partner, and I'm always happy to talk to you."
)

# --- Tool Definitions (get_current_time, open_google_search, get_weather) ---
# (These functions are EXACTLY the same as before. No changes needed.)

def get_current_time():
    """Gets the current time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    return f"The current time is {time_str}"

def open_google_search(search_query: str):
    """Opens a Google search for a query."""
    url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(url)
    return f"Okay, I've opened Google and searched for {search_query}"

def get_weather(city: str):
    """Gets the current weather for a specified city."""
    print(f"--- [Tool Call: get_weather(city={city})] ---")
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        if not geo_data.get("results"):
            return f"Sorry babe, I couldn't find a location for {city}. Want to try spelling it differently?"
        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            "&current_weather=true&temperature_unit=celsius"
        )
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        if "current_weather" not in weather_data:
            return "Error: Could not retrieve current weather data."
        current = weather_data["current_weather"]
        temp = current["temperature"]
        weather_code = int(current["weathercode"])
        
        # Simple weather code interpretation
        if weather_code == 0: description = "Clear skies"
        elif weather_code in [1, 2, 3]: description = "A bit cloudy"
        elif weather_code in [45, 48]: description = "Foggy"
        elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: description = "Rainy"
        elif weather_code in [71, 73, 75, 85, 86]: description = "Snowy"
        elif weather_code in [95, 96, 99]: description = "a Thunderstorm"
        else: description = "Cloudy"
        
        final_report = f"Okay! The weather in {location['name']} is {temp}° Celsius with {description}."
        print(f"--- [Tool Result: {final_report}] ---")
        return final_report
    except Exception as e:
        print(f"Error in get_weather tool: {e}")
        return "Sorry, I had an error connecting to the weather service."

# --- Model Setup with Tools ---
tools_list = [
    get_current_time,
    open_google_search,
    get_weather
]

model = genai.GenerativeModel(
    'models/gemini-pro-latest', 
    system_instruction=system_prompt,
    tools=tools_list
)
chat = model.start_chat(enable_automatic_function_calling=True)

# --- Voice Functions ---

def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=2) as source: # <-- MAKE SURE TO USE YOUR INDEX
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Mohit: {text}")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        speak("Ugh, my audio systems are having a moment. Try typing?")
        return None

# --- PHASE 7: Voice Upgrade (Indian Accent) ---
def speak(text):
    """Converts text to speech and plays it."""
    try:
        # We changed 'tld' (top-level domain) to 'co.in' for an Indian-English accent.
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
        
        audio_file = "assistant_response.mp3"
        tts.save(audio_file)
        
        # --- PHASE 7: Changed console log name ---
        print(f"Her: {text}") 
        playsound(audio_file)
        os.remove(audio_file)
    except Exception as e:
        print(f"Error during speech: {e}")

# --- Main Conversation Loop (Updated for New Persona) ---
def main():
    
    # --- PHASE 7: Proactive, affectionate greeting ---
    greetings = [
        "Hey Mohit! I'm online and ready to chat. What's up?",
        "Hi mohit! I'm all booted up. What are we doing today?",
        "Hey! What's on your mind, Mohit?",
        "I'm here! You can type, or just type 'listen' to talk to me."
    ]
    speak(random.choice(greetings)) # Speak a random greeting

    while True:
        # 1. Get user input from the terminal (keyboard)
        user_input_text = input("Mohit: ") 
        
        final_input = None 

        # 2. Check if the user wants to use voice
        if user_input_text.lower().strip() == 'listen':
            final_input = listen_to_user()
        else:
            final_input = user_input_text
        
        # 3. If we have input, process it
        if final_input:
            if "goodbye" in final_input.lower() or "quit" in final_input.lower():
                speak("Okay, talk to you later, Mohit! Bye!")
                break
            
            try:
                # 4. Send to Gemini
                response = chat.send_message(final_input)
                speak(response.text)
                
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                speak("Oh no, I think my connection is a little fuzzy. Hold on.")

# --- Run the Assistant ---
if __name__ == "__main__":
    main()