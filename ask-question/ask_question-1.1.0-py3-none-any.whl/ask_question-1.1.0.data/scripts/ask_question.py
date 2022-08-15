##
## EPITECH PROJECT, 2022
## Desktop_pet (Workspace)
## File description:
## ask_question.py
##

"""
The file containing the code to speed up the boiling
process that occurs when a question is asked.
This module is provided as if and without any warranty
Crediting the author is appreciated.
"""

__Version__ = "1.1.0"
__Author__ = "(c) Henry Letellier"

from string import printable
class AskQuestion:
    """ An advanced function that contains boiling to gain time when asking a question """
    def __init__(self, human_type:dict={}, illegal_characters_nb:str="") -> None:
        """ The globals for the class """
        self.human_type = human_type
        self.illegal_characters_nb = illegal_characters_nb
        self.author = "(c) Henry Letellier"
        self.version = "1.0.0"
        self.check_load()

    def check_load(self) -> None:
        """ Check that the ressources are present """
        if self.human_type == dict():
            self.human_type = {
            "int":"whole number (-1, 0, 1, 2, 3, etc...)",
            "float":"floating number (-1.2, 0.1, 1.2, etc...)",
            "uint":"whole positive number (0, 1, 2, etc...)",
            "ufloat":"whole positive floating number (0.1, 1.2, etc ...)",
            "num":"numeric (numbers from 0 onwards)",
            "alnum":"alphanumeric (only numbers and the alphabet)",
            "isalpha":"alphabet (from a to z and A to Z)",
            "char":"alphabet (from a to z and A to Z)",
            "ascii":"ascii Table",
            "str":"string (any character you can type)",
            "version":"version (numbers seperated by '.' characters)",
            "ver":"version (numbers seperated by '.' characters)",
            "bool":"boolean (yes/True/1 or no/False/0 answer type)",
            }
        if self.illegal_characters_nb == "":
            self.illegal_characters_nb = printable.replace("-", "")
            self.illegal_characters_nb = self.illegal_characters_nb.replace(".", "")
            self.illegal_characters_nb = self.illegal_characters_nb.replace(",","")
            self.illegal_characters_nb = self.illegal_characters_nb.replace("+","")
            self.illegal_characters_nb = self.illegal_characters_nb.replace("0123456789","")


    def is_empty(self, string:str) -> bool:
        """ Check if the string is not empty """
        if len(string) == 0:
            return True
        return False

    def is_version(self, string:str) -> bool:
        """ Check if the given string is a version """
        string_length = len(string)-1
        for i in enumerate(string):
            if i[1].isdigit() == False:
                if i[0] == string_length and (i[1] == '.' or i[1] == ','):
                    return False
                if i[1] != "." and i[1] != ",":
                    return False
        return True

    def contains_illegal_characters(self, string:str, illegal_characters:str) -> bool:
        """ Check if there are no forbidden characters in a string destined to be converted to a number """
        for i in string:
            if i in illegal_characters:
                return True
        return False

    def remove_char_overflow(self, string:str, char:str, presence_tolerance:int=1, case_sensitive:bool=False) -> str:
        """ Remove the number of times a specific character appears in a string after the allowed number of times """
        result = ""
        for i in string:
            if case_sensitive == False:
                if i.lower() == char:
                    if presence_tolerance > 0:
                        result+=i
                        presence_tolerance-=1
                else:
                    result+=i
            else:
                if i == char:
                    if presence_tolerance > 0:
                        result+=i
                        presence_tolerance-=1
                else:
                    result+=i
        return result

    def clean_number(self, string:str, char:str=".", tolerance:int=1, case_sensitive:bool=False) -> str:
        """ Remove content that should not be in a number input """
        if " " in string:
            string = string.replace(" ", "")
        if "," in string:
            string = string.replace(",",".")
        if string.count(char) > tolerance:
            string = self.remove_char_overflow(string, char, tolerance, case_sensitive)
        return string


    def ask_question(self, question:str, answer_type:str) -> (str or int or float):
        """ Ask a question and continue asking until type met """
        answer_found = False
        while answer_found == False:
            answer = input(str(question))
            if self.is_empty(answer) == False and answer.isspace() == False and answer.isprintable() == True:
                contains_illegal_characters = self.contains_illegal_characters(answer, self.illegal_characters_nb)
                if answer.isalnum() == True and "alnum" in answer_type:
                    return answer
                if answer.isalpha() == True and "char" in answer_type:
                    return answer
                if answer.isdigit() == True and "num" in answer_type:
                    return float(answer)
                if answer.isascii() == True and ("ascii" in answer_type or "str" in answer_type):
                    return answer
                if "up" in answer_type:
                    return answer.upper()
                if "low" in answer_type or "down" in answer_type:
                    return answer.lower()
                if "version" in answer_type or "ver" in answer_type and self.is_version(answer) == True:
                    return answer
                if "uint" in answer_type and answer.isdigit() == True:
                    answer = self.clean_number(answer, ".", 0, False)
                    return int(answer)
                if "ufloat" in answer_type and answer.isdigit() == True:
                    answer = self.clean_number(answer, ".", 1, False)
                    return float(answer)
                if "bool" in answer_type:
                    answer_l = answer.lower()
                    if "y" in answer_l or "t" in answer_l or "1" in answer_l:
                        return True
                    elif "n" in answer_l or "f" in answer_l or "0" in answer_l:
                        return False
                    else:
                        answer_l = None
                if "int" in answer_type and "uint" not in answer_type and contains_illegal_characters == False:
                    answer = self.clean_number(answer, ".", 0, False)
                    answer = self.remove_char_overflow(answer, "-", 1, False)
                    try:
                        return int(answer)
                    except TypeError:
                        continue
                    except BaseException:
                        continue
                if "float" in answer_type and "ufloat" not in answer_type and contains_illegal_characters == False:
                    answer = self.clean_number(answer, ".", 0, False)
                    answer = self.remove_char_overflow(answer, "-", 1, False)
                    try:
                        return float(answer)
                    except TypeError:
                        continue
                    except BaseException:
                        continue
                print(f"Please enter a response of type '{self.human_type[answer_type]}'")
            else:
                print("Response must not be empty or only contain spaces or any non visible character.")
    def pause(self, pause_message:str="Press enter to continue...") -> None:
        """ Act like the windows batch pause function """
        empty=""
        pause_response = input(pause_message)
        empty+=pause_response

if __name__ == "__main__":
    AQI = AskQuestion(dict(), "")
    answer = AQI.ask_question("How old are you?", "uint")
    ADD_S = ""
    if answer > 1:
        ADD_S = "s"
    print(f"You are {answer} year{ADD_S} old")
    AQI.pause()
