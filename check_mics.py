import speech_recognition as sr

print("Listing all available microphones...")
print("-----------------------------------")

mic_list = sr.Microphone.list_microphone_names()

if not mic_list:
    print("ERROR: No microphones found. Is PyAudio installed correctly?")
else:
    for index, name in enumerate(mic_list):
        print(f"Microphone at index {index}: {name}")
    print("\nFind your microphone in the list and note its index number.")