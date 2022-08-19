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
        res = _summarize(text[:maxlen], levels, key)
        text_splitter(text[maxlen+1:], levels, key)
    else:
        res = _summarize(text, levels, key)
    
    return res

def _summarize(text, levels, key):
    openai.api_key = key

    engine_type='text-davinci-002'
    #engine_type='text-curie-001'
    quest1 = "Summarize for a second-grade student:\n\n"
    quest2 = "Summarize for a high school student:\n\n"
    quest3 = "Summarize for a PhD student:\n\n"

    result = []

    # level 1
    run = True
    if (levels==0) or (levels==3):
        while run==True:
            result1 = openai.Completion.create(
              engine=engine_type,
              prompt=quest1+text,
              temperature=0.7,
              max_tokens=1000,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0)["choices"][0]["text"].\
                replace("\n", "").replace('"', '').strip()
            if len(result1)<10:
                retry = input(' ARTK identified a poor quality summary, would you like to re-run? [y/n]\n ')
                if retry in ['y','Y']:
                    run=True
                else:
                    run=False
            else:
                run=False
        result.append(result1)

    # level 2
    run = True
    if (levels==1) or (levels==3):
        while run==True:
            result2 = openai.Completion.create(
              engine=engine_type,
              prompt=quest2+text,
              temperature=0.7,
              max_tokens=1000,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0)["choices"][0]["text"]#.\
                #replace("\n", "").replace('"', '').strip()
            if len(result2)<10:
                retry = input(' ARTK identified a poor quality summary, would you like to re-run? [y/n]\n ')
                if retry in ['y','Y']:
                    run=True
                else:
                    run=False
            else:
                run=False
        result.append(result2)

    # level 3
    run = True
    if (levels==2) or (levels==3):  
        while run==True:
            result3 = openai.Completion.create(
              engine=engine_type,
              prompt=quest3+text,
              temperature=0.7,
              max_tokens=1000,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0)["choices"][0]["text"].\
                replace("\n", "").replace('"', '').strip()
            if len(result3)<10:
                retry = input(' ARTK identified a poor quality summary, would you like to re-run? [y/n]\n ')
                if retry in ['y','Y']:
                    run=True
                else:
                    run=False
            else:
                run=False
        result.append(result3)

    return result


def summarizer():
    key = input("\n The Summarizer is an AI-based tool requiring an OpenAI API key.\n For instructions on acquiring a key, visit the Help page.\n Please enter your API key or type \'Demo\' to continue:\n\n ")
    if key=='Demo':
        key = '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'

    summarize_menu_title = "\n Select an input method:\n"
    summarize_menu_items = ["arXiv",
                            "Raw text",
                            "Exit"]
    summarize_menu_cursor = "> "
    summarize_menu_cursor_style = ("fg_yellow", "bold")
    summarize_menu_style = ("italics", "bg_purple")
    summarize_menu_exit = False

    summarize_menu = TerminalMenu(
        menu_entries=summarize_menu_items,
        title=summarize_menu_title,
        menu_cursor=summarize_menu_cursor,
        menu_cursor_style=summarize_menu_cursor_style,
        menu_highlight_style=summarize_menu_style,
        cycle_cursor=True
    )

    summarize_sel = summarize_menu.show()

    if summarize_sel == 2:
        return

    if summarize_sel == 0:
        #pdf = input("\n Enter arXiv link:\n\n ")
        pdf = "https://arxiv.org/pdf/1811.05477.pdf"

        print("\n Processing...")
        with alive_bar(bar=None, spinner='fishes', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
            text = extract_text(pdf)

        summarize_menu_title = "\n What would you like to summarize?\n"
        summarize_menu_items = ["Abstract"]
        for section in text['sections']:
            summarize_menu_items.append(section['heading'].capitalize())
        summarize_menu_items.append('Full text')
        summarize_menu_cursor = "> "
        summarize_menu_cursor_style = ("fg_yellow", "bold")
        summarize_menu_style = ("italics", "bg_purple")
        summarize_menu_exit = False

        summarize_menu = TerminalMenu(
            menu_entries=summarize_menu_items,
            title=summarize_menu_title,
            menu_cursor=summarize_menu_cursor,
            menu_cursor_style=summarize_menu_cursor_style,
            menu_highlight_style=summarize_menu_style,
            cycle_cursor=True
        )

        ans = summarize_menu.show()
        if ans==0: text=text['abstract']        
        elif ans==len(summarize_menu_items)-1: text=text
        else: text=list(text.values())[0]

    elif summarize_sel == 1:
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
        summarized_text = text_splitter(text, level_sel, key)

    summarize_menu_title = "\n Run completed! How would you like your output?\n"
    summarize_menu_items = ["Printed to console",
                            "Written to file",
                            ]
    summarize_menu_cursor = "> "
    summarize_menu_cursor_style = ("fg_yellow", "bold")
    summarize_menu_style = ("italics", "bg_purple")
    summarize_menu_exit = False

    summarize_menu = TerminalMenu(
        menu_entries=summarize_menu_items,
        title=summarize_menu_title,
        menu_cursor=summarize_menu_cursor,
        menu_cursor_style=summarize_menu_cursor_style,
        menu_highlight_style=summarize_menu_style,
        cycle_cursor=True
    )
    ans_output = summarize_menu.show()

    if ans_output==0:
        for summa in summarized_text:
            transform(text, summa, pyfiglet.figlet_format("Summarizer", font = "stampatello"), "yellow")

        os.system('clear')
        print(stylize("\n{}".format(pyfiglet.figlet_format("Summarizer", font = "stampatello")),colored.attr("bold")+colored.fg('yellow')))
        for summa in summarized_text:
            print(summa,'\n')
        
        rating = input(stylize(" Please rate the output:\n [1-10] ",colored.fg("yellow")))
        input(stylize("\n Press Enter to continue...",colored.fg("yellow")))

        return

    if ans_output==1:
        with open("../output/summarized_text.txt", "w") as f:
            print(stylize("\n{}".format(pyfiglet.figlet_format("Summarizer", font = "stampatello")),colored.attr("bold")+colored.fg('yellow')))
            print(" Write out successful.\n")
            for summa in summarized_text:
                print(summa,'\n')    
            input(stylize(" Press Enter to continue...",colored.fg("yellow")))

            return

    return

if __name__=="__main__":
    summarizer()

