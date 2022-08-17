# Using os module for checking if file already exists
import os

"""
This module stores a variable in your computer memory.
It creates parent folders and files to store the variable.
You can change and get the value of the variable
"""

"""
Sample code-
from stored_variable import *
Example = StoreInt("IntVar")
Example.push(198) or Example.push("198") 
print(Example.pull())
"""


class StoreString:
    """StoreInt"""
    """
    Functions - 
    pull
    push
    """
    def __init__(self, name):
        """
        This initializes the variable and creates a file in computer system to
        store the variable.
        It creates the file if not exists.
        It first makes the parent folder in which all files will be stored
        """
        try:
            os.mkdir(f'{os.getcwd()}/strings')
        except OSError as error:
            pass
        variables = os.listdir(f'{os.getcwd()}/strings')
        if f"{name}.txt" not in variables:
            file = open(f"{os.getcwd()}/strings/{name}.txt", 'x')
            file.close()
        self.string_value = ""
        self.var_name = name

    def push(self, value):
        name = self.var_name
        """
        It pushes a value to the given variable
        """
        self.string_value = value
        file = open(f"{os.getcwd()}/strings/{name}.txt", 'w')
        file.write(value)
        file.close()

    def pull(self):
        """
        It returns the value stored in the given variable
        """
        name = self.var_name
        string_value = open(f"{os.getcwd()}/strings/{name}.txt", 'r')
        string_data = string_value.read()
        return string_data

    def delete(self):
        """
        It deletes the variable to save the storage
        """
        os.remove(f"{os.getcwd()}/strings/{self.var_name}.txt")


class StoreInt:
    """StoreString"""
    """
    Functions - 
    pull
    push
    """
    def __init__(self, name):
        """
        This initializes the variable and creates a file in computer system to
        store the variable.
        It creates the file if not exists.
        It first makes the parent folder in which all files will be stored
        """

        try:
            os.mkdir(f'{os.getcwd()}/integers')
        except OSError as error:
            pass
        variables = os.listdir(f'{os.getcwd()}/integers')
        if f"{name}.txt" not in variables:
            file = open(f"{os.getcwd()}/integers/{name}.txt", 'x')
            file.close()
        self.integer_value = ""
        self.var_name = name

    def push(self, value):
        """
        It pushes a value to the given variable
        """
        name = self.var_name
        self.integer_value = value
        file = open(f"{os.getcwd()}/integers/{name}.txt", 'w')
        file.write(str(value))
        file.close()

    def pull(self):
        """
        It returns the value stored in the given variable
        """
        name = self.var_name
        integer_value = open(f"{os.getcwd()}/integers/{name}.txt", 'r')
        integer_data = integer_value.read()
        return int(integer_data)

    def delete(self):
        """
        It deletes the variable to save the storage
        """
        os.remove(f"{os.getcwd()}/strings/{self.var_name}.txt")


class StoreFloat:
    """StoreFloat"""
    """
    Functions - 
    pull
    push
    """
    def __init__(self, name):
        """
        This initializes the variable and creates a file in computer system to
        store the variable.
        It creates the file if not exists.
        It first makes the parent folder in which all files will be stored
        """
        try:
            os.mkdir(f'{os.getcwd()}/float')
        except OSError as error:
            pass
        variables = os.listdir(f'{os.getcwd()}/float')
        if f"{name}.txt" not in variables:
            file = open(f"{os.getcwd()}/float/{name}.txt", 'x')
            file.close()
        self.float_value = ""
        self.var_name = name

    def push(self, value):
        """
        It pushes a value to the given variable
        """
        name = self.var_name
        self.float_value = value
        file = open(f"{os.getcwd()}/float/{name}.txt", 'w')
        file.write(str(value))
        file.close()

    def pull(self):
        """
        It returns the value stored in the given variable
        """
        name = self.var_name
        float_value = open(f"{os.getcwd()}/float/{name}.txt", 'r')
        float_data = float_value.read()
        return float(float_data)

    def delete(self):
        """
        It deletes the variable to save the storage
        """
        os.remove(f"{os.getcwd()}/float/{self.var_name}.txt")