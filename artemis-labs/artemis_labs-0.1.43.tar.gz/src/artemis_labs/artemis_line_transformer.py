'''
This module contains the LineTransformer class
'''

#pylint: disable=line-too-long
#pylint: disable=anomalous-backslash-in-string
#pylint: disable=too-many-locals
#pylint: disable=too-many-nested-blocks
#pylint: disable=too-many-branches
#pylint: disable=too-many-statements
#pylint: disable=too-few-public-methods

import re
import datetime
import sys
from typing import List

from .artemis_tag_map import TagMap
from .artemis_token_chain import TokenChain
from .artemis_line import Line
from .artemis_helper import ArtemisHelper
from .config import get_fields

class LineTransformer():
    '''
    This class is used to transform an entire script into the Artemis version,
    which features the commands to communicate back and forth with the Artemis
    interface
    '''

    @staticmethod
    def transform_script(lines : List[str], init_offset=10) -> List[str]:
        '''
        This is the main function which transformes a list of lines, which comprise a script,
        into the Artemis version
        '''

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
            if 'app = Artemis' in line:

                # Add line
                transformed_lines.append(line)

                # Get fields
                print('Fields!')
                fields = get_fields()
                fields_str = '### *System Information* \\n'
                for field_name, field_value in fields.items():
                    fields_str += f'__**{field_name}**__: {field_value} \\n'
                print(fields_str)
                transformed_lines.append(f"app.create_output(0, 0, '', '{fields_str}', 'markdown', '')")
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
            next_line = None
            if i < len(lines) - 1:
                next_line = Line(lines[i + 1])

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
                    for char_index in range(0, min(doc_accum_offset, len(line))):
                        if line[char_index] == ' ':
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
                if token_chain.get_command() == '@enddoc' and i < len(lines) - 1 and "'''" in lines[i + 1] and doc_accum_active:

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
                    image_matches = re.findall('!\[.*?\]\(.*?\)', doc_accum)
                    for match in image_matches:

                        # Match image
                        image_path = re.findall('\((.*?)\)', match)[0]
                        modified_image_path = image_path.replace('/', '\\')

                        # Replace local image in markdown with b64 data
                        if 'http' not in image_path:
                            image_data = ArtemisHelper.load_image(modified_image_path)
                            if image_data is not None:
                                updated_match = match.replace(image_path, image_data)
                                doc_accum = doc_accum.replace(match, updated_match)

                    # Sanitize spaces in links -> [](file.png)
                    link_matches = re.findall('(?<!!)(\[.*?\]\(.*?\))', doc_accum)
                    for match in link_matches:
                        link = re.findall('\((.*?)\)', match)[0]
                        new_match = match.replace(link, link.replace(' ', '%20'))
                        doc_accum = doc_accum.replace(match, new_match)

                    # Scan for eval expressions
                    eval_lines = []
                    eval_expressions = re.findall("<<.*?>>", doc_accum)
                    for eval_expression_index, eval_expression in enumerate(eval_expressions):
                        clean_eval_expression = eval_expression[2:-2]
                        if clean_eval_expression.startswith('\\\''):
                            clean_eval_expression = '\'' + clean_eval_expression[2:]
                        if clean_eval_expression.endswith('\\\''):
                            clean_eval_expression = clean_eval_expression[0:-2] + '\''
                        if clean_eval_expression.startswith('\\"'):
                            clean_eval_expression = '"' + clean_eval_expression[2:]
                        if clean_eval_expression.endswith('\\"'):
                            clean_eval_expression = clean_eval_expression[0:-2] + '\"'
                        temp_var_name = f'artemis_temp_{i}_{eval_expression_index}'
                        eval_lines.append(f'{temp_var_name} = {clean_eval_expression}')
                        doc_accum = doc_accum.replace(eval_expression, '{' + temp_var_name + '}', 1)

                    # Clean off tags
                    doc_accum = doc_accum.replace('<', '&lt;').replace('>', '&gt;')

                    # Store MD
                    str_prefix = 'f' if len(eval_expressions) > 0 else ''

                    # Store lines
                    transformed_lines.append(line)
                    transformed_lines.append(lines[i + 1])
                    for eval_line in eval_lines:
                        transformed_lines.append(eval_line)
                    transformed_lines.append(f"{token_chain.get_indentation()}app.create_output({doc_accum_line_start - 1}, {i - init_offset + 2}, '', {str_prefix}'{doc_accum}', 'markdown', '')")
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
                if tag_map.get_prop_value(token_chain.get_tags(), 'disable') is True:
                    transformed_lines.append(line)
                    continue

                # check for data arg
                has_data_arg = False
                for named_arg in token_chain.get_named_args():
                    if 'data' in named_arg[0]:
                        has_data_arg = True


                if '@input' == token_chain.get_command() and next_line is not None:

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
                    if input_type is None:
                        transformed_lines.append(line)
                        continue

                    # append fodder
                    transformed_lines.append(line)
                    transformed_lines.append(f"{token_chain.get_indentation()}app.create_input({i - init_offset + 1}, {i - init_offset + 2}, 'Variable {lhs}', '')")
                    transformed_lines.append(f'{token_chain.get_indentation()}state = {input_type}(app.wait_for_input())')
                    transformed_lines.append(f'{token_chain.get_indentation()}app.hide_input()')
                    transformed_lines.append(token_chain.get_indentation() + next_line.get_lhs() + ' = state')
                    skip_counter = 1
                    continue

                if '@output' == token_chain.get_command() and (next_line is not None or has_data_arg):

                    # ensure next line is not a comment if there is no data arg
                    if not has_data_arg and (next_line is None or next_line.get_lhs().strip() == '' or next_line.is_comment()):
                        transformed_lines.append(line)
                        continue

                    # get type of component
                    component_type = token_chain.get_component_type()

                    # append original line
                    transformed_lines.append(line)

                    # append next line if there is one
                    if not has_data_arg:
                        transformed_lines.append(next_line.get_line())

                    # create named arg string
                    named_arg_str = '['
                    data = None
                    for named_arg_index, named_arg in enumerate(token_chain.get_named_args()):
                        if named_arg_index > 0:
                            named_arg_str += ', '
                        arg_name, arg_value = named_arg
                        if '<<' in arg_value and '>>' in arg_value:
                            if ' ' in arg_name:
                                continue
                            arg_value = arg_value.translate({ord(j) : None for j in '<>'})
                            temp_var_name = f'artemis_temp_{i}_{named_arg_index}'
                            transformed_lines.append(f'{token_chain.get_indentation()}{temp_var_name} = {arg_value}')
                            if arg_name == 'data':
                                data = temp_var_name
                            named_arg_str += f'(\'{arg_name}\',{temp_var_name})'
                        elif isinstance(arg_value, tuple):
                            named_arg_str += f'(\'{arg_name}\', (\'{arg_value[0]}\', \'{arg_value[1]}\'))'
                        else:
                            if arg_name == 'data':
                                data = arg_value
                            named_arg_str += f'(\'{arg_name}\', \'{arg_value}\')'
                    named_arg_str += ']'

                    # get name of variable
                    lhs = None
                    line_start = i - init_offset + 1
                    line_end = i - init_offset + 2
                    if has_data_arg:
                        lhs = data
                        line_end = line_start
                    else:
                        lhs = next_line.get_lhs()

                    # append output
                    if lhs is None:
                        transformed_lines.append(f"{token_chain.get_indentation()}app.create_output({line_start}, {line_end}, '', {None}, '{component_type}', '', {named_arg_str})")
                    else:
                        transformed_lines.append(f"{token_chain.get_indentation()}app.create_output({line_start}, {line_end}, '{lhs}', {lhs}, '{component_type}', '', {named_arg_str})")

                    # add stop
                    if tag_map.get_prop_value(token_chain.get_tags(), 'nostop') is not True and 'nostop' not in token_chain.get_args():
                        transformed_lines.append(f"{token_chain.get_indentation()}app.wait_for_next()")
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
                        image_data = ArtemisHelper.load_image(modified_image_path)
                        if image_data is not None:
                            updated_match = match.replace(image_path, image_data)
                            markdown_text = markdown_text.replace(match, updated_match)

                    # Sanitize spaces in links -> [](file.png)
                    link_matches = re.findall('(?<!!)(\[.*?\]\(.*?\))', markdown_text)
                    for match in link_matches:
                        link = re.findall('\((.*?)\)', match)[0]
                        new_match = match.replace(link, link.replace(' ', '%20'))
                        markdown_text = markdown_text.replace(match, new_match)

                    # Scan for eval expressions
                    eval_expressions = re.findall("<<.*?>>", markdown_text)
                    for eval_expression_index, eval_expression in enumerate(eval_expressions):
                        clean_eval_expression = eval_expression[2:-2]
                        if clean_eval_expression.startswith('\\\''):
                            clean_eval_expression = '\'' + clean_eval_expression[2:]
                        if clean_eval_expression.endswith('\\\''):
                            clean_eval_expression = clean_eval_expression[0:-2] + '\''
                        temp_var_name = f'artemis_temp_{i}_{eval_expression_index}'
                        transformed_lines.append(f'{temp_var_name} = {clean_eval_expression}')
                        markdown_text = markdown_text.replace(eval_expression, '{' + temp_var_name + '}', 1)

                    # Clean off tags
                    markdown_text = markdown_text.replace('<', '&lt;').replace('>', '&gt;')

                    # Store MD
                    str_prefix = 'f' if len(eval_expressions) > 0 else ''
                    transformed_lines.append(f"{token_chain.get_indentation()}app.create_output({i - init_offset + 1}, {i - init_offset + 1}, '', {str_prefix}'{markdown_text}', '{token_chain.get_component_type()}', '')")
                    continue

            # Add normal line
            transformed_lines.append(line)

        # Return transformed lines
        return transformed_lines
