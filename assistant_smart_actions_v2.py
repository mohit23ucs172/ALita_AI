import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from dotenv import load_dotenv
load_dotenv()
import webbrowser
import datetime

# --- PHASE 5: NEW IMPORTS ---
import requests
import json
# ------------------------------


# --- Configuration ---
# Load API key from .env
API_KEY = os.getenv("API_KEY")

# --- Gemini Model Setup ---
genai.configure(api_key=API_KEY)

# --- PHASE 5: Define Our "Tools" (Python Functions) ---

def get_current_time():
    """Gets the current time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
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

# --- THIS IS THE NEW WEATHER TOOL ---
def get_weather(city: str):
    """
    Gets the current weather for a specified city.
    Args:
        city (str): The name of the city (e.g., "New Delhi", "Tokyo").
    """
    print(f"--- [Tool Call: get_weather(city={city})] ---")
    try:
        # Step 1: Geocoding (Convert city name to lat/lon)
        # We use Open-Meteo's geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return f"I could not find the location for {city}. Please try again."
            
        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        
        # Step 2: Get Weather (Use lat/lon to get weather)
        # We use Open-Meteo's forecast API
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
        
        # Simple interpretation of weather codes (you can expand this)
        if weather_code == 0:
            description = "Clear sky"
        elif weather_code in [1, 2, 3]:
            description = "Mainly clear to partly cloudy"
        elif weather_code in [45, 48]:
            description = "Foggy"
        elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            description = "Rainy"
        elif weather_code in [71, 73, 75, 85, 86]:
            description = "Snowy"
        elif weather_code in [95, 96, 99]:
            description = "a Thunderstorm"
        else:
            description = "Cloudy"
        
        # Format the final string
        final_report = f"The current weather in {location['name']} is {temp}° Celsius with {description}."
        print(f"--- [Tool Result: {final_report}] ---")
        return final_report

    except Exception as e:
        print(f"Error in get_weather tool: {e}")
        return "Sorry, I had an error connecting to the weather service."

# --- End of Tool Definitions ---


# --- PHASE 4: Model Setup with Tools ---
system_prompt = (
    "You are my personal AI assistant. Your name is 'Jarvis'. "
    "You are witty, friendly, sarcastic but always helpful, and loyal. "
    "You are talking to your creator. Keep your responses concise. "
    "When you use a tool, briefly confirm the action before stating the result."
)

# --- ADD THE NEW TOOL TO THE LIST ---
tools_list = [
    get_current_time,
    open_google_search,
    get_weather  # <-- THE NEW TOOL IS ADDED HERE
]

model = genai.GenerativeModel(
    'models/gemini-pro-latest',  # <-- MAKE SURE THIS IS YOUR WORKING MODEL
    system_instruction=system_prompt,
    tools=tools_list
)

chat = model.start_chat(enable_automatic_function_calling=True)

# --- Voice Functions (Same as before) ---

def listen_to_user():
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
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
        audio_file = "jarvis_response.mp3"
        tts.save(audio_file)
        print(f"Jarvis: {text}")
        playsound(audio_file)
        os.remove(audio_file)
    except Exception as e:
        print(f"Error during speech: {e}")

# --- Main Conversation Loop (Updated for Text and Voice) ---
def main():
    # Updated greeting
    speak("Systems online. You can type your command, or type 'listen' to use voice.")

    while True:
        # 1. Get user input from the terminal (keyboard)
        user_input_text = input("You: ")
        
        final_input = None # Variable to hold the command

        # 2. Check if the user wants to use voice
        if user_input_text.lower().strip() == 'listen':
            # If they type 'listen', activate the microphone
            final_input = listen_to_user()
        else:
            # Otherwise, just use the text they typed
            final_input = user_input_text
        
        # 3. If we have input (from either source), process it
        if final_input:
            # 4. Check for the 'quit' command
            if "goodbye" in final_input.lower() or "quit" in final_input.lower():
                speak("Goodbye, sir.")
                break
            
            try:
                # 5. Send the final input (text or speech) to Gemini
                response = chat.send_message(final_input)
                
                # 6. Speak the AI's response
                speak(response.text)
                
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                speak("Apologies, sir. I'm having a connection issue with my core.")

# --- Run the Assistant ---
if __name__ == "__main__":
    main()