# This is the file: check_models.py
import google.generativeai as genai
import os

# --- PASTE YOUR API KEY HERE ---
API_KEY = "AIzaSyDXCNwOuYRMR0HbcSizFGSIrnQy7FXEtAg"

genai.configure(api_key=API_KEY)

print("Attempting to connect and list available models...")

try:
    # This loop asks Google "What models can I use?"
    found_model = False
    for m in genai.list_models():
        # We are looking for models that can "generateContent"
        if 'generateContent' in m.supported_generation_methods:
            print(f"Found usable model: {m.name}")
            found_model = True

    if not found_model:
        print("\n--- No usable models found ---")
        print("This might mean your API key is restricted or billing is not enabled for your project.")

except Exception as e:
    print("\n--- A critical error occurred ---")
    print(f"Error details: {e}")
    print("\nThis usually means your API Key is invalid or the API is not enabled in your project.")