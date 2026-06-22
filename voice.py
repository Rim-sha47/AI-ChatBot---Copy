import speech_recognition as sr
import pyttsx3
import threading

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Initialize TTS Engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            
            # Use female voice if available
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Warning: TTS initialization failed: {e}")
            self.engine = None

    def speak(self, text):
        if self.engine is None:
            return
            
        def _speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
                
        # Run in thread to prevent blocking UI
        threading.Thread(target=_speak_thread, daemon=True).start()

    def listen(self, timeout=5):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
                
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "Timeout: Did not hear anything."
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        except Exception as e:
            return f"Microphone error: {e}"
