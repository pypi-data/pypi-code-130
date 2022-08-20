from .cartoon import cartoon_characters
from .games import game_characters
from .memes import memes_characters
from .animals import animal_characters

genres = ["cartoon_characters", "game_characters", 
        "memes_characters", "animal_characters"]
        
all_characters = []

for genre in genres:
    for character in eval(genre):
        all_characters.append({"name":character, "ascii":eval(genre)[character]})
    