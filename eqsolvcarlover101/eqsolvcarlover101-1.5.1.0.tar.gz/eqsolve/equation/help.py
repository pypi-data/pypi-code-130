class help():
  def __init__(self):
    import os
    if os.name == "nt":
      os.system("cls")
    else:
      os.system("clear")
    print("Type eqsolve.commands() to get started or read the README.md file for more information.")