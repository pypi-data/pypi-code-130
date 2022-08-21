import re


precednce = {
    '==': 0,
    '!=': 0,
    '>':  0,
    '>=': 0,
    '<':  0,
    '<=': 0,
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '//': 2,
    '%': 2,
    '(': 0,
    ')': 0
}


# temp solution
def red(op, queue):
    num1 = queue.pop(-1) or 0
    num2 = queue.pop(-1) or 0

    if type(num2) is str and num1 == 0:
        num1 = ''

    if op == '+':
        num2 += num1
    elif op == '-':
        num2 -= num1
    elif op == '*':
        num2 *= num1
    elif op == '/':
        num2 /= num1
    elif op == '==':
        num2 = num2 == num1
    elif op == '!=':
        num2 = num2 != num1
    elif op == '>':
        num2 = num2 > num1
    elif op == '>=':
        num2 = num2 >= num1
    elif op == '<':
        num2 = num2 < num1
    elif op == '<=':
        num2 = num2 <= num1
    queue.append(num2)


# this should happen on decorator
def get_var(tag, var_name, default=None):
    name, *index = var_name.split('.')
    while True:
        # BUG: this causes the tag to look for state var all the
        # way up to root before even attempting to consider tag args
        if var := tag.get_state(name):
            # supports for chaining indexes??
            if index:
                return var[int(index[0])]
            return var
        if (tag := tag.parent) is None:
            return default


def shunting_yard(tag, string):
    op_stack = []
    out_queue = []
    ex = r"(?P<const>[0-9\.]+)|\"(?P<str>.*?)\"|(?P<var>[a-zA-Z][a-zA-Z0-9_\.]*)|(?P<op>[+\-*/%()=><!]{1,2})"
    for match in re.finditer(ex, string):
        const, string, var, op = match.groups()
        if const:
            out_queue.append(int(const))
        elif string:
            out_queue.append(string)
        elif var:
            v = get_var(tag, var)
            out_queue.append(v)
        elif op:
            if op == ')':
                while (_op := op_stack.pop(-1)) != '(':
                    red(_op, out_queue)
            else:
                if op_stack:
                    if op != '(' and precednce[op_stack[-1]] >= precednce[op]:
                        _op = op_stack.pop(-1)
                        red(_op, out_queue)
                op_stack.append(op)
    for _op in op_stack[::-1]:
        red(_op, out_queue)

    return out_queue[0]


if __name__ == '__main__':
    s = "hi == \"hi\""
    out = shunting_yard(s, lambda x: x)
    print(out)