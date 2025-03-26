import os
import tempfile
from gtts import gTTS
import speech_recognition as sr
import pygame
import threading
import queue
import time

class VoiceProcessor:
    def __init__(self):
        """Initialize the voice processor with text-to-speech and speech-to-text capabilities."""
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Audio processing queue
        self.audio_queue = queue.Queue()
        
        # Speech recognition thread
        self.recognition_thread = None
        self.is_listening = False
        
        # Temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        
    def text_to_speech(self, text):
        """Convert text to speech and play it."""
        try:
            # Generate temporary file path
            temp_file = os.path.join(self.temp_dir, f'speech_{time.time()}.mp3')
            
            # Convert text to speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Play the audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Clean up temporary file
            os.remove(temp_file)
            
            return True
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            return False
    
    def start_listening(self, callback):
        """Start continuous speech recognition."""
        if self.recognition_thread is not None and self.recognition_thread.is_alive():
            return False
        
        self.is_listening = True
        self.recognition_thread = threading.Thread(
            target=self._recognition_worker,
            args=(callback,)
        )
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        return True
    
    def stop_listening(self):
        """Stop continuous speech recognition."""
        self.is_listening = False
        if self.recognition_thread is not None:
            self.recognition_thread.join()
            self.recognition_thread = None
    
    def _recognition_worker(self, callback):
        """Worker function for continuous speech recognition."""
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.is_listening:
                try:
                    # Listen for speech
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                    # Recognize speech using Google Speech Recognition
                    text = self.recognizer.recognize_google(audio)
                    
                    if text:
                        # Call the callback function with the recognized text
                        callback(text)
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results; {str(e)}")
                except Exception as e:
                    print(f"Error in speech recognition: {str(e)}")
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_listening()
        pygame.mixer.quit()
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir) 