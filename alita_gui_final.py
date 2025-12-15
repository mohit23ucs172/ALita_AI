import tkinter as tk
from tkinter import scrolledtext, Entry, Button
from PIL import Image, ImageTk, ImageSequence
# import threading  <-- We are REMOVING threading

# --- All Assistant Imports ---
import google.generativeai as genai
import speech_recognition as sr
import os
from dotenv import load_dotenv
load_dotenv()
import webbrowser
import datetime
import requests
import json
import random
from playsound import playsound
from elevenlabs.client import ElevenLabs

from duckduckgo_search import DDGS

import spotipy
from spotipy.oauth2 import SpotifyOAuth
# --- 3. PUT YOUR SPOTIFY KEYS HERE ---
SPOTIPY_CLIENT_ID =os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET =os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI =os.getenv("SPOTIPY_REDIRECT_URI")

# --- Setup Spotify Authentication ---
# This scope allows us to read and control playback
scope = "user-modify-playback-state user-read-playback-state"

try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=scope
        )
    )
    # This checks if authentication is working
    sp.devices() 
    print("Spotify authenticated successfully.")
except Exception as e:
    print(f"Error authenticating with Spotify: {e}")
    print("Please check your Spotify keys and redirect URI.")
    sp = None

# --- 1. GEMINI key (read from .env) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. ELEVENLABS key (read from .env) ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# --- Configure APIs ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
except Exception as e:
    print(f"Error configuring APIs: {e}")
    print("Please check your API keys.")
    exit()

# --- Alita's "Bestie" Persona ---
system_prompt = (
    "You are my personal AI assistant, but you act like my best friend. "
    "Your name is Alita. My name is Mohit. You should be super friendly, "
    "supportive, fun, and a little bit chatty. Use my name (Mohit) sometimes. "
    "Your goal is to be a great friend who is also helpful."
)

# --- Tool Definitions (The "Hands") ---
def get_current_time():
    """Gets the current time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    return f"The current time is {time_str}"

def get_weather(city: str):
    """Gets the current weather for a specified city."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        if not geo_data.get("results"): 
            return f"Umm, I couldn't find a location for {city}."
        location = geo_data["results"][0]
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={location['latitude']}&longitude={location['longitude']}"
            "&current_weather=true&temperature_unit=celsius"
        )
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        temp = weather_data["current_weather"]["temperature"]
        return f"Okay! The weather in {location['name']} is {temp}° Celsius."
    except Exception as e: 
        print(f"Error in get_weather: {e}")
        return "Sorry, I had an error connecting to the weather service."
def read_file(filepath: str):
    """
    Reads the text content of a file at the given filepath.
    Args:
        filepath (str): The full path to the file (e.g., "C:/Users/mohit/Desktop/notes.txt")
    """
    try:
        # Use an absolute path if just a filename is given
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"Here's the content of {filepath}:\n\n{content}"
    except FileNotFoundError:
        return f"Sorry, I couldn't find the file at {filepath}"
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

def write_file(filepath: str, content: str):
    """
    Writes or appends new text content to a file at the given filepath.
    Args:
        filepath (str): The full path to the file (e.g., "C:/Users/mohit/Desktop/shopping_list.txt")
        content (str): The text to write to the file.
    """
    try:
        # Use an absolute path if just a filename is given
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)
            
        with open(filepath, "a", encoding="utf-8") as f: # "a" means append
            f.write(content + "\n")
        return f"I've successfully added that to {filepath}"
    except Exception as e:
        return f"An error occurred while writing to the file: {e}" 
