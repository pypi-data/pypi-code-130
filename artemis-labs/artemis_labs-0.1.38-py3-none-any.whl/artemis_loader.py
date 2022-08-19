from asyncio import constants
from lib2to3.pgen2 import token
import os 
from enum import Enum
from pprint import pprint
from textwrap import indent 
import re
import base64
import sys
import datetime
from .artemis_token import *
from .artemis_token_parser import *


class TokenChain():
   
    def __init__(self, line):
        old_line = line
        line = line.strip()
        self.is_token_chain = False
        self.tokens = []
        if len(line) == 0 or line[0] != '#':
            return
        self.indentation, self.tokens = TokenParser.parse_line(old_line)

    def get_indentation(self):
        return self.indentation

    def get_tokens_str(self):
        if not self.is_valid():
            return "[Invalid token chain]"

        out = '['
        for token in self.tokens[:-1]:
            out += str(token) + ', '
        if len(self.tokens) > 0:
            out += str(self.tokens[-1])
        out += ']'
        return out

    def __str__(self):
        out = 'Token' + '\n\tCommand: ' + self.get_command() + '\n'
        out += '\tComponent Type: ' + self.get_component_type() + '\n'
        out += "\tTokens: " + self.get_tokens_str() + "\n"
        out +=  '\tTags: ' + "\n"
        for tag in self.get_tags():
            out += "\t" + tag + "\n"
        out += '\tArgs' + "\n"
        for arg in self.get_args():
            out += "\t" + arg + "\n"
        return out


    def is_valid(self):

        # Verify tokens exist
        if len(self.tokens) == 0:
            return False

        # Verify command exists
        if self.tokens[0].token_type != TokenType.COMMAND:
            return False

        # We dont need to verify compnent type if we're just enabling or disabling
        single_command_tokens = ['@flag', '@doc', '@startdoc', '@enddoc', '@marker', '@linkedcode']
        if self.tokens[0].token_value in single_command_tokens:
            return True

        # Verify component type provided
        if len(self.tokens) <= 1:
            return False

        # Verify component type exists
        if self.tokens[1].token_type != TokenType.COMPONENT_TYPE:
            return False
        return True

    
    def get_tags(self):
        tags = []
        for token in self.tokens:
            if token.token_type == TokenType.TAG:
                tags.append(token.token_value)
        return tags

    def get_named_args(self):
        named_args = []
        for token in self.tokens:
            if token.token_type == TokenType.NAMED_ARGUMENT:
                named_args.append(token.token_value)
        return named_args

    def get_args(self):
        args = []
        for token in self.tokens:
            if token.token_type == TokenType.ARGUMENT:
                args.append(token.token_value)
        return args

    def get_command(self):
        if len(self.tokens) == 0: return None
        if self.tokens[0].token_type == TokenType.COMMAND:
            return self.tokens[0].token_value
        return None

    def get_component_type(self):
        if self.tokens[1].token_type == TokenType.COMPONENT_TYPE:
            return self.tokens[1].token_value

    def get_component_value(self):
        if self.tokens[2].token_type == TokenType.VALUE:
            return self.tokens[2].token_value
        return None

