import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

def run_assistant():
    speak("Hello! How can I help you?")
    
    while True:
        command = take_command()

        if "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")

        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            speak("Opening Google")

        elif "time" in command:
            time = datetime.datetime.now().strftime("%H:%M")
            speak("The time is " + time)

        elif "search google for" in command:
            query = command.replace("search google for", "")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak("Searching Google for " + query)

        elif "open calculator" in command:
            os.system("open -a Calculator")

        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

run_assistant()