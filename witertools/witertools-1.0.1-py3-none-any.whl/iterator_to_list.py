

def iterator_to_list_function(iterator_function):
    """Composes list with interator_function.  The return function has the same arguments as iterator_fuction and returns a list."""
    #return list(iterator_function(*args,*kwargs))
    def as_list(*args,**kwargs):
        return list(iterator_function(*args,**kwargs))
    return as_list

def iterator_name_to_list_function(module,name):
    return iterator_to_list_function(getattr(module,name))