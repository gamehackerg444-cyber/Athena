import os
import webbrowser
import datetime
from dotenv import load_dotenv
import glob
import subprocess # Needed for the new feature

import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# --- 1. INITIALIZATION ---
# (Same as before)
load_dotenv()
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Failed to initialize TTS engine: {e}")
    exit()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    print(f"Failed to configure Gemini API: {e}. Programming help will be unavailable.")
    model = None

# --- 2. CORE FUNCTIONS ---
# (speak, take_command, ask_programming_question are the same as before)
def speak(text: str):
    print(f"Phoenix: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return "timeout"
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        return "none"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "error"

def ask_programming_question(question: str) -> str:
    if not model:
        return "Sorry, the programming help module is not initialized."
    prompt = f"Expert programmer assistant. Answer concisely. Question: {question}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't get an answer. Error: {e}"

def optimize_laptop():
    # (The previous, safer optimization function)
    speak("Starting laptop optimization.")
    speak("Closing common background processes.")
    processes_to_kill = ["chrome.exe", "msedge.exe", "firefox.exe", "discord.exe"]
    for process in processes_to_kill:
        os.system(f"taskkill /F /IM {process} > nul 2>&1")
    speak("Cleaning temporary files.")
    temp_folders = [
        os.path.join(os.environ.get('TEMP', ''), '*'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp', '*')
    ]
    deleted_files_count = 0
    for folder_path in temp_folders:
        files = glob.glob(folder_path)
        for file_path in files:
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
                deleted_files_count += 1
            except Exception: pass
    speak(f"Optimization complete. Cleaned up {deleted_files_count} temporary files.")

# --- NEW: AGGRESSIVE OPTIMIZATION ---
def aggressive_clean():
    """Kills all non-whitelisted processes, replicating the batch script."""
    speak("Warning: This will close all non-essential applications, and you will lose any unsaved work. Are you sure you want to continue?")
    
    confirmation = take_command()
    if 'yes' not in confirmation:
        speak("Aggressive clean cancelled.")
        return

    speak("Proceeding with aggressive clean. Terminating all non-essential processes.")

    # Whitelist of essential processes to keep running. Added python to prevent the script from killing itself.
    whitelist = {
        "explorer.exe", "taskmgr.exe", "cmd.exe", "conhost.exe", "dwm.exe",
        "svchost.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
        "python.exe", "pythonw.exe"
    }
    
    try:
        # Get the list of running processes
        result = subprocess.check_output(['tasklist']).decode('utf-8', errors='ignore')
        killed_count = 0
        
        # Loop through each line in the tasklist output
        for line in result.splitlines()[3:]: # Skip header lines
            parts = line.split()
            if parts:
                process_name = parts[0]
                if process_name.lower() not in whitelist:
                    try:
                        # Forcibly terminate the process
                        print(f"  - Terminating {process_name}")
                        subprocess.run(
                            ['taskkill', '/F', '/IM', process_name],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        killed_count += 1
                    except Exception:
                        pass # Ignore errors for processes that can't be killed
        
        speak(f"Aggressive clean complete. Terminated {killed_count} processes.")

    except FileNotFoundError:
        speak("Error: tasklist command not found. This feature is for Windows only.")
    except Exception as e:
        speak(f"An error occurred: {e}")

# --- 3. MAIN EXECUTION LOOP ---

if __name__ == "__main__":
    speak("Hello! I am your Phoenix.")
    
    while True:
        choice = input("\nPress Enter to use voice, or type 'text' to write a command: ").lower()
        query = ""
        if choice == 'text':
            query = input("You: ").lower()
        else:
            query = take_command()

        if query in ["none", "timeout", "error"]:
            if query == "timeout": speak("I didn't hear anything.")
            continue

        # --- Command Processing ---
        
        # NEW: Aggressive Clean Command
        if 'aggressive clean' in query or 'deep clean' in query:
            aggressive_clean()
        
        # Standard Optimization Command
        elif 'optimize my laptop' in query:
            optimize_laptop()

        # Other commands...
        elif 'open notepad' in query:
            speak("Opening Notepad.")
            os.system('notepad')
        elif 'open youtube' in query:
            speak("Opening YouTube.")
            webbrowser.open("https://youtube.com")
        elif 'the time' in query:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {str_time}")
        elif 'the date' in query:
            str_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {str_date}")
        elif 'explain' in query or 'code for' in query or 'what is' in query:
            speak("Getting a programming answer for you...")
            answer = ask_programming_question(query)
            speak(answer)
        elif 'exit' in query or 'stop' in query or 'quit' in query:
            speak("Goodbye!")
            break