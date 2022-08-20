import string
import random

# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate API Requests                                           #
# ---------------------------------------------------------------------------------------------------------------------#

# --------------------------------------------- Random String Functions -----------------------------------------------#


def generate_unique_id(chars_number):
    """Generate N chars random string with Lowercase and Uppercase."""
    unique_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(chars_number)])
    return unique_id


def generate_unique_lowercase_id(chars_number):
    """Generate N chars random string with Lowercase."""
    unique_id = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(chars_number)])
    return unique_id


def generate_unique_uppercase_id(chars_number):
    """Generate N chars random string with Uppercase."""
    unique_id = ''.join([random.choice(string.ascii_uppercase + string.digits) for n in range(chars_number)])
    return unique_id


def generate_unique_email(username, id, domain_list):
    """Generate random email, combine generate_unique_id,  generate_unique_lowercase_id or
    generate_unique_uppercase_id and a list of domains. """
    email = username + '.' + id + random.choice(domain_list)
    return email


# ---------------------------------------------  String Manipulation Functions ----------------------------------------#


def split_string_between(string_value, slice_a, slice_b):
    """Find and validate before-part and return middle part."""
    pos_a = string_value.find(slice_a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = string_value.rfind(slice_b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(slice_a)
    if adjusted_pos_a >= pos_b: return ""
    return string_value[adjusted_pos_a:pos_b]


def split_string_before(string_value, slice_a):
    """Find first part and return slice before it."""
    pos_a = string_value.find(slice_a)
    if pos_a == -1: return ""
    return string_value[0:pos_a]


def split_string_after(string_value, slice_a):
    """Find and validate first part and returns chars after the found string."""
    pos_a = string_value.rfind(slice_a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(slice_a)
    if adjusted_pos_a >= len(string_value): return ""
    return string_value[adjusted_pos_a:]


def remove_chars_from_string(string_value, char_list):
    """Remove all characters in list from string."""
    new_string = string_value
    for char in char_list:
        # Remove the char in list from the string value.
        new_string = new_string.replace(char, "")
    return new_string


def replace_string_with(string_value, old_string, new_string):
    # Replace the string for another value.
    result_string = string_value.replace(old_string, new_string)
    return result_string


def empty_string_to_none_string(string_value):
    # Replace the string "" or '' for None.
    if string_value == '' or "":
        return None
    else:
        return string_value


def generate_random_number(number_of_digits):
    begin = int('1' + '0' * (number_of_digits - 1))
    end = int('9' * number_of_digits)
    return str(random.randrange(begin, end))
