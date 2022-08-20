__version__ = '0.1.2'

from .colors import Back256, Fore256, XtermCodes, XtermColor
from .utils import (
    calculate_distance_matrix,
    find_differentiated_colors,
    print_all_colors,
    print_color_table,
    print_colors,
    print_differentiated_colors,
)

__all__ = [
    'Back256',
    'Fore256',
]
