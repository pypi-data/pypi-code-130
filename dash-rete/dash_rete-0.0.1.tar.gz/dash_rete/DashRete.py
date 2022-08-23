# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashRete(Component):
    """A DashRete component.


Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- label (string; optional):
    A label that will be printed when this component is rendered.

- value (string; optional):
    The value displayed in the input."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_rete'
    _type = 'DashRete'
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, label=Component.UNDEFINED, value=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'label', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'label', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashRete, self).__init__(**args)
