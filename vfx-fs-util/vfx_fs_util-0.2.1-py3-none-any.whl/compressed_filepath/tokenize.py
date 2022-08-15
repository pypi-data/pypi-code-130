import re
import lucidity
from string import Formatter


class TokenParseError(Exception):
    """When the tokenizer cannot parse tokens from a string"""
    
    
class TokenStringFormatError(Exception):
    """When a token string cannot be formatted"""


class Tokenizer(object):
    """Tokenizer is meant to take strings and parse elements/tokens from them.
    (Similar to using re.MatchObject.groupdict())
    
    Example:
        >>> input_string = "hello this is a test"
        >>> token_string = "{first} this is a {last}"
        >>> Tokenizer.tokenize(token_string, [token_string], token_regex='\\w+')
        {'first': 'hello', 'last': 'test'}
    """
    
    DEFAULT_TOKEN_REGEX=r'\d+'

    @staticmethod
    def tokenize(
        input_string, token_strings, token_regex=None, anchor=None, raise_error=True
    ):
        """Given a list of token patterns, parse and tokenize a string.

        Args:
            input_string (str): String to be parsed.
            token_strings (list): List of token patterns to parse
            token_regex (str, optional): You can decide what regex each token pattern uses or define a default. 
                Defaults to Tokenizer.DEFAULT_TOKEN_REGEX.
            anchor (bool, optional): Where in the string should the pattern achor to. 
                Defaults to None.
            raise_error (bool, optional): raise TokenParseError or return empty dict. 
                Defaults to False.
            
        Example:
            >>> token_strings = ["%{padding}d", "{first}-{last}"]
            >>> input_string = "abc_%05d1001-1005_def_%04d_ghi"
            >>> Tokenizer.tokenize(input_string, token_strings)
            {'padding': '04', 'first': '1001', 'last': '1005'}
            >>> # Note that all token strings are evaluated
            >>> # The last occurance of a match is what will be returned at a given key

        Raises:
            TokenParseError: If there is an issue parsing all tokens from the input string
            
        Returns:
            dict: token names to parsed values
        """

        if not token_regex:
            token_regex = Tokenizer.DEFAULT_TOKEN_REGEX

        token_keys = set()
        for token_string in token_strings:
            keys = {
                i[1] for i in Formatter().parse(token_string) if i[1] is not None
            }
            token_keys.update(keys)
        
        parsed = {}
        templates = []
        for i, template_string in enumerate(token_strings):
            templates.append(
                lucidity.Template(
                    name=i,
                    pattern=template_string,
                    anchor=anchor,
                    default_placeholder_expression=token_regex
                )
            )

        for template in templates:
            try:
                parsed.update(template.parse(input_string))
            except lucidity.ParseError:
                pass

        if raise_error:
            missing = token_keys - set(parsed.keys())
            if missing:
                raise TokenParseError(
                    'Unable to parse the following tokens: {}'.format(missing)
                )

        return parsed

    @staticmethod
    def format(input_string, token_data, anchor=None):
        """Given a token string and key value pairs, format the string

        Args:
            input_string (str): String to format.
            token_data (dict): key value pairs to be plugged into the input string
            anchor (bool, optional): Where in the string should the pattern achor to.
                Defaults to None.

        Returns:
            str: formatted string
        """
        
        data = {k: str(v) for k,v in token_data.items()}
        
        template = lucidity.Template(
            name='tmp',
            pattern=input_string,
            anchor=anchor,
            default_placeholder_expression=Tokenizer.DEFAULT_TOKEN_REGEX
        )
        try:
            return template.format(data)
        except lucidity.error.FormatError as e:
            raise TokenStringFormatError(e)

    @staticmethod
    def to_regex(input_string, token_regex=None):
        """Given a string, replace all possible tokens with regexes
        
        Args:
            input_string (str): String presumably containing tokens
            token_regex (str, optional): Regex to replace the token with. 
                Defaults to Tokenizer.DEFAULT_TOKEN_REGEX.
            
        Example:
            >>> string = "I am {tesing} 123"
            >>> Tokenizer.to_regex(string, token_regex=r'\\w+')
            "I am \\w+ 123"

        Returns:
            str: A string where tokens have been replaced with regexes
        """
        
        if not token_regex:
            token_regex = Tokenizer.DEFAULT_TOKEN_REGEX

        regex = input_string
        broken_out_token_strings = {}
        for parsed in Formatter().parse(input_string):
            # parse(format_string) method of string.Formatter instance
            # returns an iterable that contains tuples of the form:
            # (literal_text, field_name, format_spec, conversion)
            # literal_text can be zero length
            # field_name can be None, in which case there's no
            #  object to format and output
            # if field_name is not None, it is looked up, formatted
            #  with format_spec and conversion and then used
            # example: [('', 'first', '\\d+', None), ('-', 'last', '\\d+', None)]
            if parsed[1] is not None:
                broken_out_token_strings[parsed[1]] = parsed[2]
                
        for k, v in broken_out_token_strings.items():
            if v:
                string = '{{{}:{}}}'.format(k, v)
                regex = regex.replace(string, v)
            else:
                string = '{{{}}}'.format(k)
                regex = regex.replace(string, token_regex)
            
        regex = regex.replace('$', r'\$')
        regex = regex.replace('*', r'\*')

        return regex

    @staticmethod
    def find_all(input_string, token_string, token_regex=None):
        """Find all token pattern occurances in a string.

        Args:
            input_string (str): Input string to parse
            token_string (str): Token string representing a pattern
            token_regex (str, optional): The regex used for parsing. Defaults to Tokenizer.DEFAULT_TOKEN_REGEX.
            
        Example:
            >>> input_string = "abc_%05d_def_%04d_ghi"
            >>> token_string = "%{padding}d"
            >>> Tokenizer.find_all(input_string, token_string)
            ['%05d', '%04d']

        Returns:
            list: All matched occurances of a token pattern
        """
        if not token_regex:
            token_regex = Tokenizer.DEFAULT_TOKEN_REGEX

        token_string = Tokenizer.to_regex(token_string, token_regex=token_regex)
        return re.findall(token_string, input_string, flags=re.I)
