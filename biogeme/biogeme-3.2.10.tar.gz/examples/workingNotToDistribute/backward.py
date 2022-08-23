from collections import defaultdict

class Variable:
    def __init__(self, value, local_gradients=()):
        self.value = value
        self.local_gradients = local_gradients
    
def add(a, b):
    "Create the variable that results from adding two variables."
    value = a.value + b.value    
    local_gradients = (
        (a, 1),  # the local derivative with respect to a is 1
        (b, 1)   # the local derivative with respect to b is 1
    )
    return Variable(value, local_gradients)

def mul(a, b):
    "Create the variable that results from multiplying two variables."
    value = a.value * b.value
    local_gradients = (
        (a, b.value), # the local derivative with respect to a is b.value
        (b, a.value)  # the local derivative with respect to b is a.value
    )
    return Variable(value, local_gradients)

def get_gradients(variable):
    """ Compute the first derivatives of `variable` 
    with respect to child variables.
    """
    gradients = defaultdict(lambda: 0)
    
    def compute_gradients(variable, path_value):
        for child_variable, local_gradient in variable.local_gradients:
            # "Multiply the edges of a path":
            value_of_path_to_child = path_value * local_gradient
            # "Add together the different paths":
            gradients[child_variable] += value_of_path_to_child
            # recurse through graph:
            compute_gradients(child_variable, value_of_path_to_child)
    
    compute_gradients(variable, path_value=1)
    # (path_value=1 is from `variable` differentiated w.r.t. itself)
    return gradients

a = Variable(4)
b = Variable(3)
c = add(a, b)
d = mul(a, c)

gradients = get_gradients(d)

print(gradients)
