"""This package provides classes to organize grammars and machines

The created grammars can be :py:meth:`elevated <.to_correct_chomsky_hierarchy_level>`
to their respective Chomsky hierarchy level.
Elevated grammar classes have access to hierarchy appropriate methods.

Machines and grammars can be transformed into each other, but only on correct
Chomsky hierarchy.

The machine functionality is just enough to display the correlation with their
corresponding grammar, for more functionality I recommend the `Jove package <https://github.com/ganeshutah/Jove>`_,
for which the objects have compatibility methods.
"""