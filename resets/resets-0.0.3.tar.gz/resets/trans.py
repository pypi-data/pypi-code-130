# Main Resets script

# Imports

# API
from translate import Translator as t
import googletrans as g



managers = {
      # Translate
      "from": None,
      "to": None,
}







# TRANSLATOR
def translate(text, fr, to):
      
      managers['from'] = fr
      managers['to'] = to

      translator = t(from_lang=managers['from'], to_lang=managers['to'])
      translation = translator.translate(text)

      return translation


def lang_list():
      encode = g.LANGUAGES

      return encode



