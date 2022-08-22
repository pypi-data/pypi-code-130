import os
import speech_recognition
from gtts import gTTS
import random
from playsound import playsound





      


def listen(pausetime=0.5, language='en-US'):
      sr = speech_recognition.Recognizer()
      sr.pause_threshold = pausetime


      with speech_recognition.Microphone() as mic:
            sr.adjust_for_ambient_noise(source=mic, duration=0.5)
            audio = sr.listen(source=mic)
            query = sr.recognize_google(audio_data=audio, language=language)

            return query


def speak(text, language='en'):
      voice = gTTS(text, lang=language)
      folder = 'voices'
      file_voice_name = "audio"+str(random.randint(0, 100))+".mp3"
      voice.save(f"{folder}/{file_voice_name}")

      playsound(os.getcwd() + f'\{folder}\{file_voice_name}')

      return text





if not os.path.exists('voices'):
      os.mkdir('voices')