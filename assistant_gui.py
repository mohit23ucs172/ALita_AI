import tkinter as tk
from tkinter import scrolledtext, Entry, Button
from PIL import Image, ImageTk, ImageSequence
import threading
import io

# --- All your previous imports ---
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
# WARNING: Your previous key was exposed. Please generate a new one.
API_KEY = "AIzaSyDXCNwOuYRMR0HbcSizFGSIrnQy7FXEtAg"

# --- Gemini Model & Persona Setup ---
genai.configure(api_key=API_KEY)

system_prompt = (
    "You are my personal AI assistant, but you act like my best friend. "
    "Your name is Alita. My name is Mohit. You should be super friendly, "
    "supportive, fun, and a little bit chatty. Use my name (Mohit) sometimes. "
    "Your goal is to be a great friend who is also helpful."
)

# --- Tool Definitions (get_current_time, get_weather, etc.) ---
# (These are the same functions from before. No changes.)
def get_current_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    return f"The current time is {time_str}"

def get_weather(city: str):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        if not geo_data.get("results"): return f"Umm, I couldn't find a location for {city}."
        location = geo_data["results"][0]
        weather_url = (f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current_weather=true&temperature_unit=celsius")
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        temp = weather_data["current_weather"]["temperature"]
        return f"Okay! The weather in {location['name']} is {temp}° Celsius."
    except Exception as e: return "Sorry, I had an error connecting to the weather service."

tools_list = [get_current_time, get_weather]

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
        self.gif_path = "alita_face.gif" # Make sure this file is in the same folder
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
                    # Resize frames for display
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
        self.root.after(100, self.animate_gif) # Update every 100ms

    def start_assistant(self):
        """Initial greeting from the assistant."""
        self.speak("Systems online. It's great to see you, Mohit!")

    def add_to_chat(self, speaker, text):
        """Adds a message to the chat history window."""
        self.chat_history.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat_history.see(tk.END) # Auto-scroll

    def process_input_event(self, event=None):
        """Handles text input from the entry box."""
        user_text = self.input_entry.get()
        if user_text:
            self.add_to_chat("Mohit", user_text)
            self.input_entry.delete(0, tk.END)
            # Run the AI response in a separate thread to not freeze the GUI
            threading.Thread(target=self.get_ai_response, args=(user_text,)).start()

    def listen_thread(self):
        """Handles voice input in a separate thread."""
        self.add_to_chat("System", "Listening...")
        threading.Thread(target=self.listen_and_respond).start()

    def listen_and_respond(self):
        """Listens for voice and then gets AI response."""
        recognizer = sr.Recognizer()
        # --- CHANGE THE INDEX HERE ---
        with sr.Microphone(device_index=2) as source: # Let's try 10
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            self.add_to_chat("Mohit (voice)", text)
            self.get_ai_response(text)
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            self.speak("My audio systems seem to be offline.")

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

    def speak(self, text):
        """Speaks the given text using gTTS."""
        self.add_to_chat("Alita", text)
        try:
            tts = gTTS(text=text, lang='en', tld='com.au')
            audio_file = "alita_response.mp3"
            tts.save(audio_file)
            playsound(audio_file)
            os.remove(audio_file)
        except Exception as e:
            print(f"Speech Error: {e}")

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantApp(root)
    root.mainloop()