class TagMap():
    def __init__(self):
        self.tags = {}

    def enable_tag(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            self.tags[tag] = {}
        self.tags[tag][prop] = True

    def disable_tag(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            self.tags[tag] = {}
        self.tags[tag][prop] = False

    def is_tag_enabled(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            return True
        if prop not in self.tags[tag]:
            return True
        return self.tags[tag]

    def get_prop_value(self, tag_list, prop):
        val = None
        for tag in tag_list:
            tag = tag.strip()
            if tag in self.tags and prop in self.tags[tag]:
                val = self.tags[tag][prop]
        return val

class Line():
    def __init__(self, line):
        self.line = line
        strip_line = self.line.strip()

        # Iniitialize variables
        self.comment = False 
        self.lhs = ''
        self.rhs = ''

        # Check if line is a comment
        if len(strip_line) == 0:
            return
        self.comment = strip_line[0] == '#'

        # Parse sides of line
        if '=' not in strip_line:
            self.lhs = strip_line.replace(';', '')
            self.rhs = ''
        else: 
            try:
                self.lhs = line.split('=')[0].strip().replace(';', '')
                self.rhs = line.split('=')[1].strip()
            except Exception as e:
                print('Failed to parse line: ' + line)
                print('Exception: ' + str(e))
                raise e
              
    def is_comment(self):
        return self.comment

    def get_lhs(self):
        return self.lhs

    def get_rhs(self):
        return self.rhs

    def get_line(self):
        return self.line

class LineParser():
    def parse_line(line):
        return Line(line)

class LineTransformer():
    def transform_script(lines, init_offset=10):
        
        # Tag map
        tag_map = TagMap()

        # Marker map
        marker_map = {}

        # Skip next line n lines 
        skip_counter = 0

        # Main pass
        transformed_lines = []

        # Compute offset
        if len(lines) > 1 and lines[1] == 'from artemis_labs.artemis import artemis':
            init_offset = 8

        # Doc accumulator
        doc_accum = ''
        doc_accum_active = False
        doc_accum_offset = 0
        doc_accum_line_start = -1
        doc_accum_line_end = -1

        # Check if in block quotes
        in_block_quote = False

        # Load marker map
        for i, line in enumerate(lines):

            # Toggle block quotes
            if "\'\'\'" in line:
                in_block_quote = not in_block_quote

            # Tokenize Line
            token_chain = TokenChain(line)

            # Process commands
            if token_chain.is_valid() and not in_block_quote:
                if '@marker' == token_chain.get_command():
                    transformed_lines.append(line)
                    marker_map[token_chain.get_component_type()] = i
                    continue

        # Transform lines
        for i, line in enumerate(lines):

            # Insert initial card
            if 'app = artemis' in line:
                
                # Add line
                transformed_lines.append(line)
                
                # Add init card
                attr_file_name = __file__.replace("\\", "/").replace(" ", "%20")
                attr_sys_type = sys.platform
                attr_sys_version = sys.version
                attr_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                attr_output = f'### *System Information* \\n __**Run Date**__ \\n {attr_date} \\n__**File Path**__\\n {attr_file_name}\\n __**System Type**__ \\n {attr_sys_type} \\n __**Version**__ \\n {attr_sys_version}'
                transformed_lines.append(f"app.createOutput(0, 0, '', '{attr_output}', 'markdown', '')")
                continue


            # Skip lines
            if skip_counter > 0:
                skip_counter -= 1
                continue

            # Toggle block quotes
            if "\'\'\'" in line:
                in_block_quote = not in_block_quote

            # Tokenize Line
            token_chain = TokenChain(line)

            # Parse line
            curr_line = LineParser.parse_line(line)
            next_line = None
            if i < len(lines) - 1:
                next_line = LineParser.parse_line(lines[i + 1])

            # Cancel @startdoc if we hit a triple quote first
            if "'''" in line and doc_accum_active:    
                doc_accum_active = False
                doc_accum = ''
                doc_accum_offset = 0

            # Handle docaccum active
            if doc_accum_active and '@enddoc' not in line:

                # Add line regular if not linked code
                if '@linkedcode' not in line:
                    trim_count = 0
                    for c in range(0, min(doc_accum_offset, len(line))):
                        if line[c] == ' ':
                            trim_count += 1
                        else:
                            break
                    doc_accum += line[trim_count:] + '\n'
                else:
                    named_args = token_chain.get_named_args()                   
                    if len(named_args) == 2 and named_args[0][0] == 'start' and named_args[1][0] == 'end':
                        if named_args[0][1] in marker_map and named_args[1][1] in marker_map:
                            doc_accum += '```\n'
                            doc_accum += '# [linked code: lines ' + str(marker_map[named_args[0][1]] - init_offset + 1) + '-' + str(marker_map[named_args[1][1]] - init_offset + 1) + ']\n'
                            start_code_index = marker_map[named_args[0][1]]
                            end_code_index = marker_map[named_args[1][1]]
                            for code_index in range(start_code_index + 1, end_code_index):
                                doc_accum += lines[code_index] + "\n"
                            doc_accum += '```\n'

                # Store lines
                transformed_lines.append(line)
                continue

            # Process block doc commands
            if token_chain.is_valid():
                
                # Handle @startdoc
                if token_chain.get_command() == '@startdoc' and i > 0 and "'''" in lines[i - 1] and not doc_accum_active:
                    doc_accum_offset = line.find("@startdoc")
                    doc_accum_active = True
                    doc_accum = ''
                    doc_accum_line_start = i - init_offset + 1
                    transformed_lines.append(line)
                    continue
                
                # Handle @enddoc
                if token_chain.get_command() == '@enddoc'  and i < len(lines) - 1 and "'''" in lines[i + 1] and doc_accum_active:

                    # Skip if no block doc
                    if len(doc_accum) == 0:
                        transformed_lines.append(line)
                        continue 

                    # Remove trailing newline
                    if doc_accum[-1] == '\n':
                        doc_accum = doc_accum[:-1]

                    # Escape quotes and newlines
                    doc_accum = doc_accum.replace('\"', '\\\"').replace('\'', '\\\'').replace('\n', '\\n')

                    # Sanitize latex
                    latex_matches = re.findall('\$\$.*?\$\$', doc_accum)
                    for match in latex_matches:
                        doc_accum = doc_accum.replace(match, match.replace('\\', '\\\\'))

                    # Replace images -> ![](file.png)
                    file_matches = re.findall('!\[.*?\]\(.*?\)', doc_accum)
                    for match in file_matches:

                        # Match image
                        image_path = re.findall('\((.*?)\)', match)[0]
                        modified_image_path = image_path.replace('/', '\\')

                        # Replace image in markdown
                        image_data = load_image(modified_image_path)
                        if image_data != None:
                            updated_match = match.replace(image_path, image_data)
                            doc_accum = doc_accum.replace(match, updated_match)

                    # Sanitize spaces in links -> [](file.png)
                    link_matches = re.findall('(?<!!)(\[.*?\]\(.*?\))', doc_accum)
                    for match in link_matches:
                        link = re.findall('\((.*?)\)', match)[0]
                        new_match = match.replace(link, link.replace(' ', '%20'))
                        doc_accum = doc_accum.replace(match, new_match)

                    # Store lines
                    transformed_lines.append(line)
                    transformed_lines.append(lines[i + 1])
                    transformed_lines.append(f"{token_chain.get_indentation()}app.createOutput({doc_accum_line_start - 1}, {i - init_offset + 2}, '', '{doc_accum}', 'markdown', '')")
                    skip_counter = 1
                    doc_accum_active = False
                    doc_accum_line_start = -1
                    doc_accum = ''
                    in_block_quote = not in_block_quote
                    continue

            # Process non-block-doc commands   
            if token_chain.is_valid() and not in_block_quote:

                # Handle flags
                if token_chain.get_command() == '@flag':
                    valid_flags = ['enable', 'disable', 'nostop']
                    if len(token_chain.get_args()) > 0 and token_chain.get_args()[0] in valid_flags:
                        for tag in token_chain.get_tags():
                            if token_chain.get_args()[0] == 'enable':
                                tag_map.disable_tag(tag, 'disable')
                            else:
                                tag_map.enable_tag(tag, token_chain.get_args()[0])
                    transformed_lines.append(line)
                    continue

                # Handle no stop flags
                if token_chain.get_command() == '@nostop':
                    for tag in token_chain.get_tags():
                        tag_map.enable_tag(tag, 'nostop')
                    transformed_lines.append(line)
                    continue

                # Handle disabled status
                if 'disable' in token_chain.get_args():
                    transformed_lines.append(line)
                    continue
                elif tag_map.get_prop_value(token_chain.get_tags(), 'disable') == True:
                    transformed_lines.append(line)
                    continue

                if '@input' == token_chain.get_command() and next_line != None:

                    # ensure next line is not a comment
                    if next_line.is_comment():
                        transformed_lines.append(line)
                        continue
                            
                    # get name of variable
                    lhs = next_line.get_lhs()

                    # get cast type 
                    input_component_type = token_chain.get_component_type()
                    input_type = None
                    if input_component_type == 'number':
                        input_type = "float"

                    # skip if no cast type
                    if input_type == None:
                        transformed_lines.append(line)
                        continue

                    # append fodder
                    transformed_lines.append(line)
                    transformed_lines.append(f"{token_chain.get_indentation()}app.createInput({i - init_offset + 1}, {i - init_offset + 2}, 'Variable {lhs}', '')")
                    transformed_lines.append(f'{token_chain.get_indentation()}state = {input_type}(app.waitForInput())')
                    transformed_lines.append(f'{token_chain.get_indentation()}app.hideInput()')
                    transformed_lines.append(token_chain.get_indentation() + next_line.get_lhs() + ' = state')
                    skip_counter = 1
                    continue

                if '@output' == token_chain.get_command() and next_line != None:

                    # ensure next line is not a comment
                    if next_line.is_comment():
                        transformed_lines.append(line)
                        continue
                            
                    # get name of variable
                    lhs = next_line.get_lhs()

                    # get type of component
                    componentType = token_chain.get_component_type()

                    # append fodder
                    transformed_lines.append(line)
                    transformed_lines.append(next_line.get_line())
                    transformed_lines.append(f"{token_chain.get_indentation()}app.createOutput({i - init_offset + 1}, {i - init_offset + 2}, '{lhs}', {lhs}, '{componentType}', '', {token_chain.get_named_args()})")

                    # add stop
                    if tag_map.get_prop_value(token_chain.get_tags(), 'nostop') != True and 'nostop' not in token_chain.get_args():
                        transformed_lines.append(f"{token_chain.get_indentation()}app.waitForNext()")
                    skip_counter = 1
                    continue

                if '@doc' == token_chain.get_command():

                    # Store original line
                    transformed_lines.append(line)

                    # Get MD
                    markdown_text = token_chain.get_component_value().replace("'", "\\'")

                    # Sanitize latex
                    latex_matches = re.findall('\$\$.*?\$\$', markdown_text)
                    for match in latex_matches:
                        markdown_text = markdown_text.replace(match, match.replace('\\', '\\\\'))

                    # Replace images -> ![](file.png)
                    file_matches = re.findall('!\[.*?\]\(.*?\)', markdown_text)
                    for match in file_matches:

                        # Match image
                        image_path = re.findall('\((.*?)\)', match)[0]
                        modified_image_path = image_path.replace('/', '\\')

                        # Replace image in markdown
                        image_data = load_image(modified_image_path)
                        if image_data != None:
                            updated_match = match.replace(image_path, image_data)
                            markdown_text = markdown_text.replace(match, updated_match)

                    # Sanitize spaces in links -> [](file.png)
                    link_matches = re.findall('(?<!!)(\[.*?\]\(.*?\))', markdown_text)
                    for match in link_matches:
                        link = re.findall('\((.*?)\)', match)[0]
                        new_match = match.replace(link, link.replace(' ', '%20'))
                        markdown_text = markdown_text.replace(match, new_match)

                    # Store MD
                    transformed_lines.append(f"{token_chain.get_indentation()}app.createOutput({i - init_offset + 1}, {i - init_offset + 1}, '', '{markdown_text}', '{token_chain.get_component_type()}', '')")
                    continue

            # Add normal line
            transformed_lines.append(line)

        # Return transformed lines
        return transformed_lines


def process_script(runner_path, launch_command, code_path, dev=False, launch=True):
    
    # Read contents of decorated.py
    original_contents = open(code_path).read()
    original_contents_lines = original_contents.split('\n')

    if dev:
        original_contents_lines.insert(0, f'app = artemis("{runner_path}", "{launch_command}", "{code_path}", {launch}, {dev})')
        original_contents_lines.insert(0, 'atexit.register(waiter)')
        original_contents_lines.insert(0, '\t\tsleep(1)')
        original_contents_lines.insert(0, '\twhile True:')
        original_contents_lines.insert(0, 'def waiter():')
        original_contents_lines.insert(0, 'import atexit')
        original_contents_lines.insert(0, 'from artemis_labs.artemis import artemis')
        original_contents_lines.insert(0, 'sys.path.append(\'./artemis_labs/src/\')')
        original_contents_lines.insert(0, 'import sys')
        original_contents_lines.insert(0, 'from time import sleep')
    else:
        original_contents_lines.insert(0, f'app = artemis("{runner_path}", "{launch_command}", "{code_path}", {launch}, {dev})')
        original_contents_lines.insert(0, 'atexit.register(waiter)')
        original_contents_lines.insert(0, '\t\tsleep(1)')
        original_contents_lines.insert(0, '\twhile True:')
        original_contents_lines.insert(0, 'def waiter():')
        original_contents_lines.insert(0, 'import atexit')
        original_contents_lines.insert(0, 'from artemis_labs.artemis import artemis')
        original_contents_lines.insert(0, 'from time import sleep')


    # Transform lines
    transformed_contents_lines = LineTransformer.transform_script(original_contents_lines)

    # Dump back to file
    new_path = code_path.strip()[:-3] + '_artemis.py'
    out_path = new_path
    with open(out_path, 'w') as f:
        for line in transformed_contents_lines:
            f.write(line + '\n')
    return new_path

def load_image(path):
    try:
        with open(path, "rb") as image_file:
            b64Encoding = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
            return b64Encoding
    except Exception as e:
        print('[Artemis] Exception: Unable to load image')
        print('[Artemis] ' + str(e))