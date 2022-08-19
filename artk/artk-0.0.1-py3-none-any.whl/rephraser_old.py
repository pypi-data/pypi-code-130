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

def text_splitter(text, key):
    maxlen = 10000
    
    if len(text) > maxlen:
        o1,o2,o3 = rephrase(text[:maxlen], key)
        output1.append(o1)
        output2.append(o2)
        output3.append(o3)
        text_splitter(text[maxlen+1:], key)
    else:
        o1,o2,o3 = rephrase(text, key)
        output1.append(o1)
        output2.append(o2)
        output3.append(o3)

    return " ".join(output1), " ".join(output2), " ".join(output3)

def rephrase(text, levels, key):
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
          presence_penalty=0)["choices"][0]["text"]#.\
            #replace("\n", "").replace('"', '').strip()
        print(result1)
        result.append(stylize(" Max simplification: \n",colored.attr("bold"))+result1)

    if (levels==1) or (levels==3):
        # level 2
        result2 = openai.Completion.create(
          engine=engine_type,
          prompt=quest2+text,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0)["choices"][0]["text"].\
            replace("\n", "").replace('"', '').strip()
        result.append(stylize(" Intermediate: \n",colored.attr("bold"))+result2)

    if (levels==2) or (levels==3):
        # level 3 
        result3 = openai.Completion.create(
          engine=engine_type,
          prompt=quest3+text,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0)["choices"][0]["text"].\
            replace("\n", "").replace('"', '').strip()
        result.append(stylize(" Advanced: \n",colored.attr("bold"))+result3)

    return result


def rephraser():
    key = input("\n The Rephraser is an AI-based tool requiring an OpenAI API key.\n For instructions on acquiring a key, visit the Help page.\n Please enter your API key or type \'Demo\' to continue:\n\n ")

    rephrase_menu_title = "\n Select an input method:\n"
    rephrase_menu_items = ["arXiv",
                       "Raw text",
                       "Exit"]
    rephrase_menu_cursor = "> "
    rephrase_menu_cursor_style = ("fg_cyan", "bold")
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
        pdf = input("\n Enter arXiv link: ")
        #pdf = "https://arxiv.org/pdf/1811.05477.pdf"
        
        rephrase_menu_title = "\n What would you like to summarize?\n"
        rephrase_menu_items = ["Abstract",
                               "Full text"]
        rephrase_menu_cursor = "> "
        rephrase_menu_cursor_style = ("fg_cyan", "bold")
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

    elif rephrase_sel == 1:
        text = input("\n Enter text: ")

    print("\n Processing...")
    with alive_bar(bar=None, spinner='fishes', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
         if rephrase_sel == 0:
             text = extract_text(pdf, key)
             if ans==0: text = text['abstract']
         a,b,c = text_splitter(text, key)

    rephrase_menu_title = "\n Run completed! How would you like your output?\n"
    rephrase_menu_items = ["Printed to console",
                           "Written to file"]
    rephrase_menu_cursor = "> "
    rephrase_menu_cursor_style = ("fg_cyan", "bold")
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
        transform(text, a, pyfiglet.figlet_format("Rephraser", font = "stampatello"), "Max simplification", "cyan")
        transform(text, b, pyfiglet.figlet_format("Rephraser", font = "stampatello"), "Intermediate", "cyan")
        transform(text, c, pyfiglet.figlet_format("Rephraser", font = "stampatello"), "Advanced", "cyan")

        os.system('clear')
        print(stylize("\n{}".format(pyfiglet.figlet_format("Rephraser", font = "stampatello")),colored.attr("bold")+colored.fg('cyan')))
        print(stylize(" Max simplification: \n",colored.attr("bold")), a,'\n')
        print(stylize(" Intermediate: \n",colored.attr("bold")), b,'\n')
        print(stylize(" Advanced: \n",colored.attr("bold")), c,'\n')
        input(stylize(" Press Enter to continue...",colored.fg("cyan")))

        return

    if ans_output==1:
        with open("../output/rephrased_text.txt", "w") as f:
            print(stylize("\n{}".format(pyfiglet.figlet_format("Rephraser", font = "stampatello")),colored.attr("bold")+colored.fg('cyan')))
            print(" Write out successful.\n")
            print(stylize(" Max simplification: \n",colored.attr("bold")), a,'\n', file=f)
            print(stylize(" Intermediate: \n",colored.attr("bold")), b,'\n', file=f)
            print(stylize(" Advanced: \n",colored.attr("bold")), c,'\n', file=f)
            input(stylize(" Press Enter to continue...",colored.fg("cyan")))

            return

    return

if __name__=="__main__":
    rephraser()
