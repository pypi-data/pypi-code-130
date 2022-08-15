import speech_recognition as sr
import pyttsx3
cmd=[]
what=[]

def SpeakText(command):
	engine = pyttsx3.init()
	rate=engine.getProperty("rate")
	engine.setProperty("rate",125)
	voices=engine.getProperty("voices")
	engine.setProperty("voice",voices[1].id)

	voices=engine.getProperty("volume")
	engine.setProperty("volume",1.0)
	
	engine.say(command)
	engine.runAndWait()

def Mira():
    with sr.Microphone() as a:
        r = sr.Recognizer()
        audio2 = r.listen(a)
        order = r.recognize_google(audio2)
        said=order.split(" ")
        what.append(order)
        cmd.append(said)

    
        
        
       
        

