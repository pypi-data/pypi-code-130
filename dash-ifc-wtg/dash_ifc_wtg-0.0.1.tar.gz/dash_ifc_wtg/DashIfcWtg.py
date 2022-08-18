# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashIfcWtg(Component):
    """A DashIfcWtg component.


Keyword arguments:

- id (string; optional):
    The ID used to identify the container for the IFC viewer
    component.

- ifc_file_contents (string; required):
    The contents of the ifc file."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_ifc_wtg'
    _type = 'DashIfcWtg'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, ifc_file_contents=Component.REQUIRED, **kwargs):
        self._prop_names = ['id', 'ifc_file_contents']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'ifc_file_contents']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['ifc_file_contents']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashIfcWtg, self).__init__(**args)
