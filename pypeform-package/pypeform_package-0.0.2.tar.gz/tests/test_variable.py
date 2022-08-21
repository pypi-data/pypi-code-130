from pypeform import Variable

test_key = 'test_key'
test_type = 'test_type'


def check_variable_values(variable: Variable, key, type, value) -> bool:
    assert variable.key == key
    assert variable.type == test_type
    assert variable.value == value

    return True


def test_variable_stores_values():
    value = 'test_value'
    variable = Variable(key=test_key, _type=test_type, value=value)
    check_variable_values(variable=variable, key=test_key, type=test_type, value=value)


def test_variable_stores_int_value():
    value = 1
    variable = Variable(key=test_key, _type=test_type, value=value)
    check_variable_values(variable=variable, key=test_key, type=test_type, value=value)


def test_variable_stores_float_value():
    value = 3.14
    variable = Variable(key=test_key, _type=test_type, value=value)
    check_variable_values(variable=variable, key=test_key, type=test_type, value=value)


def test_variable_stores_str_value():
    value = 'test_string'
    variable = Variable(key=test_key, _type=test_type, value=value)
    check_variable_values(variable=variable, key=test_key, type=test_type, value=value)
