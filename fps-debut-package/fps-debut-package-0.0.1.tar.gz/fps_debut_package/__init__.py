## Specify the functions you want importable.
## from module(in same directory) import function.

from .functions import average, power
from .greet import SayHello

## from packagename import power, average, SayHello
## Note that functions power() and SayHello() are imported from the package and not from their respective modules, as done earlier, because it has been specified in the __init__.py file.