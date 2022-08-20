from .characters import all_characters

def split_at_max_width(s, text_box_width=50):
    lines = [s[idx:idx + text_box_width] for idx in range(0, len(s), text_box_width)]
    return lines

def draw_text_box(s):
    lines = split_at_max_width(s)
    box_width = len(lines[0])
    print("  " + "_"*box_width)
    for line in lines:
        print(f"| " + line + " " * (box_width - len(line) + 1) + "|")
    print("  " + "="*box_width)

def draw_arrow():
    print(" "*11 + "\\")
    print(" "*12 + "\\")
    print(" "*13 + "\\", end="")

def get_character(character_name):
    for c in all_characters:
        if c["name"] == character_name:
            character = c
            return character
    raise ValueError("Character name is invalid.")

def draw(character_name, text=""):
    character = get_character(character_name)
    if text != "":
        draw_text_box(text)
        draw_arrow()
    print(character["ascii"])
