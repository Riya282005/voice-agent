# listener.py — voice sun ke text mein convert karta hai

import speech_recognition as sr
import config

def listen():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Bol raha hoon... sun raha hoon!")
        
        # background noise adjust karo
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,
                phrase_time_limit=config.PHRASE_TIMEOUT
            )
            
            print("⏳ Samajh raha hoon...")
            
            # Google speech recognition use karo
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"✅ Tune kaha: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ Kuch nahi suna...")
            return None
        except sr.UnknownValueError:
            print("❓ Samajh nahi aaya, dobara bolo")
            return None
        except sr.RequestError:
            print("❌ Internet check karo")
            return None