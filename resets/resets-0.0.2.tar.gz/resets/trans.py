# Main Resets script

# Imports

# API
from translate import Translator as t
import googletrans as g

# Manager
import manager as m







# TRANSLATOR
def translate(text, fr, to):
      
      m.managers['from'] = fr
      m.managers['to'] = to

      translator = t(from_lang=m.managers['from'], to_lang=m.managers['to'])
      translation = translator.translate(text)

      return translation


def lang_list():
      encode = g.LANGUAGES

      return encode



