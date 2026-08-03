import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import urllib.parse
import urllib.request
import json
import threading
import time
import re
import random

# Step B: Initialize pyttsx3 Engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Step D & E: Listen to microphone input via SpeechRecognition & Convert Speech to Text
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            # Return empty string to loop back silently if no speech is detected
            return ""

    try:
        # Step E: Convert Speech to Text
        print("Recognizing...")
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Speech was unrecognized.")
        return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return None

# Advanced Helper: Fetch summary from Wikipedia REST API
def fetch_wikipedia_summary(query):
    try:
        # Standardize query format (capitalize first letter/spaces to underscores)
        formatted_query = query.strip().title().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted_query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'DesktopVoiceAssistant/1.0 (contact: admin@example.com)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            extract = data.get('extract')
            if extract:
                return extract
            return f"I found the Wikipedia page for {query}, but could not parse a summary."
    except Exception as e:
        print("Wikipedia API Error:", e)
        return f"Sorry, I couldn't retrieve information about {query} from Wikipedia."

# Advanced Helper: Fetch random joke from public API with curated offline fallback
def fetch_joke():
    try:
        url = "https://official-joke-api.appspot.com/random_joke"
        req = urllib.request.Request(url, headers={'User-Agent': 'DesktopVoiceAssistant/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            return f"{data['setup']} ... {data['punchline']}"
    except Exception:
        # Fallback offline jokes
        jokes = [
            "Why do programmers wear glasses? Because they can't C#.",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why did the database administrator leave the restaurant? Because there were too many joins."
        ]
        return random.choice(jokes)

# Advanced Helper: Timer worker running in background thread
def timer_worker(duration_seconds, label):
    time.sleep(duration_seconds)
    time_unit = "seconds" if duration_seconds < 60 else "minutes"
    display_time = duration_seconds if duration_seconds < 60 else duration_seconds // 60
    speak(f"Time is up! Your timer for {display_time} {time_unit} is done.")

# Step F & H: Process command and check matches
def run_assistant():
    # Step C: Speak greeting
    speak("Hello! How can I help you?")
    
    while True:
        # Step D & E: Listen and Convert
        command = take_command()

        # Step E -> Error / Unrecognized
        if command is None:
            # Step G: Speak 'Sorry, I didn't catch that'
            speak("Sorry, I didn't catch that.")
            continue  # Loop back to Step D
            
        if command == "":
            continue  # Silent loop back on timeout

        # Step F: Process command (Success)
        # Step H: Command matches?
        
        # 1. YouTube Open
        if "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")

        # 2. Google Open
        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            speak("Opening Google")

        # 3. Announce Current Time
        elif "time" in command:
            time_str = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {time_str}")

        # 4. Search Google
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching Google for {query}")

        # 5. Play on YouTube
        elif "play" in command and "on youtube" in command:
            # e.g., "play bohemian rhapsody on youtube"
            query = command.replace("play", "").replace("on youtube", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
            speak(f"Playing {query} on YouTube")

        # 6. Wikipedia Search / Information Retrieval
        elif "search wikipedia for" in command or "tell me about" in command:
            query = command.replace("search wikipedia for", "").replace("tell me about", "").strip()
            speak(f"Searching Wikipedia for {query}...")
            summary = fetch_wikipedia_summary(query)
            speak(summary)

        # 7. Joke Teller
        elif "joke" in command:
            speak("Let me find a joke for you.")
            joke = fetch_joke()
            speak(joke)

        # 8. Set Timer
        elif "timer" in command or "set a timer" in command:
            # Regex to find numbers and time unit (seconds/minutes)
            match = re.search(r'(\d+)\s*(second|minute)', command)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                
                duration = value
                if "minute" in unit:
                    duration = value * 60
                
                speak(f"Setting a timer for {value} {unit}s.")
                # Run timer in background thread to avoid blocking the assistant
                t = threading.Thread(target=timer_worker, args=(duration, unit))
                t.daemon = True
                t.start()
            else:
                speak("I couldn't understand the duration for the timer. Please specify seconds or minutes.")

        # 9. macOS System controls (Volume and Screen Lock)
        elif "volume" in command:
            if "mute" in command:
                os.system("osascript -e 'set volume with output muted'")
                speak("Volume muted.")
            elif "unmute" in command:
                os.system("osascript -e 'set volume without output muted'")
                speak("Volume unmuted.")
            else:
                # Search for digits in the command (e.g. "set volume to 50 percent")
                digits = re.findall(r'\d+', command)
                if digits:
                    level = int(digits[0])
                    # Bound level to 0-100 range
                    level = max(0, min(100, level))
                    # macOS volume scale is 0 to 7 (AppleScript is 0 to 100)
                    os.system(f"osascript -e 'set volume output volume {level}'")
                    speak(f"Volume set to {level} percent.")
                else:
                    speak("Please specify a volume level from zero to one hundred percent.")

        elif "lock system" in command or "lock screen" in command:
            speak("Locking screen.")
            os.system("pmset displaysleepnow")

        # 10. Open macOS native calculator
        elif "open calculator" in command:
            speak("Opening Calculator")
            os.system("open -a Calculator")

        # 11. Exit Program
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    run_assistant()