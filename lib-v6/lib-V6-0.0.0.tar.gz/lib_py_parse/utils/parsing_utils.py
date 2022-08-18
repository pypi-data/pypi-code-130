import lib_py_parse.utils.exceptions as exceptions
import lib_py_parse.utils.constants as constants

def indent_multiline_str(indent_str, multiline_str):
    return '\n'.join(
            [
                f'{indent_str}{x}'
                for x in multiline_str.splitlines()
            ]
        )


def get_fmt_str_expr_closure(target_substr, open_index, symbol_table):
    assert target_substr[open_index - 1] == '{'
    op_count = 1
    index = open_index
    while op_count > 0 and index < len(target_substr):
        if target_substr[index] == '}':
            op_count -= 1
        if target_substr[index] == '{':
            op_count += 1
        if target_substr[index] in ['\'', '\"']:
            index = get_quote_closure(target_substr, index)
            continue
        index += 1
    if op_count > 0:
        err_message = f'str literal cannot be parsed: {target_substr}'
        exceptions.raise_exception_ST(symbol_table, err_message)
    return index


def get_char_closure(s, index):
    t_mapper = constants.select_bracket_map()
    i = index
    open_token, close_token = s[index-1], t_mapper[s[index-1]]
    scope = 1
    while i < len(s) and scope > 0:
        if s[i] == open_token:

scope += 1

if s[i] == close_token:


scope -= 1
i += 1

if scope > 0:
    exceptions.raise_exception_msg(s, index, f'Unclosed: {s[index-1]}')
    return i


def get_unescaped_quote(s, index, quote):
    assert s[index] == quote
    i1 = index
    while True:
        i1 = s.find(quote, i1+1)
        if i1 == -1:
            exceptions.raise_exception_msg(s, index, f'unclosed quote')
        esc_count = 0
        while esc_count < i1 and s[i1 - esc_count - 1] == '\\':
            esc_count += 1
        if esc_count % 2 == 0:
            break
    return i1


def close_triple_quote(s, index, trq):
    i1 = index-1
    while True:
        i1 = s.find(trq, i1+1)
        if i1 == 0:
            break
        esc_count = 0
        while esc_count < i1 and s[i1 - esc_count - 1] == '\\':
            esc_count += 1
        if esc_count % 2 == 0:
            break
        if i1 == -1:
            raise Exception('unclosed triple quote')
    return i1


def get_quote_closure(s, index):
    trq1 = '\'\'\''
    trq2 = '\'\'\''
    if s[index:index+3] == trq1:
        return close_triple_quote(s, index+3, trq1) + 3
    if s[index:index+3] == trq2:
        return close_triple_quote(s, index+3, trq2) + 3
    return get_unescaped_quote(s, index, s[index]) + 1


def is_escaped_quote(s, index):
    result = 0
    while index > result and s[index - result - 1] == '\\':
        result += 1
    return result % 2 == 1


def get_cleared_char_closure(s, index):
    t_mapper = constants.select_bracket_map()
    i = index
    open_token, close_token = s[index-1], t_mapper[s[index-1]]
    scope = 1
    while i < len(s) and scope > 0:
        if s[i] == '\'' and not is_escaped_quote(s, i):
            i = get_quote_closure(s, i)
            continue
        if s[i] == '\"' and not is_escaped_quote(s, i):
            i = get_quote_closure(s, i)
            continue
        if s[i] == open_token:

scope += 1

if s[i] == close_token:


scope -= 1
i += 1

if scope > 0:
    exceptions.raise_exception_msg(s, index, f'Unclosed: {s[index-1]}')
    return i


def read_next_cleared_char(s, index, target_char):
    t_mapper = constants.select_bracket_map()
    while index < len(s):
        if s[index] == target_char:
            break
        if s[index] in t_mapper:
            index = get_cleared_char_closure(s, index+1)
        elif s[index] == '\'' and not is_escaped_quote(s, index):
            index = get_quote_closure(s, index)
        elif s[index] == '\"' and not is_escaped_quote(s, index):
            index = get_quote_closure(s, index)
        else :
            index += 1
    if index == len(s):
        return -1
    return index


def parse_current_scope(source_code, scope_start_index):
    current_scope = 0
    index = scope_start_index
    if not source_code[index].isspace():
        return current_scope, index
    scope_divide_factor_router = {
            '\t' : 1,
            ' ' : 4,
        }
    scope_divide_factor = scope_divide_factor_router[source_code[index]]
    while index < len(source_code) and source_code[index].isspace():
        index += 1
        current_scope += 1
    current_scope = current_scope // scope_divide_factor
    return current_scope, index