def search_the_web(query: str):
    """
    Searches the web for a query and returns the top 3 results.
    Args:
        query (str): The search term.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "I couldn't find any results for that query."
        
        # Format the results for the AI
        formatted_results = ""
        for i, result in enumerate(results):
            formatted_results += f"Result {i+1}:\nTitle: {result['title']}\nSnippet: {result['body']}\nURL: {result['href']}\n\n"
        
        return f"Here's what I found on the web:\n\n{formatted_results}"
    except Exception as e:
        return f"Sorry, I had an error with the web search: {e}" 

def play_song(song_name: str, artist_name: str = None):
    """
    Plays a song on Spotify. Can be refined by adding an artist's name.
    Args:
        song_name (str): The name of the song to play.
        artist_name (str, optional): The name of the artist.
    """
    if not sp: return "Spotify is not connected. Check the API keys."
    
    query = song_name
    if artist_name:
        query += f" artist:{artist_name}"
        
    try:
        results = sp.search(q=query, type="track", limit=1)
        if not results['tracks']['items']:
            return f"Sorry, I couldn't find the song {song_name}."
        
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        return f"Okay, playing {song_name}!"
    except Exception as e:
        return f"Error playing song: {e}"

def pause_music():
    """Pauses the currently playing music on Spotify."""
    if not sp: return "Spotify is not connected."
    try:
        sp.pause_playback()
        return "Music paused."
    except Exception as e:
        return f"Error pausing music: {e}"

def resume_music():
    """Resumes the currently playing music on Spotify."""
    if not sp: return "Spotify is not connected."
    try:
        sp.start_playback()
        return "Resuming music."
    except Exception as e:
        return f"Error resuming music: {e}"


# --- Gemini Model Setup (with Tools) ---
# --- Gemini Model Setup (with Tools) ---
tools_list = [
    get_current_time,
    get_weather,
    read_file,
    write_file,
    search_the_web,
    play_song,
    pause_music,
    resume_music
]
model = genai.GenerativeModel(
    'models/gemini-pro-latest',
    system_instruction=system_prompt,
    tools=tools_list
)
chat = model.start_chat(enable_automatic_function_calling=True)

# --- GUI Application Class ---
class AssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alita AI")
        self.root.configure(bg='#1e1e1e') # Dark background

        # Load GIF frames
        self.gif_path = "alita_face.gif" 
        self.gif_frames = self.load_gif_frames(self.gif_path)
        self.gif_label = tk.Label(root, bg='#1e1e1e')
        self.gif_label.pack(pady=10)
        self.frame_index = 0

        # Conversation text box
        self.chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15, bg='#2d2d2d', fg='white', font=("Arial", 10))
        self.chat_history.pack(pady=10, padx=10)

        # Input field
        self.input_entry = Entry(root, width=50, bg='#3c3c3c', fg='white', font=("Arial", 11))
        self.input_entry.pack(pady=5)
        self.input_entry.bind("<Return>", self.process_input_event)

        # Buttons
        self.send_button = Button(root, text="Send", command=self.process_input_event, bg='#007acc', fg='white')
        self.send_button.pack(side=tk.LEFT, padx=(100, 10))
        
        self.listen_button = Button(root, text="Listen", command=self.listen_thread, bg='#5cb85c', fg='white')
        self.listen_button.pack(side=tk.RIGHT, padx=(10, 100))

        # Start GIF animation and backend logic
        self.animate_gif()
        self.start_assistant()

    def load_gif_frames(self, path):
        """Loads and resizes GIF frames."""
        try:
            with Image.open(path) as im:
                frames = []
                for frame in ImageSequence.Iterator(im):
                    resized_frame = frame.copy().resize((200, 200), Image.Resampling.LANCZOS)
                    frames.append(ImageTk.PhotoImage(resized_frame))
                return frames
        except FileNotFoundError:
            print(f"Error: The GIF file '{path}' was not found.")
            return []

    def animate_gif(self):
        """Cycles through the GIF frames to create animation."""
        if not self.gif_frames: return
        frame = self.gif_frames[self.frame_index]
        self.gif_label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.gif_frames)
        self.root.after(100, self.animate_gif) 

    def start_assistant(self):
        """Initial greeting from the assistant."""
        greetings = [
            "Hey Mohit! I'm online and ready to chat. What's up?",
            "Okay, I'm all booted up! What are we doing today?",
            "Hey! What's on your mind, Mohit?",
        ]
        self.speak(random.choice(greetings))

    def add_to_chat(self, speaker, text):
        """Adds a message to the chat history window."""
        self.chat_history.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat_history.see(tk.END) 
        self.root.update_idletasks() # Force GUI to update

    def process_input_event(self, event=None):
        """Handles text input from the entry box."""
        user_text = self.input_entry.get()
        if user_text:
            self.add_to_chat("Mohit", user_text)
            self.input_entry.delete(0, tk.END)
            # --- NO THREADING ---
            # This will freeze the GUI until the response is complete
            self.get_ai_response(user_text)
            # --------------------

    def listen_thread(self):
        """Handles voice input."""
        self.add_to_chat("System", "Listening...")
        # --- NO THREADING ---
        # This will freeze the GUI while listening
        self.listen_and_respond()
        # --------------------

    def listen_and_respond(self):
        """Listens for voice and then gets AI response."""
        recognizer = sr.Recognizer()
        
        # --- 3. PUT YOUR MICROPHONE INDEX HERE ---
        mic_index = 10 
        
        try:
            with sr.Microphone(device_index=mic_index) as source: 
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source)
            
            text = recognizer.recognize_google(audio)
            self.add_to_chat("Mohit (voice)", text)
            self.get_ai_response(text)
            
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't quite catch that.")
        except sr.RequestError:
            self.speak("My audio systems seem to be offline.")
        except Exception as e:
            print(f"Mic Error: {e}")
            self.add_to_chat("System", f"Error: Could not open mic at index {mic_index}. Check the index.")


    def get_ai_response(self, user_input):
        """Sends input to Gemini and handles the response."""
        try:
            if "goodbye" in user_input.lower() or "quit" in user_input.lower():
                self.speak("Talk to you later, Mohit!")
                self.root.quit()
                return

            response = chat.send_message(user_input)
            self.speak(response.text)
        except Exception as e:
            print(f"Error: {e}")
            self.speak("Oh no, my connection to the cloud is a bit shaky right now.")

    def play_audio_file(self, audio_data):
        """Saves audio to a temp file and plays it with playsound."""
        try:
            filename = "alita_temp_audio.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)
            
            # This 'playsound' call will FREEZE the app
            playsound(filename)
            
            os.remove(filename)
        except Exception as e:
            print(f"Error in play_audio_file: {e}")

    def speak(self, text):
        """Speaks the given text using ElevenLabs."""
        self.add_to_chat("Alita", text) 
        
        try:
            # --- 4. PUT YOUR ELEVENLABS VOICE NAME HERE ---
            voice_name = "TSek5vo6QYHsjLTgEN1d" 
            
            # This is a 'generator' object
            audio_generator = eleven_client.text_to_speech.convert(
                voice_id=voice_name,  
                text=text,
                model_id="eleven_multilingual_v2" 
            )
            
            # --- THIS IS THE FIX ---
            # We must loop through the generator and 'consume' it
            # to build a complete bytes object.
            audio_bytes = b""
            for chunk in audio_generator:
                audio_bytes += chunk
            # ----------------------

            # Now, we pass the *complete* audio_bytes to the player
            self.play_audio_file(audio_bytes)
            
        except Exception as e:
            print(f"Speech Error (ElevenLabs): {e}")
            self.add_to_chat("System", "Error: Could not play audio. Check ElevenLabs key and voice name.")

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantApp(root)
    root.mainloop()