"""This package holds modules providing functionality needed elsewhere

The code in them is needed by other subpackages, but deemed non-informative
for purposes of education on formal languages

Following are the modules:

#. decorators
    Provides a decorator to deepcopy all arguments before passing them to the
    function
#. input_validator
    Provides functions to validate that the provided dictionary fulfills the
    requirements of a grammar as described in
    :ref:`the package description <grammar description>`
#. production_grouping
    Provides functions to organize grammar productions into dictionaries
#. sequence_functions
    Provides functions to determine the common prefix or suffix
    of any arbitrary collection of sequences
#. set_functions
    Provides functions to work with sets; such as :py:func:`powerset`
"""