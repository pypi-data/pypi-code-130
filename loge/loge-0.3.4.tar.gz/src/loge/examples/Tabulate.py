from tabulate import tabulate
#! *Working with tabulate*
#! See more about Tabulate use at https://github.com/astanin/python-tabulate

table = [["spam",42],["eggs",451],["bacon",0]]
headers = ["item", "qty"]
tabulate_tab = tabulate(table, headers, tablefmt="fancy_grid") #%tab