from simple_term_menu import TerminalMenu
import sys
#from utilites.trend_catcher import grants, papers
#from questioner import presentations, papers, general
from artk.related_papers import related_papers
from artk.idea_generator import idea_generator
from artk.coder import coder
from artk.rephraser import rephraser 
from artk.summarizer import summarizer
import colored
from colored import stylize
import os

def main_menu():
    os.system('clear')
    menu_title = "\n Select a research tool:\n"
    menu_items = ["Rephraser",
                  "Related papers",
                  "Summarizer",
                  "Idea generator",
                  "Coding assistant",
                  "Audience members",
    	          "Answerer",
    	          "Pocker pushers",
                  "Paper pinger",
                  "Trend catcher",
                  "Help",
                  "Quit"]
    menu_cursor = "> "
    menu_cursor_style = ("fg_red", "bold")
    menu_style = ("italics", "bg_purple")
    menu_exit = False

    menu = TerminalMenu(
        menu_entries=menu_items,
        title=menu_title,
        menu_cursor=menu_cursor,
        menu_cursor_style=menu_cursor_style,
        menu_highlight_style=menu_style,
        cycle_cursor=True
    )

    main_sel = menu.show()
 
    if main_sel == 0:
        rephraser()
        main_menu()
    elif main_sel == 1:
        related_papers()
        main_menu()
    elif main_sel == 2:
        summarizer()
        main_menu()
    elif main_sel == 3:
        idea_generator()
        main_menu()
    elif main_sel == 4:
        coder()
        main_menu()
