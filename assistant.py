import google.generativeai as genai
import os

# --- Configuration ---
# PASTE YOUR API KEY HERE.
# (A more secure way is to use environment variables, 
# but this is the simplest way to start.)
API_KEY = "AIzaSyDXCNwOuYRMR0HbcSizFGSIrnQy7FXEtAg" 

genai.configure(api_key=API_KEY)

# --- The "Personality" Prompt ---
# This is where you tell the AI how to act.
system_prompt = (
    "You are my personal AI assistant. Your name is 'Jarvis'. "
    "You are witty, friendly, sarcastic but always helpful, and loyal. "
    "You are talking to your creator. Keep your responses concise and "
    "like a real conversation."
)

# --- Model Setup ---
# We tell the model to use our system_prompt as its base instructions

# --- Model Setup ---
# We tell the model to use our system_prompt as its base instructions
model = genai.GenerativeModel(
    'models/gemini-pro-latest',  # <-- Use this name from your list
    system_instruction=system_prompt
)

# --- The Conversation Loop ---
print("Jarvis: System online. How can I help you?")

# Start a chat session that will remember the history
chat = model.start_chat(history=[])

while True:
    # 1. Get user input from the terminal
    user_input = input("You: ")
    
    # 2. Check if the user wants to quit
    if user_input.lower() == 'quit':
        print("Jarvis: Goodbye, sir.")
        break
    
    try:
        # 3. Send the user's message to the API
        response = chat.send_message(user_input)
        
        # 4. Print the AI's response
        print(f"Jarvis: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Jarvis: Apologies, sir. I seem to be having a connection issue.")