import time
from pyobjus import autoclass, protocol
from pyobjus.dylib_manager import load_framework, INCLUDE
load_framework(INCLUDE.AVFoundation)
load_framework('/System/Library/Frameworks/AppKit.framework')
load_framework('/System/Library/Frameworks/Foundation.framework')
NSTimer = autoclass('NSTimer')
NSString = autoclass('NSString')
NSArray = autoclass('NSArray')
NSObject = autoclass('NSObject')
AVSpeechSynthesizer = autoclass('AVSpeechSynthesizer')
AVSpeechUtterance = autoclass('AVSpeechUtterance')
AVSpeechSynthesisVoice = autoclass('AVSpeechSynthesisVoice')
NSURL = autoclass('NSURL')

from text2sentences import text_to_sentences
from .version import __version__

def get_locale_by_language(lang):
	locales = {
		'zh':'zh-CN',
		'en':'en-US',
		'tr':'tr-TR',
		'th':'th-TH',
		'sv':'sv-SE',
		'es':'es-ES',
		'sk':'sk-SK',
		'ru':'ru-RU',
		'ro':'ro-RO',
		'pt':'pt-PT',
		'pl':'pl-PL',
		'no':'no-NO',
		'ko':'ko-KO',
		'ja':'ja-JP',
		'it':'it-IT',
		'id':'id-ID',
		'hu':'hu-HU',
		'hi':'hi-IN',
		'el':'el-GR',
		'de':'de-DE',
		'fr':'fr-FR',
		'nl':'nl-NL',
		'da':'da-DK',
		'cs':'cs-CZ',
		'ar':'ar-SA'
	}
	return locales.get(lang, None)

def buildDriver(proxy, **kw):
	# return NSSpeechDriver.alloc().initWithProxy(proxy)
	return SpeechDriver(proxy, **kw)

class SpeechDriver:
	def __init__(self, proxy, **kw):
		self._proxy = proxy
		self._tts = AVSpeechSynthesizer.alloc().init()
		self._tts.setDelegate_(self)
		self._completed = True
		self.rate = 180
		self.set_stop_period()
		self.voice = None
		self.speaking_sentence = None

	def set_stop_period(self):
		r = 1.0 / float(self.rate)
		self.semi_stop_period = 1.5 * r
		self.sentence_stop_period = 3.0 * r

	def pause(self):
		self._tts.pauseSpeakingAtBoundary()

	def contineu(self):
		self._tts.continueSpeaking()

	def stop(self):
		if self._proxy.isBusy():
			self._completed = False
		self._tts.stopSpeakingAtBoundary()

	def say(self, text):
		self._proxy.setBusy(True)
		self._completed = True
		self.sentences += text_to_sentences(text)

	def set_utterances_by_sentence(self, utterance, sentence):
		if sentence.dialog:
			utterance.pitchModifier = 1.25
		else:
			utterance.pitchModifier = 1.0
		locale = get_local_by_language(sentence.lang)
		voice = AVSpeechSynthesisVoice.voiceWithLanguage(locale)
		utterance.voice = voice
		utterance.rate = self.rate

	def isBusy(self):
		if self.speaking_sentence:
			return True
		else:
			return False

	def speak_sentence(self, sentence):
		utterance = AVSpeechUtterance.alloc().initWithString(sentence.text)
		self.set_utterances_by_sentence(utterance, sentence)
		self._tts.speakUtterance(utterance)

	def destroy(self):
		self._tts.setDelegate_(None)
		del self._tts

	def startLoop(self):
		self._proxy.notify('started-utterance')
		speak_next_sentence()

	def speak_next_sentence(self):
		if len(self.sentences) > 0:
			self.speaking_sentence = self.sentences.pop(0)
			self.speak_sentence(self.speaking_sentence)
		else:
			sself.speaking_sentence = None
			self._completed = True
			self._proxy.notify('finished-utterance', 
								completed=self._completed)
			self._proxy.setBusy(False)
			
	def endLoop(self):
		self.speaking_sentence = None

	def iterate(self):
		self._proxy.setBusy(False)
		yield

	def getProperty(self, name):
		if name == 'voices':
			return self.get_all_language()
		elif name == 'voice':
			return self.voice
		elif name == 'rate':
			return None
		elif name == 'volume':
			return None
		elif name == "pitch":
			print("Pitch adjustment not supported when using NSSS")
		else:
			raise KeyError('unknown property %s' % name)

	def setProperty(self, name, value):
		return
		if name == 'voice':
			# vol/rate gets reset, so store and restore it
			self.voice = value
		elif name == 'rate':
			self._tts.setRate_(value)
		elif name == 'volume':
			self._tts.setVolume_(value)
		elif name == 'pitch':
			print("Pitch adjustment not supported when using NSSS")
		else:
			raise KeyError('unknown property %s' % name)

	def get_all_language(self):
		langs = AVSpeechSynthesisVoice.speechVoices()
		return langs

	def save_to_file(self, text, filename):
		url = NSURL.fileURLWithPath_(filename)
		self._tts.startSpeakingString_toURL_(text, url)

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_didCancelSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_didContinueSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_didPauseSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_didStartSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_didFinishSpeechUtterance_(self, *args):
		print('args=', args)
		if self.speaking_sentence.semi_sentenece:
			time.sleep(self.simi_stop_period)
		else:
			time.sleep(self.sentence_stop_period)
		self.speak_next_utterance()
		return

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_willSpeakRangeOfSpeechString_(self, *args):
		print('args=', args)

