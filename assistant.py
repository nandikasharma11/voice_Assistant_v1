import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os

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
            
        # Step F: Process command (Success)
        # Step H: Command matches?
        if "open youtube" in command:
            # Step I: Open webbrowser
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")

        elif "open google" in command:
            # Open Google (Matches README table)
            webbrowser.open("https://www.google.com")
            speak("Opening Google")

        elif "time" in command:
            # Step K: Announce current time
            time_str = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {time_str}")

        elif "search google for" in command:
            # Step J: Query google in browser
            query = command.replace("search google for", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching Google for {query}")

        elif "open calculator" in command:
            # Step L: Launch macOS Calculator
            speak("Opening Calculator")
            os.system("open -a Calculator")

        elif "exit" in command or "stop" in command:
            # Step M: Speak 'Goodbye' & Stop
            speak("Goodbye!")
            break
            
        # If command is unrecognized by the match system, it loops back to listening (Step D)

if __name__ == "__main__":
    # Step A: Start assistant.py
    run_assistant()