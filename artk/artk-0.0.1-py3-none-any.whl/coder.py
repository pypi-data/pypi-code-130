from simple_term_menu import TerminalMenu
import autopep8
import openai 
from alive_progress import alive_bar
import colored
from colored import stylize
import warnings
import pyfiglet
from artk.transform import transform
import os
import keyboard
warnings.filterwarnings("ignore")

def generate_code(lang, task, key):
    openai.api_key = key

    engine_type='text-davinci-002'
    #engine_type='text-curie-001'
    quest1 = "Write {} code that does the following:\n".format(lang)+task+"\n\n"

    # level 1
    result1 = openai.Completion.create(
      engine=engine_type,
      prompt=quest1,
      temperature=0.7,
      max_tokens=1500,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0)["choices"][0]["text"]

    return result1 

def coder():
    key = input("\n The Coding Assistant is an AI-based tool requiring an OpenAI API key.\n For instructions on acquiring a key, visit the Help page.\n Please enter your API key or type \'Demo\' to continue:\n\n ")

    coder_menu_title = "\n Which language would you like to use?\n"
    coder_menu_items = ["Python",
                           "C++",
                        "Back to menu"]
    coder_menu_cursor = "> "
    coder_menu_cursor_style = ("fg_green", "bold")
    coder_menu_style = ("italics", "bg_purple")
    coder_menu_exit = False

    coder_menu = TerminalMenu(
        menu_entries=coder_menu_items,
        title=coder_menu_title,
        menu_cursor=coder_menu_cursor,
        menu_cursor_style=coder_menu_cursor_style,
        menu_highlight_style=coder_menu_style,
        cycle_cursor=True
    )

    ans = coder_menu.show()

    if ans==0:
        task = input("\n Enter a task to program:\n"+stylize(" Some examples include\n   Compute the cosmological matter power spectrum\n   Given two datasets, build a support vector machine\n\n ",colored.attr('dim')))

        print("\n Processing...")
        with alive_bar(bar=None, spinner='fish2', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
             a = autopep8.fix_code(generate_code("Python", task, key))
        
        coder_menu_title = "\n Run completed! How would you like your output?\n"
        coder_menu_items = ["Printed to console",
                            "Written to file"]
        coder_menu_cursor = "> "
        coder_menu_cursor_style = ("fg_green", "bold")
        coder_menu_style = ("italics", "bg_purple")
        coder_menu_exit = False

        coder_menu = TerminalMenu(
            menu_entries=coder_menu_items,
            title=coder_menu_title,
            menu_cursor=coder_menu_cursor,
            menu_cursor_style=coder_menu_cursor_style,
            menu_highlight_style=coder_menu_style,
            cycle_cursor=True
        )
        ans = coder_menu.show()
        
        if ans==0:
            transform("", a, pyfiglet.figlet_format("Coding assistant", font = "stampatello"), "Python", "green")

            #os.system('clear')
#            print(stylize("\n {}".format(pyfiglet.figlet_format("Rephraser", font = "stampatello")),colored.attr("bold")+colored.fg('cyan')))
#            print(stylize(" Max simplification: \n",colored.attr("bold")), a,'\n')
#            print(stylize(" Intermediate: \n",colored.attr("bold")), b,'\n')
#            print(stylize(" Advanced: \n",colored.attr("bold")), c,'\n')                
            input(stylize(" Press Enter to continue...",colored.fg("green")))

            return

    elif ans==2:
        return
