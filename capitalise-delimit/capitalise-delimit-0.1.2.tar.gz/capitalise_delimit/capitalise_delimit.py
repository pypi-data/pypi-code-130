from typing import Union


class CapitaliseDelimit:
    # list of popular syncategorematic words that may not always want to be capitalised
    default_words_to_ignore = {'upon', 'at', 'the', 'on', 'in'}

    def __init__(self, delimiters: Union[list[str], set[str]]):
        # self.delimiters converted to set to ensure uniqueness of elements and back to list for use
        self.delimiters = self.__make_set_of_strings(delimiters, 'delimiters')
        self.delimiters = list(delimiters)
        self.ignore_words = False
        self.custom_words_to_ignore = set()

    def capitalise(self, string: str, ignore_words: bool = None,
                   custom_ignore_words: Union[list[str], set[str]] = None) -> str:
        """
        'do_capitalise' called separately as it is a recursive function and the parameter 'string' it takes in is
        modified upon each invocation
        :param string: the string to capitalise
        :param ignore_words: boolean specifying if to ignore (i.e. don't capitalise) the defined list
        of syncategorematic words
        :param custom_ignore_words: custom set of words to ignore during capitalisation. Can be used in conjunction
        with or instead of the predefined set of words
        :return: capitalised form of string
        """
        if not isinstance(string, str):
            raise TypeError(f"Please provide a string to be capitalised ({type(string)} provided)")
        if ignore_words is not None:
            if not isinstance(ignore_words, bool):
                raise TypeError(
                    f"Please provide a boolean value for the 'ignore_words' parameter ({type(ignore_words)} provided)")
            else:
                self.ignore_words = ignore_words

        words_to_ignore = set()
        if self.ignore_words:
            words_to_ignore.update(self.default_words_to_ignore)
        if custom_ignore_words:
            custom_ignore_words = self.__make_set_of_strings(custom_ignore_words, 'custom ignore words')
            custom_ignore_words = {word.lower() for word in custom_ignore_words}
            self.custom_words_to_ignore = custom_ignore_words
        """
        words_to_ignore is always updated with self.custom_words_to_ignore as the custom list is saved and used for 
        every capitalisation, hence why this is outside the if block
        """
        words_to_ignore.update(self.custom_words_to_ignore)
        return self.__do_capitalise(string, self.delimiters, words_to_ignore)

    @staticmethod
    def __do_capitalise(string, delimiters: list[str], words_to_ignore: set[str]) -> str:
        """
        Recursively split string by given delimiters, then capitalise individual parts before joining them back together
        with the delimiter that the string was split by
        :param string: string to capitalise, becomes list as recursion occurs
        :param delimiters: list of delimiters to split and capitalise string by
        :return: capitalised string
        """
        if len(delimiters) == 0:
            if string not in words_to_ignore:
                if len(string) > 1:
                    string = string.capitalize()
                else:
                    string = string.capitalize()
        else:
            string = string.split(delimiters[0])
            for s in range(len(string)):
                string[s] = CapitaliseDelimit.__do_capitalise(string[s], delimiters[1:], words_to_ignore)
            string = f'{delimiters[0]}'.join(string)
        return string

    @staticmethod
    def __make_set_of_strings(items, param_name) -> set:
        try:
            items = set(items)
            if not all(isinstance(item, str) for item in items):
                raise TypeError
        except TypeError:
            raise TypeError(f"Please ensure the parameter provided for {param_name} is a list/set of strings only")
        return items
