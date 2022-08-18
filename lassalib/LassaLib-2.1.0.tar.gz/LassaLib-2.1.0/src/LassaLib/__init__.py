"""Convenient function set"""

try:
    import text_editing

    COLOR = True
except ModuleNotFoundError:
    COLOR = False

import typing


def enter(__prompt='', __type=int):
    """
    This function allows to input any type
    :param __prompt: Text to print before recovery
    :type __prompt: str
    :param __type: The type to recover
    :type __type: type
    :return: The input in the requested type
    :rtype: bool or complex or float or int or list or set or slice or str or property or type
    :raise TypeError: If __type is not in return type.
    """
    if __type not in [
        bool, complex, float, int, list, set, slice, str,
        property, type
    ]:
        raise TypeError(f'{__type} is not a possible type.')
    var: str = input(__prompt)
    while True:
        try:
            '''  '''
            if __type == bool:
                if var.lower() in [
                    "yes", "是的", "हां", "sí", "si", "نعم", "হ্যাঁ", "oui", "да", "sim", "جی ہاں",
                    "y", "1", "true"
                ]:
                    return True
                elif var.lower() in [
                    "no", "不", "नहीं", "no", "لا", "না", "non", "нет", "não", "nao", "نہیں",
                    "n", "0", "false"
                ]:
                    return False
                else:
                    raise ValueError(f"could not convert string to bool: '{var}'")
            return __type(var)
        except ValueError:
            print(f"\"{var}\" is not the type {__type.__name__}")
            var: str = input(__prompt)


def last_iteration(iteration_text, txt):
    """
    Return the index of the last iteration on string.
    :param iteration_text: The searched iteration
    :type iteration_text: str
    :param txt: The variable to search in.
    :type txt: str or list
    :return: The index of last iteration.
    :rtype: int
    """
    if isinstance(txt, str):
        liste = txt.split(iteration_text)
    else:
        liste = txt

    if len(liste) == 1:
        return None
    else:
        return len(txt) - (len(liste[-1]) + len(iteration_text))


def menu(choices, prompt, can_back, title, desc=None):
    """Create a menu

    :param title: Title of menu
    :type title: str
    :param desc: Description of menu
    :type desc: str
    :param choices: The liste of choice
    :type choices: list
    :param prompt: The prompt before choice
    :type prompt: str
    :param can_back: Menu affiche back choice at 0)?
    :type can_back: bool
    :return: The index of choice with 'Back' in index 0 and other index + 1
    :rtype: int
    """

    """
    Modèle:
           ╔═════════════╗       
    ╔══════╣ Nom du menu ╠══════╗
    ║      ╚═════════════╝      ║
    ║ ┌───────────────────────┐ ║
    ║ │  Description du menu  │ ║
    ║ └───────────────────────┘ ║
    ║                           ║
    ║ ┌───┐ ┌────────────────┐  ║
    ║ │ 1 ├─┤ Texte du choix │  ║
    ║ └───┘ └────────────────┘  ║
    ║ ┌───┐ ┌────────────────┐  ║
    ║ │ 2 ├─┤ Texte du choix │  ║
    ║ └───┘ └────────────────┘  ║
    ╟---------------------------╢
    ║ ┌───┐ ┌────────┐          ║
    ║ │ 0 ├─┤ Retour │          ║
    ║ └───┘ └────────┘          ║
    ╚═══════════════════════════╝
    """

    def choice_button(num, texte):
        """Create a button of choice"""
        ln = length_num
        lt = length_choice

        num = position('right', str(num), ln, ' ')
        texte = position('center', texte, lt, ' ')

        u = position('left', f" ┌──" + ("─" * ln) + "┐ ┌──" + ("─" * lt) + "┐ ", largeur - 2, ' ')
        m = position('left', f" │ {num} ├─┤ {texte} │ ", largeur - 2, ' ')
        b = position('left', f" └──" + ("─" * ln) + "┘ └──" + ("─" * lt) + "┘ ", largeur - 2, ' ')

        return (
                "║" + u + "║\n" +
                "║" + m + "║\n" +
                "║" + b + "║"
        )

    largeur_choice = max([len(desc) for desc in choices])
    largeur_desc = max([len(word) for word in desc.split()]) if desc else 0
    length_num = len(str(len(choices)))
    largeur = max(
        18,
        len(f"╔══╣  {title}  ╠══╗"),
        len(f"║ │ {' ' * length_num} ├─┤ {' ' * largeur_choice} │ ║"),
        len(f"║ │ {' ' * largeur_desc} │ ║")
    )
    length_choice = largeur - 13 - len(str(len(choices)))

    back_button = (
            "║" + position('left', " ┌───┐ ┌──────┐ ", largeur - 2, ' ') + "║\n" +
            "║" + position('left', " │ 0 ├─┤ Back │ ", largeur - 2, ' ') + "║\n" +
            "║" + position('left', " └───┘ └──────┘ ", largeur - 2, ' ') + "║"
    )

    # =-= =-= =< Menu >= =-= =-=
    print(position('center', f"╔══{'═' * len(title)}══╗", largeur, ' '))
    print("╔" + position('center', f"══╣  {title}  ╠══", largeur - 2, '═') + "╗")
    print("║" + position('center', f"╚══{'═' * len(title)}══╝", largeur - 2, ' ') + "║")

    if desc:
        desc_lines = ['']
        for word in desc.split():
            if len(f"║ │ {desc_lines[-1]} {word} │ ║") > largeur:
                desc_lines.append(word)
            else:
                desc_lines[-1] += f" {word}"

        print(f"║ ┌{'─' * (largeur - 6)}┐ ║")
        for line in desc_lines:
            print(f"║ │ {line.center(largeur - 8, ' ')} │ ║")
        print(f"║ └{'─' * (largeur - 6)}┘ ║")
        print(f"║{' ' * (largeur - 2)}║")

    i = 1
    for choice in choices:
        print(choice_button(i, choice))
        i += 1

    if can_back:
        print("╟" + '-' * (largeur - 2) + "╢")
        print(back_button)
    print("╚" + '═' * (largeur - 2) + "╝")

    chx = enter(prompt + ' ')
    while chx not in range(0 if can_back else 1, len(choices) + 1):
        print(f'"{chx}" not in possibility')
        chx = enter(prompt + ' ')
    return chx


