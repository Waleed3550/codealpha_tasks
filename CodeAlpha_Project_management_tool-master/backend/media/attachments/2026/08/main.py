import os
import sys
import traceback
from automation.scanner import scan_apps, start_watcher
from voice.listen import listen_continuously
from voice.speak import speak
from automation.command_handler import handle_command
try:
    from ai.brain import ask_nova
except ImportError:
    def ask_nova(text):
        return "I am unable to reach the AI model right now Boss."

def main_callback(command):
    # This callback executes synchronously.
    # The microphone is automatically paused until this function returns.
    try:
        if command == "stop listening":
            speak("Voice listening stopped Boss.")
            return
            
        if command == "start listening":
            speak("Listening Boss.")
            return
            
        if command in ["exit", "shutdown"]:
            speak("Goodbye Boss. Shutting down.")
            os._exit(0)
            
        success, response = handle_command(command)
        
        if success:
            speak(response)
        else:
            print("Command handler returned false. Sending to AI...")
            ai_response = ask_nova(command)
            speak(ai_response)
            
    except Exception as e:
        print(f"Error handling command: {e}")
        traceback.print_exc()

def main():
    print("Nova Started")
    print("Scanning all installed applications...")
    apps = scan_apps()
    print(f"Ready — {len(apps)} applications detected.")

    start_watcher(interval=120)

    # Begin the sequential listening pipeline
    listen_continuously(main_callback)

if __name__ == "__main__":
    main()