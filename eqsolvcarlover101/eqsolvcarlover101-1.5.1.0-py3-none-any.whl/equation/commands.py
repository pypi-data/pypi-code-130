class commands():
  def __init__(self):
    import os
    if os.name == "nt":
      os.system("cls")
    else:
      os.system("clear")
    print("The commands are: \neqsolve.quadsolve() - For quadratic equations. \neqsolve.slopeint() - For slope-intercept equations. \neqsolve.midpoint() - For finding the midpoint of two points. \neqsolve.perpint() - Takes a slope and an intersection point and returns the slope-intercept equation of the perpendicular line. \neqsolve.issim() - Takes the lengths of the sides of one shape and the corresponding sides of a second shape and calculates if they are similar. \neqsolve.findright() - Finds the missing length of a right triangle. \neqsolve.help() - Brings up the help page.")