def position(pos, txt, length, fill):
    """Push in the position the text with correct length

    :type pos: str
    :type txt: str
    :type length: int
    :type fill: str
    :rtype: str
    """
    if pos == 'center':
        return txt.center(length, fill)
    else:
        while len(txt) < length:
            if pos == 'right':
                txt = fill + txt
            else:
                txt += fill
    return txt


def replace_last(sub_string: str, new_string: str, string: str) -> str:
    """
    Replaces the last iteration of the substring entered with the string chosen in the quoted string.
    :param sub_string: The substring entered.
    :param new_string: The string chosen.
    :param string: The quoted string.
    :return: The quoted string with the last iteration of the substring replaced by the chosen string.
    """
    li = last_iteration(sub_string, string)
    if li is None:
        return string
    return string[0:li] + new_string + string[li + len(sub_string):]


def show_value(value: typing.Any, tab_number: int = 0) -> None:
    """
    Prints in the terminal all the elements of a list, a dictionary or a tuple and its sub-elements.
    Prints in the terminal the other types and class.
    :param value: A value of any type or class.
    :param tab_number: The default number of tabs to put in front of the printout.
    :return: None
    """

    def sort_key(dico):
        """Sort values alphabetically

        :param dico: The dico
        :return: the sorted dico
        """
        if isinstance(dico, dict):
            liste_key = list(dico.keys())
            sorted_liste_key = []
            while len(liste_key) > 0:
                best = liste_key[0]
                for key_from_list in liste_key:
                    i = 0
                    stop = False
                    while i < min(len(str(best)), len(str(key_from_list))) and not stop:
                        if ord(str(best)[i]) > ord(str(key_from_list)[i]):
                            best = key_from_list
                            stop = True
                        elif ord(str(best)[i]) < ord(str(key_from_list)[i]):
                            stop = True
                        i += 1
                    if not stop:
                        if len(str(key_from_list)) < len(str(best)):
                            best = key_from_list
                liste_key.remove(best)
                sorted_liste_key.append(best)
            return sorted_liste_key
        else:
            return []

    if isinstance(value, list) or isinstance(value, dict) or isinstance(value, tuple):
        print(f"{text_editing.color.COLOR_PURPLE if COLOR else ''}{type(value).__name__}", end="")
        print(f" ({len(value)} items):")
        for key in (sort_key(value) if isinstance(value, dict) else range(len(value))):
            print("\t" * tab_number + f"\t{text_editing.color.COLOR_GREEN if COLOR else ''}{key}: ", end='')
            show_value(value[key], tab_number + 1)
    else:
        print(str_object(value))


def space_number(number: typing.Union[int, float], spacing: str = ' ') -> str:
    """
    Separate with character defines the number entered every 3 digits.
    :param number: A value.
    :param spacing: A character.
    :return: A string of number separate.
    """
    if isinstance(number, int):
        number_list = list(str(number))
        txt = ""
        i = 0
        while len(number_list) != 0:
            if i == 3:
                i = 0
                txt = spacing + txt
            txt = number_list.pop() + txt
            i += 1
        return txt
    else:
        return space_number(int(number), spacing) + '.' + str(number).split('.')[1]


def str_object(obj: typing.Any, tab: int = 0, pass_: bool = False) -> str:
    """
    Create a string of all info about an object regardless of its class.
    :param obj: An object from Any type or class.
    :param tab:
    :param pass_: If pass the name of type
    :return: A string that summarizes the object in detail.
    """
    try:
        max_key_length = max([len(key) for key in obj.__dict__])
        max_type_length = max([len(str(type(obj.__dict__[key]).__name__)) for key in obj.__dict__])
        txt = ('\t' * tab + f"{text_editing.color.COLOR_PURPLE if COLOR else ''}"
                            f"{obj.__class__.__name__} : \n") if not pass_ else '\n'

        for key in obj.__dict__:
            txt += '\t' * tab + f"\t - {key.center(max_key_length, ' ')} " \
                                f"({str(type(obj.__dict__[key]).__name__).center(max_type_length)}) : " \
                                f"{str_object(obj.__dict__[key], tab + 1, True)}\n"

        return txt[:-1]
    except Exception as e:
        str(e)
        txt = ('\t' * tab + f"{text_editing.color.COLOR_YELLOW if COLOR else ''}"
                            f"{obj.__class__.__name__} : ") if not pass_ else ''
        txt += f"{text_editing.color.COLOR_GREEN if COLOR else ''}" \
               f"{str(obj)}"
        return txt
