# Check the file readme.md for more information.


# Importing modules


# Other
from colorama import Fore, Back, Style
from termcolor import colored











class FilesEncoders:


      # Manage
      __manager__ = """import urllib.request
from webes import FilesEncoders




# Manager the server
# 0 - true, 1 - false
manager = {
      'private': 0, # Private server
      'security': 0, # Security on the server
      'always': 1, # Being always online
      'debug': 1, # Debug of errors on the server
}

def server():
      with open("__server__.py", "w+", encoding='UTF-8') as addw:
            addw.write(FilesEncoders.__server__)
            addw.close()


server()

      



print("The file server.py has created!")
      """


      # Readme
      __readme__ = """==============================
Documentation

English (UK)
==============================




Create a . py file with any name and type in the "webs" module.

from webs import *


And write there:

start_server()

In the console you can see the API. Copy it.


Your API: (your API)


Next, go to the manager folder and go to the manage.py file

Customize the settings for yourself.

Then run the manage.py file

And create a server.py file

Run it and start the server.













==============================
Документация

Русский (RU)
==============================




Создайте файл .py с любым названием и заимпортировайте туда модуль "webs".

from webs import *


И напишите туда:

start_server()

В консоле полявиться API. Скопируйте его.


Your API: (ваш API)


Дальше зайдите в папку manager и зайдите в файл manage.py

Настройте параметры под себя.

Потом запустите файл manage.py

И создаёться файл server.py

Его запустите и запуститься сервер.

      """




      # Server
      __server__ = """from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
      return "<h1>Hello World!</h1>"


if __name__ == "__main__":
      app.run()
"""










# Starting server
def start_server():
      create("__manager__.py", FilesEncoders.__manager__)
      print(colored("Created file __manager__.py", "yellow"))

def doc():
      create("__readme__.md", FilesEncoders.__readme__)
      print(colored("Created file __readme__.md", "yellow"))




def create(file, txt):
      with open(file, 'w+', encoding='UTF-8') as w:
            w.write(txt)
            w.close()




