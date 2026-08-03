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
import tkinter as tk
from tkinter import scrolledtext

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Voice Assistant")
        self.root.geometry("450x600")
        self.root.configure(bg="#1E1E2E")
        self.root.resizable(False, False)

        # Threading state
        self.assistant_active = False
        self.assistant_thread = None

        # Speech Engine
        self.engine = pyttsx3.init()

        # UI Layout
        self.setup_ui()

    def setup_ui(self):
        # Header / Title Label
        title_label = tk.Label(
            self.root, 
            text="🎙️ Voice Assistant", 
            font=("Helvetica", 18, "bold"), 
            bg="#1E1E2E", 
            fg="#CDD6F4"
        )
        title_label.pack(pady=15)

        # Status Panel
        status_frame = tk.Frame(self.root, bg="#313244", bd=0)
        status_frame.pack(fill="x", padx=20, pady=5)

        self.status_indicator = tk.Canvas(status_frame, width=12, height=12, bg="#313244", highlightthickness=0)
        self.status_indicator.pack(side="left", padx=(15, 5), pady=10)
        self.status_dot = self.status_indicator.create_oval(2, 2, 10, 10, fill="#A6ADC8") # Gray initial

        self.status_label = tk.Label(
            status_frame, 
            text="Status: Stopped", 
            font=("Helvetica", 11, "bold"), 
            bg="#313244", 
            fg="#A6ADC8"
        )
        self.status_label.pack(side="left", pady=10)

        # Log Area
        log_frame = tk.Frame(self.root, bg="#1E1E2E")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        log_label = tk.Label(
            log_frame, 
            text="Conversation Log", 
            font=("Helvetica", 10, "bold"), 
            bg="#1E1E2E", 
            fg="#BAC2DE"
        )
        log_label.pack(anchor="w", pady=(0, 5))

        self.log_area = scrolledtext.ScrolledText(
            log_frame, 
            font=("Courier", 10), 
            bg="#181825", 
            fg="#CDD6F4", 
            insertbackground="#CDD6F4", 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#313244", 
            highlightcolor="#89B4FA",
            wrap=tk.WORD
        )
        self.log_area.pack(fill="both", expand=True)
        self.log_area.configure(state='disabled') # Read only

        # Action Buttons Panel
        btn_frame = tk.Frame(self.root, bg="#1E1E2E")
        btn_frame.pack(fill="x", padx=20, pady=15)

        self.toggle_btn = tk.Button(
            btn_frame, 
            text="Start Assistant", 
            font=("Helvetica", 12, "bold"), 
            bg="#89B4FA", 
            fg="#1E1E2E", 
            activebackground="#B4BEFE", 
            activeforeground="#1E1E2E", 
            bd=0, 
            height=2, 
            cursor="hand2", 
            command=self.toggle_assistant
        )
        self.toggle_btn.pack(fill="x")

        # Initial instruction
        self.log_message("System: Click 'Start Assistant' to begin.")

    def log_message(self, message):
        """Append message to GUI scrolled text box thread-safely."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def set_status(self, text, color):
        """Update status label and glowing indicator color."""
        self.status_label.configure(text=f"Status: {text}", fg=color)
        self.status_indicator.itemconfig(self.status_dot, fill=color)

    def speak(self, text):
        """Add spoken phrase to log and run pyttsx3 speech synthesis."""
        self.log_message(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def toggle_assistant(self):
        if self.assistant_active:
            # Stop the assistant
            self.assistant_active = False
            self.toggle_btn.configure(text="Start Assistant", bg="#89B4FA")
            self.set_status("Stopped", "#A6ADC8")
            self.log_message("System: Voice Assistant stopped.")
            self.engine.say("Goodbye!")
            self.engine.runAndWait()
        else:
            # Start the assistant
            self.assistant_active = True
            self.toggle_btn.configure(text="Stop Assistant", bg="#F38BA8") # Red active
            self.set_status("Initializing...", "#F9E2AF") # Yellow
            self.log_message("System: Voice Assistant starting...")
            
            # Start background thread to run loop
            self.assistant_thread = threading.Thread(target=self.assistant_loop)
            self.assistant_thread.daemon = True
            self.assistant_thread.start()

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.root.after(0, self.set_status, "Listening...", "#A6E3A1") # Green
            r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                # Silence timeout
                return ""

        try:
            self.root.after(0, self.set_status, "Recognizing...", "#F9E2AF") # Yellow
            command = r.recognize_google(audio)
            self.log_message(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            self.log_message("System: Speech was unrecognized.")
            return None
        except sr.RequestError:
            self.log_message("System: Google Speech API unavailable.")
            return None

    def fetch_wikipedia_summary(self, query):
        try:
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

    def fetch_joke(self):
        try:
            url = "https://official-joke-api.appspot.com/random_joke"
            req = urllib.request.Request(url, headers={'User-Agent': 'DesktopVoiceAssistant/1.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                return f"{data['setup']} ... {data['punchline']}"
        except Exception:
            jokes = [
                "Why do programmers wear glasses? Because they can't C#.",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why did the database administrator leave the restaurant? Because there were too many joins."
            ]
            return random.choice(jokes)

    def timer_worker(self, duration_seconds, label):
        time.sleep(duration_seconds)
        time_unit = "seconds" if duration_seconds < 60 else "minutes"
        display_time = duration_seconds if duration_seconds < 60 else duration_seconds // 60
        self.speak(f"Time is up! Your timer for {display_time} {time_unit} is done.")

    def assistant_loop(self):
        # Step C: Speak greeting
        self.speak("Hello! How can I help you?")
        
        while self.assistant_active:
            self.root.after(0, self.set_status, "Ready", "#89B4FA") # Blue idle
            command = self.take_command()

            if not self.assistant_active:
                break

            # Error/Unrecognized
            if command is None:
                self.speak("Sorry, I didn't catch that.")
                continue
                
            if command == "":
                continue

            # Command matches
            if "open youtube" in command and not "play" in command:
                webbrowser.open("https://www.youtube.com")
                self.speak("Opening YouTube")

            elif "open google" in command:
                webbrowser.open("https://www.google.com")
                self.speak("Opening Google")

            elif "time" in command:
                time_str = datetime.datetime.now().strftime("%H:%M")
                self.speak(f"The time is {time_str}")

            elif "search google for" in command:
                query = command.replace("search google for", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
                self.speak(f"Searching Google for {query}")

            elif "play" in command or "search youtube for" in command:
                query = command.replace("play", "").replace("on youtube", "").replace("search youtube for", "").strip()
                if query:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
                    self.speak(f"Searching YouTube for {query}")
                else:
                    self.speak("What would you like me to play on YouTube?")

            elif "joke" in command or "make me laugh" in command:
                self.speak("Let me find a joke for you.")
                joke = self.fetch_joke()
                self.speak(joke)

            elif "timer" in command or "set a timer" in command:
                match = re.search(r'(\d+)\s*(second|minute)', command)
                if match:
                    value = int(match.group(1))
                    unit = match.group(2)
                    duration = value
                    if "minute" in unit:
                        duration = value * 60
                    self.speak(f"Setting a timer for {value} {unit}s.")
                    t = threading.Thread(target=self.timer_worker, args=(duration, unit))
                    t.daemon = True
                    t.start()
                else:
                    self.speak("I couldn't understand the duration for the timer.")

            elif "volume" in command or "louder" in command or "quieter" in command or "turn up" in command or "turn down" in command:
                def get_mac_volume():
                    try:
                        output = os.popen("osascript -e 'output volume of (get volume settings)'").read().strip()
                        return int(output)
                    except Exception:
                        return 50

                if "mute" in command or "silent" in command:
                    os.system("osascript -e 'set volume with output muted'")
                    self.speak("Volume muted.")
                elif "unmute" in command:
                    os.system("osascript -e 'set volume without output muted'")
                    self.speak("Volume unmuted.")
                elif "up" in command or "louder" in command or "increase" in command or "turn up" in command:
                    current_vol = get_mac_volume()
                    new_vol = min(100, current_vol + 10)
                    os.system(f"osascript -e 'set volume output volume {new_vol}'")
                    self.speak(f"Increasing volume to {new_vol} percent.")
                elif "down" in command or "quieter" in command or "decrease" in command or "lower" in command or "turn down" in command:
                    current_vol = get_mac_volume()
                    new_vol = max(0, current_vol - 10)
                    os.system(f"osascript -e 'set volume output volume {new_vol}'")
                    self.speak(f"Decreasing volume to {new_vol} percent.")
                else:
                    digits = re.findall(r'\d+', command)
                    if digits:
                        level = int(digits[0])
                        level = max(0, min(100, level))
                        os.system(f"osascript -e 'set volume output volume {level}'")
                        self.speak(f"Volume set to {level} percent.")
                    else:
                        self.speak("Please specify a volume level.")

            elif "brightness" in command or "dimmer" in command or "brighter" in command or "dim" in command:
                if "up" in command or "brighter" in command or "increase" in command:
                    self.speak("Increasing brightness.")
                    os.system("osascript -e 'tell application \"System Events\" to key code 145'")
                elif "down" in command or "dimmer" in command or "decrease" in command or "dim" in command:
                    self.speak("Decreasing brightness.")
                    os.system("osascript -e 'tell application \"System Events\" to key code 144'")
                else:
                    self.speak("Please say increase brightness or decrease brightness.")

            elif "lock system" in command or "lock screen" in command:
                self.speak("Locking screen.")
                os.system("pmset displaysleepnow")

            elif "open calculator" in command:
                self.speak("Opening Calculator")
                os.system("open -a Calculator")

            elif "exit" in command or "stop" in command:
                self.root.after(0, self.toggle_assistant)
                break

            elif any(phrase in command for phrase in ["search wikipedia for", "tell me about", "what is", "who is", "define"]):
                query = command
                for phrase in ["search wikipedia for", "tell me about", "what is", "who is", "define"]:
                    query = query.replace(phrase, "")
                query = query.strip()
                if query:
                    self.speak(f"Searching Wikipedia for {query}...")
                    summary = self.fetch_wikipedia_summary(query)
                    self.speak(summary)
                else:
                    self.speak("What would you like me to tell you about?")

            else:
                print(f"Command not matched: {command}")
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(command)}")
                self.speak(f"I didn't recognize that command, so I am searching Google for {command}.")

        self.root.after(0, self.set_status, "Stopped", "#A6ADC8")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()