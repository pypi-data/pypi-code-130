from simple_term_menu import TerminalMenu
import openai
from alive_progress import alive_bar
import colored
from colored import stylize
import warnings
import pyfiglet
from artk.transform import transform
from artk.parser import extract_text
import os
warnings.filterwarnings("ignore")

output1 = []
output2 = []
output3 = []


def text_splitter(text, levels, key):
    maxlen = 10000

    if len(text) > maxlen:
        res = _rephrase(text[:maxlen], levels, key)
        text_splitter(text[maxlen+1:], levels, key)
    else:
        res = _rephrase(text, levels, key)
    
    return res

def _rephrase(text, levels, key):
    openai.api_key = key

    engine_type='text-davinci-002'
    #engine_type='text-curie-001'
    quest1 = "Rephrase for a second-grade student:\n\n"
    quest2 = "Rephrase for a high school student:\n\n"
    quest3 = "Rephrase for a PhD student:\n\n"

    result = []

    # level 1
    if (levels==0) or (levels==3):
        result1 = openai.Completion.create(
          engine=engine_type,
          prompt=quest1+text,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0)["choices"][0]["text"].\
            replace("\n", "").replace('"', '').strip()
        result.append(result1)
    
    # level 2
    if (levels==1) or (levels==3):
        result2 = openai.Completion.create(
          engine=engine_type,
          prompt=quest2+text,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0)["choices"][0]["text"].\
            replace("\n", "").replace('"', '').strip()
        result.append(result2)

    # level 3
    if (levels==2) or (levels==3):  
        result3 = openai.Completion.create(
          engine=engine_type,
          prompt=quest3+text,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0)["choices"][0]["text"].\
            replace("\n", "").replace('"', '').strip()
        result.append(result3)

    return result


def rephraser():
    key = input("\n The Rephraser is an AI-based tool requiring an OpenAI API key.\n For instructions on acquiring a key, visit the Help page.\n Please enter your API key or type \'Demo\' to continue:\n\n ")
    if key=='Demo':
        key = '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'

    rephrase_menu_title = "\n Select an input method:\n"
    rephrase_menu_items = ["arXiv",
                            "Raw text",
                            "Exit"]
    rephrase_menu_cursor = "> "
    rephrase_menu_cursor_style = ("fg_yellow", "bold")
    rephrase_menu_style = ("italics", "bg_purple")
    rephrase_menu_exit = False

    rephrase_menu = TerminalMenu(
        menu_entries=rephrase_menu_items,
        title=rephrase_menu_title,
        menu_cursor=rephrase_menu_cursor,
        menu_cursor_style=rephrase_menu_cursor_style,
        menu_highlight_style=rephrase_menu_style,
        cycle_cursor=True
    )

    rephrase_sel = rephrase_menu.show()

    if rephrase_sel == 2:
        return

    if rephrase_sel == 0:
        #pdf = input("\n Enter arXiv link:\n\n ")
        pdf = "https://arxiv.org/pdf/1811.05477.pdf"

        print("\n Processing...")
        with alive_bar(bar=None, spinner='fishes', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
            text = extract_text(pdf)

        rephrase_menu_title = "\n What would you like to rephrase?\n"
        rephrase_menu_items = ["Abstract"]
        for section in text['sections']:
            rephrase_menu_items.append(section['heading'].capitalize())
        rephrase_menu_items.append('Full text')
        rephrase_menu_cursor = "> "
        rephrase_menu_cursor_style = ("fg_yellow", "bold")
        rephrase_menu_style = ("italics", "bg_purple")
        rephrase_menu_exit = False

        rephrase_menu = TerminalMenu(
            menu_entries=rephrase_menu_items,
            title=rephrase_menu_title,
            menu_cursor=rephrase_menu_cursor,
            menu_cursor_style=rephrase_menu_cursor_style,
            menu_highlight_style=rephrase_menu_style,
            cycle_cursor=True
        )

        ans = rephrase_menu.show()
        if ans==0: text=text['abstract']        
        elif ans==len(rephrase_menu_items)-1: text=text
        else: text=list(text.values())[0]

    elif rephrase_sel == 1:
        text = input("\n Enter text:\n ")
    
    level_menu_title = "\n Select an output level:\n"
    level_menu_items = ["Max simplification",
                        "Intermediate",
                        "Advanced",
                        "All"]
    level_menu_cursor = "> "
    level_menu_cursor_style = ("fg_yellow", "bold")
    level_menu_style = ("italics", "bg_purple")
    level_menu_exit = False

    level_menu = TerminalMenu(
        menu_entries=level_menu_items,
        title=level_menu_title,
        menu_cursor=level_menu_cursor,
        menu_cursor_style=level_menu_cursor_style,
        menu_highlight_style=level_menu_style,
        cycle_cursor=True
    )

    level_sel = level_menu.show()

    with alive_bar(bar=None, spinner='fish', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
        rephrased_text = text_splitter(text, level_sel, key)

    rephrase_menu_title = "\n Run completed! How would you like your output?\n"
    rephrase_menu_items = ["Printed to console",
                            "Written to file",
                            ]
    rephrase_menu_cursor = "> "
    rephrase_menu_cursor_style = ("fg_yellow", "bold")
    rephrase_menu_style = ("italics", "bg_purple")
    rephrase_menu_exit = False

    rephrase_menu = TerminalMenu(
        menu_entries=rephrase_menu_items,
        title=rephrase_menu_title,
        menu_cursor=rephrase_menu_cursor,
        menu_cursor_style=rephrase_menu_cursor_style,
        menu_highlight_style=rephrase_menu_style,
        cycle_cursor=True
    )
    ans_output = rephrase_menu.show()

    if ans_output==0:
        for summa in rephrased_text:
            transform(text, summa, pyfiglet.figlet_format("Rephraser", font = "stampatello"), "yellow")

        os.system('clear')
        print(stylize("\n{}".format(pyfiglet.figlet_format("Rephraser", font = "stampatello")),colored.attr("bold")+colored.fg('yellow')))
        for summa in rephrased_text:
            print(summa,'\n')

        rating = input(stylize(" Please rate the output:\n [1-10] ",colored.fg("yellow")))

        input(stylize("\n Press Enter to continue...",colored.fg("yellow")))

        return

    if ans_output==1:
        with open("../output/rephrased_text.txt", "w") as f:
            print(stylize("\n{}".format(pyfiglet.figlet_format("Rephraser", font = "stampatello")),colored.attr("bold")+colored.fg('yellow')))
            print(" Write out successful.\n")
            for summa in rephrased_text:
                print(summa,'\n')    
            input(stylize(" Press Enter to continue...",colored.fg("yellow")))

            return

    return

if __name__=="__main__":
    rephraser()

