# main.py — sab kuch ek jagah jodta hai

import pyttsx3
import config
from listener import listen
from brain import think
from executor import execute

# voice engine setup
engine = pyttsx3.init()
engine.setProperty('rate', config.VOICE_RATE)
engine.setProperty('volume', config.VOICE_VOLUME)

# thodi aachi awaaz ke liye
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    print(f"🤖 {config.AGENT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()

def run():
    speak(f"Hello! Main {config.AGENT_NAME} hoon. Aapki kya madad kar sakta hoon?")
    
    while True:
        try:
            # sun lo
            user_input = listen()
            
            if user_input is None:
                continue
            
            # band karne ka command
            if any(word in user_input for word in ["exit", "quit", "band karo", "bye", "goodbye"]):
                speak("Theek hai, band ho raha hoon. Alvida!")
                break
            
            # AI se samjho
            result = think(user_input)
            
            # response bolo
            speak(result.get("response", "Ho gaya!"))
            
            # action karo
            action = result.get("action", "unknown")
            params = result.get("params", {})
            
            if action != "unknown":
                success = execute(action, params)
                if not success:
                    speak("Yeh kaam nahi kar paya, maafi chahta hoon")
                    
        except KeyboardInterrupt:
            speak("Alvida!")
            break

if __name__ == "__main__":
    run()