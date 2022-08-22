# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashReactFlowing(Component):
    """A DashReactFlowing component.


Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- defaultEdgeOptions (dict; default { animated: True }):
    The default edge options.

- edges (list of dicts; optional):
    The edges which connect the flow chart.

- fitViewOptions (dict; optional):
    The fit view options.

- nodes (list of dicts; optional):
    The nodes which make up the flow chart.

    `nodes` is a list of dicts with keys:

    - data (dict; optional)

        `data` is a dict with keys:

        - label (string; optional)

    - id (string; optional)

    - position (dict; optional)

        `position` is a dict with keys:

        - x (number; optional)

        - y (number; optional)

- style (dict; optional):
    The reactFlowStyle."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_react_flowing'
    _type = 'DashReactFlowing'
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, nodes=Component.UNDEFINED, edges=Component.UNDEFINED, defaultEdgeOptions=Component.UNDEFINED, fitViewOptions=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'defaultEdgeOptions', 'edges', 'fitViewOptions', 'nodes', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'defaultEdgeOptions', 'edges', 'fitViewOptions', 'nodes', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashReactFlowing, self).__init__(**args)
