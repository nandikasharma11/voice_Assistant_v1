# Voice Assistant

A lightweight, Python-based desktop voice assistant that listens to speech commands, interprets them, and executes system tasks or web activities. 

## Features

- 🎙️ **Voice Recognition**: Listens to commands through your microphone using Google Speech Recognition.
- 🔊 **Text-to-Speech**: Responds back using the `pyttsx3` offline speech synthesis engine.
- 🌐 **Web Automation**: Opens Google and YouTube in your default browser.
- 🔍 **Google Search**: Performs hands-free search queries on Google.
- 🕒 **Time Announcement**: Reports the current system time.
- 🧮 **System Control**: Launches native applications (e.g., macOS Calculator).

---

## Installation & Setup

### 1. Prerequisites

Before installing the Python packages, you must have some system-level dependencies for audio input:

#### macOS (Homebrew required)
Since the `SpeechRecognition` library uses PyAudio for microphone input, you need to install `portaudio` first:
```bash
brew install portaudio
```

#### Ubuntu / Debian
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

#### Windows
On Windows, PyAudio binaries can usually be installed directly via pip.

---

### 2. Set Up Virtual Environment

It is recommended to run the project in a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

---

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

*Note: If installing PyAudio fails on macOS, run:*
```bash
pip install --global-option='--include-path=/opt/homebrew/include' --global-option='--listen-path=/opt/homebrew/lib' pyaudio
```

---

## Usage

Run the assistant script:

```bash
python assistant.py
```

Once running, the assistant will speak `"Hello! How can I help you?"` and start listening.

### Supported Voice Commands

| Command | Action |
|---|---|
| **"open youtube"** | Opens YouTube in the browser |
| **"open google"** | Opens Google homepage |
| **"time"** | Announces the current local time |
| **"search google for [query]"** | Searches Google for the specified query |
| **"open calculator"** | Launches the macOS Calculator app |
| **"exit"** or **"stop"** | Stops the assistant and exits |

---

## Technical Architecture

The assistant's flow is illustrated below:

```mermaid
graph TD
    A[Start assistant.py] --> B[Initialize pyttsx3 Engine]
    B --> C[Speak greeting]
    C --> D[Listen to microphone input via SpeechRecognition]
    D --> E{Convert Speech to Text}
    E -- Success --> F[Process command]
    E -- Error / Unrecognized --> G[Speak 'Sorry, I didn't catch that'] --> D
    F --> H{Command matches?}
    H -- "open youtube" --> I[Open webbrowser] --> D
    H -- "search google for..." --> J[Query google in browser] --> D
    H -- "time" --> K[Announce current time] --> D
    H -- "open calculator" --> L[Launch macOS Calculator] --> D
    H -- "exit" / "stop" --> M[Speak 'Goodbye' & Stop]
```
