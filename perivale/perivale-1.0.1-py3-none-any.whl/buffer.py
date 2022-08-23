from copy import copy

from .position import Position


class Buffer:

    def __init__(self, text: str):
        self.text = text
        self.length = len(text)


        self.line_indices = []
        self.line_indentations = []
        self.line_count = 0
        
        index = 0
        while index < self.length:
            self.line_indices.append(index)
        
            # Evaluate indentation
            indentation = 0
            while True:
                if index == self.length:
                    break
            
                if text[index] == "\t":
                    indentation = ((indentation + 4) & ~0x03)
                elif text[index] == " ":
                    indentation += 1
                else:
                    break
            
                index += 1
            self.line_indentations.append(indentation)

            # Move to next newline
            while index < self.length and text[index] != '\n':
                index += 1
            index += 1
        
        self.line_count = len(self.line_indices)
        
        self.position = Position()
        if not text:
            self.position.line = -1
            self.position.column = -1
        elif text[0] == "\n":
            self.position.column = -1
    
    def increment(self, steps: int = 1):
        """ Increments the buffer's position
        
        Arguments
        ---------
        steps: int
            the number of steps to increment
        """

        for _ in range(steps):

            # Stop when the end of the buffer has been reached
            if self.position.index >= self.length:
                return

            # If the current character is a newline, increment the line number
            # and reset the column
            character = self.text[self.position.index]
            if character == "\n":
                self.position.line += 1
                self.position.column = 1

            # Handle tabs by rounding up to the next multiple of 4 (+1)
            elif character == "\t":
                column = int(((self.position.column + 3) / 4) * 4 + 1)
                self.position.column = column

            # Failing the above, and if the character wasn't format-related,
            # increment the column
            else:

                value = ord(character)
                lower, upper = [ord(letter) for letter in [" ", "~"]]
                if value >= lower and value <= upper:
                    self.position.column += 1

            self.position.index += 1

            if self.position.index == self.length:
                self.position.column = -1
            elif self.text[self.position.index] == "\n":
                self.position.column = -1
    
    def finished(self) -> bool:
        """ Checks if the buffer is finished
        
        Returns
        -------
        finished: bool
            if the buffer is finished
        """
        
        return self.position.index == self.length
    
    def copy_position(self) -> Position:
        """ Copies the buffer's position
        
        Note: this method _must_ be used rather than using the position member 
        directly
        
        Returns
        -------
        position: Position
            the copied position
        """

        return copy(self.position)
    
    def read(self, consume: bool = False) -> str:
        """ Reads the next character from the buffer
        
        Arguments
        ---------
        consume: bool
            if True, increments past the read character
            
        Returns
        -------
        character: str
            the character read, or "" if the buffer is finished
        """

        if self.finished():
            return ""
        
        result = self.text[self.position.index]
        if consume:
            self.increment()
        return result
    
    def match(self, text: str, consume: bool = False) -> bool:
        """ Checks whether a substring matches
        
        Arguments
        ---------
        text: str
            the substring to match
        consume: bool
            if true (and the substring matches), increments past it
        
        Returns
        -------
        match: bool
            true if the substring matched
        """

        if self.finished():
            return False
        
        # Check match feasible
        length = len(text)
        if self.position.index + length > self.length:
            return False
        
        # Extract substring
        end = self.position.index + length
        substring = self.text[self.position.index:end]

        # Check for match
        result = text == substring
        if result and consume:
            self.increment(steps=length)
        
        return result

    def parse_set(self, set: str, consume: bool = False) -> str:
        """ Parses a string comprised of the given set characters
        
        Arguments
        ---------
        set: str
            the set of permissible parse characters
        consume: bool
            if true, increments past the parsed string
        
        Returns
        -------
        result: str
            the parsed text
        """

        result = ""
        index = self.position.index
        while index < self.length:

            character = self.text[index]
            if character not in set:
                break

            result += character
            index += 1
        
        if result and consume:
            self.increment(len(result))
        return result
    
    def parse_range(self, range: tuple, consume: bool = False) -> str:
        """ Parses a string comprised of characters in a given range
        
        Arguments
        ---------
        range: tuple
            the (upper, lower) bounds of the range
        consume: bool
            if true, increments past the parsed string
        
        Returns
        -------
        result: str
            the parsed string
        """
        
        # Unpack bounds values
        if len(range) != 2:
            raise Exception("invalid range")
        lower, upper = [ord(letter) for letter in range]

        result = ""
        index = self.position.index
        while index < self.length:

            character = self.text[index]
            value = ord(character)
            if value < lower or value > upper:
                break

            result += character
            index += 1
        
        # Consume if requested
        if result and consume:
            self.increment(len(result))
        return result
    
    def parse_bounded_text(self, 
            bounds: tuple, 
            escape_bounds: bool = True,
            escape_codes: dict = {}, 
            permit_newlines: bool = False,
            consume: bool = False) -> str:
        
        """ Parses a bounded expression

        Arguments
        ---------
        bounds: tuple
            the start and end delimiters
        escape_bounds: bool
            if true, allows the end delimiter to be escaped with a backslash
        escape_codes: dict
            a set of mappings for escape codes
        permit_newlines: bool
            if true, allows newlines in the expression
        consume: bool
            if true, increments parsed the parsed expression
        
        Returns
        -------
        result: str
            the parsed expression, including its delimiters
        """

        # Unpack bounds
        if len(bounds) != 2:
            raise Exception("invalid bounds")
        start_token, end_token = bounds
        
        # Consume start token
        start_position = self.copy_position()
        if not self.match(start_token, consume=True):
            return ""
        
        # Add escape for end token
        if escape_bounds:
            escape_codes[f"\\{end_token}"] = end_token

        result = start_token
        while not self.finished():

            if (end_token != "\n" and 
                    self.match("\n") and 
                    not permit_newlines):
                break
            
            for symbol, code in escape_codes.items():
                if self.match(symbol, consume=True):
                    result += code
            
            if self.match(end_token):
                break
        
            result += self.read(consume=True)
        
        # Check end token found
        if not self.match(end_token, consume=True):
            result = ""
        
        # Consume if requested
        if not result or not consume:
            self.position = start_position
        
        if result:
            result += end_token
        return result
            
    def skip_line(self):
        """ Skips the current line """

        if self.position.line >= self.line_count:
            self.position.index = self.length
            self.position.column = -1
        else:
            index = self.line_indices[self.position.line]
            self.position.index = index
            self.position.line += 1
            self.position.column = 1

    def skip_space(self, include_newlines: bool = False):
        """ Skips whitespace characters
        
        Arguments
        ---------
        include_newlines: bool
            if true, skips newlines as well
        """
        while not self.finished():
            character = self.text[self.position.index]

            if ((character not in " \t\v\r") and 
                    not (character == "\n" and include_newlines)):
                break

            self.increment()

    def line_text(self, line_number: int = 0) -> str:
        """ Gets the text of a given line
        
        Arguments
        ---------
        line_number: int
            the number of the line of text to fetch; Note: not zero-indexed! By
            default, gets the current line's text
        
        Returns
        -------
        text: str
            the given line's text
        """

        # Set line number to current if zero or less
        if line_number <= 0:
            line_number = self.position.line

        # Assert line number in range
        if line_number < 1 or line_number > self.line_count:
            return ""

        # Evaluate start index
        start_index = 0
        if line_number > 1:
            start_index = self.line_indices[line_number - 1]

        # Evaluate end index
        end_index = self.length
        if line_number < self.line_count:
            end_index = self.line_indices[line_number] - 1
        elif self.length and self.text[self.length - 1] == "\n":
            end_index = self.length - 1

        return self.text[start_index:end_index]

    def line_indentation(self, line_number: int = 0) -> int:
        """ Gets the indentation of a given line
        
        Arguments
        ---------
        line_number: int
            the number of the line whose indentation to fetch; Note: not 
            zero-indexed! By default, gets the current line's indentation
        
        Returns
        -------
        indentation: int
            the given line's indentation
        """

        # Set line to current if not specified
        if line_number <= 0:
            line_number = self.position.line

        # Check line is in bounds
        if line_number < 1 or line_number > self.line_count:
            return 0

        return self.line_indentations[line_number - 1]