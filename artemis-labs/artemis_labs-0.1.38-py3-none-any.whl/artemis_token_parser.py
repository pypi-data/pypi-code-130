import token
from enum import Enum
from .artemis_token import *
import re

class TokenParser():

    def parse_line(line):

        # Store old line
        old_line = line

        # Clean line
        line = line.strip()

        # Remove trailing escape
        if line.endswith('\\'):
            line = line[:-1]

        # Remove lone escape
        line = line.replace('\\ ', '')

        # Verify comment
        if not line.startswith('#'):
            return ('', [])

        # Strip comment
        line = line[1:].strip()

        # Tokenize
        try:
            tokens = TokenParser.tokenify_line(line)
        except Exception as e:
            print("[Artemis] Error: Failed to tokenify line")
            print(e)
            return ('', [])

        # Remove empty tokens
        tokens = [token for token in tokens if token.strip() != '']

        # Check to make sure its non-empty
        if tokens == None or len(tokens) == 0:
            return ('', [])

        # Parse first token
        first_token = TokenParser.parse_token(tokens[0])

        # Exit if first token is not valid
        valid_tokens = ['@doc', '@input', '@flag', '@output', '@startdoc', '@enddoc', '@marker', '@linkedcode']
        if first_token.token_value not in valid_tokens:
            return ('', [])

        # Ensure inputs and outputs specifiy type    
        if first_token.token_value == '@doc':

            # Get markdown content
            doc_content = line[line.find('@doc') + len('@doc'):].strip()
            component_type = 'markdown'

            # Ensure proper command count
            if line.count('@') > 1:
                return ('', [])

            # Ensure value
            if doc_content.strip() == '':
                return ('', [])

            # Process doc token
            parsed_tokens = [TokenParser.parse_token('@doc'), Token(TokenType.COMPONENT_TYPE, component_type), Token(TokenType.VALUE, doc_content.strip())]

        elif tokens[0].strip() == '@marker':

            # Get marker name
            marker_name = line[line.find('@marker') + len('@marker'):].strip()
            if marker_name == '':
                return ('', [])

            # Tokenify marker name
            marker_name_tokens = TokenParser.tokenify_line(marker_name)
            if len(marker_name_tokens) == 0:
                return ('', [])

            # Process marker token
            parsed_tokens = [TokenParser.parse_token('@marker'), Token(TokenType.COMPONENT_TYPE, marker_name_tokens[0].strip())]
        else:

            # Tokenize line
            parsed_tokens = [TokenParser.parse_token(token) for token in tokens]

            # Mark any component types other than the first errors
            found_first_component_type = False
            for i, parsed_token in enumerate(parsed_tokens):
                if parsed_token.token_type == TokenType.COMPONENT_TYPE:
                    if not found_first_component_type:
                        found_first_component_type = True
                    else:
                        parsed_tokens[i].token_type = TokenType.ERROR

            # Prune error tokens
            parsed_tokens = [parsed_token for parsed_token in parsed_tokens if parsed_token.token_type != TokenType.ERROR]

            # Ensure first token is a command
            if first_token.token_type != TokenType.COMMAND:
                return ('', [])

            # Check token count
            two_token_types = ['@input', '@output']
            if first_token.token_value in two_token_types and len(parsed_tokens) < 2:
                return ('', [])

            # Ensure input and output have component type
            if first_token.token_value in two_token_types and parsed_tokens[1].token_type != TokenType.COMPONENT_TYPE:
                return ('', [])

            # Ensure proper command count
            command_count = 0
            for parsed_token in parsed_tokens:
                if parsed_token.token_type == TokenType.COMMAND:
                    command_count += 1
            if command_count == 0 or command_count > 1:
                return ('', [])

            # Validate token count
            two_token_types = ['@input', '@output']
            if first_token.token_value in two_token_types and len(parsed_tokens) < 2:
                return ('', [])

            # Trim garbage for startdoc and enddoc
            single_token_types = ['@startdoc', '@enddoc']
            if first_token.token_value in single_token_types:
                parsed_tokens = [first_token]

            # Validate flag
            if first_token.token_value == '@flag':

                # Validate inputs
                if len(parsed_tokens) < 2 or parsed_tokens[1].token_type != TokenType.ARGUMENT:
                    return ('', [])

                # Ensure only one arg
                arg_counter = 0
                for parsed_token in parsed_tokens:
                    if parsed_token.token_type == TokenType.ARGUMENT:
                        arg_counter += 1
                if arg_counter != 1:
                    return ('', [])

                # Remove erroneous tokens
                clean_parsed_tokens = []
                for parsed_token in parsed_tokens:
                    if parsed_token.token_type == TokenType.COMMAND or parsed_token.token_type == TokenType.ARGUMENT or parsed_token.token_type == TokenType.TAG:
                        clean_parsed_tokens.append(parsed_token)
                parsed_tokens = clean_parsed_tokens

            # Validate linked code
            if first_token.token_value == '@linkedcode':

                # Validate we have start and end
                found_start = False
                found_end = False
                clean_parsed_tokens = [first_token]
                for parsed_token in parsed_tokens[1:]:
                    if parsed_token.token_type == TokenType.NAMED_ARGUMENT and parsed_token.token_value[0] == 'start':
                        found_start = True
                        clean_parsed_tokens.append(parsed_token)
                    if parsed_token.token_type == TokenType.NAMED_ARGUMENT and parsed_token.token_value[0] == 'end':
                        found_end = True
                        clean_parsed_tokens.append(parsed_token)
                if not found_start or not found_end:
                    return ('', [])

                # Clean args
                parsed_tokens = clean_parsed_tokens

        # Validate

        # Return with indentation
        indentation = ''
        if not old_line.startswith('#'):
            indentation = old_line[:old_line.find('#')]
        return (indentation, parsed_tokens)

    def tokenify_line(line):
        tokens = []
        last_token = ""
        inside_quote = False
        for i, ch in enumerate(line):
            if ch == '\"':
                inside_quote = not inside_quote
            if not inside_quote and ch == ' ':
                tokens.append(last_token)
                last_token = ''
                continue
            last_token += ch
        if last_token != '':
            tokens.append(last_token)
        return tokens

    def parse_token(token):
        try:
            token = token.strip()
            if len(token) <= 1:
                return Token(TokenType.ERROR, token)
            if token.startswith("#"):
                if token[1] == ' ' or token.count('#') > 1 or "'" in token or "\"" in token or '\\' in token or '@' in token or '--' in token or '=' in token:
                    return Token(TokenType.ERROR, token)
                return Token(TokenType.TAG, token)
            elif token.startswith("@"):
                if token[1] == ' ' or token.count('@') > 1 or "'" in token or "\"" in token or '\\' in token or '=' in token:
                    return Token(TokenType.ERROR, token)
                return Token(TokenType.COMMAND, token)
            elif token.startswith("--") and len(token) > 2:
                if token[2] == ' ' or token.count('-') > 2 or "'" in token or "\"" in token or '\\' in token or '=' in token:
                    return Token(TokenType.ERROR, token)
                return Token(TokenType.ARGUMENT, token[2:])
            elif '=' in token and len(token.split('=')) == 2:
                if '\\' in token:
                    return Token(TokenType.ERROR, '')
                if '(' in token.split('=')[1] and ')' in token.split('=')[1]:
                    if token.split('=')[1].count('(') != 1 or token.split('=')[1].count(')') != 1:
                        return Token(TokenType.ERROR, '')
                    if ',' not in token.split('=')[1]:
                        return Token(TokenType.ERROR, '')
                    if not token.split('=')[1][0] == '(' or not token.split('=')[1][-1] == ')':
                        return Token(TokenType.ERROR, '')

                    arg_val = token.split('=')[1].replace('(','').replace(')','').replace("\"", "").split(',')

                    if arg_val[0].strip() == '' or arg_val[1].strip() == '':
                        return Token(TokenType.ERROR, '')

                    if len(arg_val) != 2:
                        return Token(TokenType.ERROR, '')
                    return Token(TokenType.NAMED_ARGUMENT, (token.split('=')[0], (arg_val[0], arg_val[1])))


                # Get arg name and value
                arg_name = token.split('=')[0].lstrip()
                arg_val = token.split('=')[1].rstrip()

                # Ensure no weird spacing
                if arg_name.endswith(' ') or arg_val.startswith(' '):
                    return Token(TokenType.ERROR, '')

                # Check for mismatched quotes
                if arg_val.count('\"') != 2 and arg_val.count('\"') != 0:
                    return Token(TokenType.ERROR, '')
                elif arg_val.count('\"') == 2 and not (arg_val.startswith('\"') and arg_val.endswith("\"")):
                    return Token(TokenType.ERROR, '')

                # Clean quotes
                arg_val = arg_val.replace('\"', '')


                if "'" in token:
                    return Token(TokenType.ERROR, '')

                if '@' in arg_name or '#' in arg_name or '--' in arg_name:
                    return Token(TokenType.ERROR, '')

                if '@' in arg_val or '#' in arg_val or '--' in arg_val:
                    return Token(TokenType.ERROR, '')

                if len(arg_name) == 0 or len(arg_val) == 0 or '"' in token.split('=')[0]:
                    return Token(TokenType.ERROR, '')
                return Token(TokenType.NAMED_ARGUMENT, (token.split('=')[0], arg_val))
            else:
                if ' ' in token or '\'' in token or '\"' in token or '=' in token or '#' in token or '@' in token or '\\' in token:
                    return Token(TokenType.ERROR, '')
                return Token(TokenType.COMPONENT_TYPE, token)
        except Exception as e:
            print("[Artemis] Failed to parse " + token)
            print("Error: ")
            print(e)
            return Token(TokenType.COMPONENT_TYPE, token)
