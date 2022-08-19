from dateutil.parser import parse


def is_date(input_string: str, fuzzy: bool = False) -> bool:
    """This function checks whether in the input string there is a date
    Args:
        input_string: string to check for date
        fuzzy: ignore unknown tokens in string if True
    Returns:
         True: whether the string can be interpreted as a date.
         False: otherwise
    """
    try:
        parse(input_string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def keep_only_digits(input_string: str) -> str:
    """This function takes as input a string and returns the same string but only containing digits
    Args:
        input_string: the input string from which we want to remove non-digit characters
    Returns:
        output_string: the output string that only contains digit characters
    """
    numeric_filter = filter(str.isdigit, input_string)
    output_string = "".join(numeric_filter)

    return output_string


def load_txt_file_as_string(path_txt_file: str) -> str:
    """This function loads a txt file and returns its content as a string.
    Args:
        path_txt_file: path to txt file
    Returns:
        content: content of txt file
    """
    file = open(path_txt_file)
    content = file.read()
    file.close()

    return content


def add_leading_zeros(input_string: str, out_len: int) -> str:
    """This function adds leading zeros to the input string. The output string will have length == out_len
    Args:
        input_string: the input string
        out_len: length of output string with leading zeros
    Returns:
        out_string: the initial string but with leading zeros up to out_len characters
    Example:
        >>> s = "13"
        >>> s_out = add_leading_zeros(input_string=s, out_len=4)
        >>> s_out
        '0013'
    """
    out_string = input_string.zfill(out_len)

    return out_string


def remove_leading_zeros(input_string: str) -> str:
    """This function removes the leading zeros from input_string
    Args:
        input_string: the input string
    Returns:
        out_string: the input string without leading zeros
    """
    # use lstrip setting '0' as leading character, by default it would be space
    out_string = input_string.lstrip('0')

    return out_string


def str2bool(v: str) -> bool:
    """This function converts the input string into a boolean
    Args:
        v: input argument
    Returns:
        True: if the input argument is 'yes', 'true', 't', 'y', '1'
        False: if the input argument is 'no', 'false', 'f', 'n', '0'
    Raises:
        ValueError: if the input argument is none of the above
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ValueError('Boolean value expected.')