def read_init_token(source_code, index, scope):
    while index < len(source_code) and source_code[index] in ['\r', '\n']:
        index += 1
    if index == len(source_code):
        return 'EOF', index
    line_begin = index
    current_scope, index = parse_current_scope(source_code, index)
    if index == len(source_code):
        return 'EOF', index
    if source_code[index] == '#':
        return source_code[index], index+1
    if scope > current_scope:
        return 'EOS', line_begin
    i_start = index
    while index < len(source_code):
        if source_code[index].isspace() or source_code[index] == ':':
            break
        index += 1
    result = source_code[i_start:index]
    return result, index


def select_token_index(tok_stream, target_token):
    index = -1
    for i in range(0, len(tok_stream)):
        if tok_stream[i] == target_token:
            index = i
            break
    return index


def get_token_stream_closure(tok_stream, i_start):
    t_mapper = constants.select_bracket_map()
    index = -1
    bound = 0
    open_token = tok_stream[index]
    close_token = t_mapper[tok_stream[index]]
    for i in range(i_start, len(tok_stream)):
        if tok_stream[i] == close_token:
            bound -= 1
        if tok_stream[i] == open_token:
            bound += 1
        if bound == 0:
            index = i
            break
    return index


def get_expr_aware_closure(tok_stream, index, symbol_table):
    mapper = {
            't[' : ']',
            '[' : ']',
            '(' : ')',
            '{' : '}',
            's{' : '}',
        }
    assert tok_stream[index] in mapper
    target_token = mapper[tok_stream[index]]
    i1 = index+1
    while i1 < len(tok_stream):
        if tok_stream[i1] == target_token:
            i1 += 1
            break
        if tok_stream[i1] in mapper:
            i1 = get_expr_aware_closure(tok_stream, i1, symbol_table)
            continue
        i1 += 1
    if tok_stream[i1-1] != target_token:
        err_message = f'could not resolve expr_aware_closure: {tok_stream} {index}'
        exceptions.raise_exception_ST(symbol_table, err_message)
    return i1


def find_all_expr_aware(tok_stream, index, symbol_table, target_token):
    mapper = {
            't[' : ']',
            '[' : ']',
            '(' : ')',
            '{' : '}',
            's{' : '}',
        }
    result = []
    i1 = index
    while i1 < len(tok_stream):
        if tok_stream[i1] == target_token:
            result.append(i1)
        if tok_stream[i1] in mapper:
            i1 = get_expr_aware_closure(tok_stream, i1, symbol_table)
            continue
        i1 += 1
    return result


def split_expr_aware(tok_stream, symbol_table, target_token):
    indices = find_all_expr_aware(tok_stream, 0, symbol_table, target_token)
    last_index = -1
    result = []
    substream = []
    for i in range(0, len(indices)):
        substream = tok_stream[last_index+1:indices[i]]
        last_index = indices[i]
        result.append(substream)
    substream = tok_stream[last_index+1:]
    result.append(substream)
    return result


def split_arg_typle(s, index):
    i = index
    i0 = index
    result = []
    while i < len(s):
        if s[i] == '[':
            i = get_char_closure(s, i+1) + 1
            continue
        if s[i] == ',':
            result.append(s[i0:i])
            i0 = i
        i += 1
    if i0 < len(s):
        result.append(s[i0:])
    return result


def read_delimited_types(type_str):
    result = []
    index = 0
    i1 = 0
    while index < len(type_str):
        if type_str[index] == ',':
            result.append(type_str[i1:index])
            ctoken = ''
            index += 1
            while index < len(type_str) and type_str[index].isspace():
                index += 1
            i1 = index
            continue
        if type_str[index] == '[':
            index = get_char_closure(type_str, index+1)
            continue
        index += 1
    if index - i1 > 0:
        result.append(type_str[i1:index])
    return result


def parse_fxn_type(function_type, symbol_table):
    ws_removed_typon_fxn_type = function_type.replace(' ', '')
    interior_fxn_type = ws_removed_typon_fxn_type[4:-1]
    if len(interior_fxn_type) == 0:
        error_msgs = [
                    'invalid type declaration',
                    f'empty fxn not allowed: {ws_removed_typon_fxn_type}',
                ]
        exceptions.raise_exception_ST(symbol_table, error_msgs)
    arg_closure_index = get_char_closure(interior_fxn_type, 1)
    typon_fxn_arg_str = interior_fxn_type[1:arg_closure_index-1]
    arg_types_typon = read_delimited_types(typon_fxn_arg_str)
    return_type_typon = interior_fxn_type[arg_closure_index+1:]
    return arg_types_typon, return_type_typon
