import sys
import yaml

from inkplot.exceptions import MismatchedLayersetSourceException, VisibilityConflictException


def read_yaml(filepath):
    """
    reads yaml page def into a dict
    """
    try:
        with open(filepath) as s:
            data = yaml.safe_load(s)
            return data
    except yaml.YAMLError as e:
        print(f"error encountered reading file, {filepath}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"file {filepath} not found")
        sys.exit(1)


def layerset_def_to_pattern_visible_iterator(layerset_def):
    """
    iterator yielding pattern, visible tuples given a layerset definition
    as input
    """
    # figure out whether visible and hidden are booleans or lists and, if they're lists,
    # go ahead and yield out the pattern, visible tuples
    hidden_explicitly_defined = False
    hidden_is_boolean = False
    visible_explicitly_defined = False
    visible_is_boolean = False
    if layerset_def.get('hidden') is not None:
        hidden_explicitly_defined = True
        try:
            for layer_name in layerset_def.get('hidden'):
                yield layer_name, False
        except TypeError:
            hidden_is_boolean = True
    if layerset_def.get('visible') is not None:
        visible_explicitly_defined = True
        try:
            for layer_name in layerset_def.get('visible'):
                yield layer_name, True
        except TypeError:
            visible_is_boolean = True

    # if they're booleans, make sure they don't conflict
    if hidden_explicitly_defined and visible_explicitly_defined:
        if hidden_is_boolean and visible_is_boolean and layerset_def.get('hidden') == layerset_def.get('visible'):
            layersetdef_name = layerset_def.get('name', 'UNNAMED')
            raise VisibilityConflictException(
                f'layerset definition for {layersetdef_name} includes conflicting settings for hidden and visible')

    # if hidden is defined and a bool, iterate over the layers list,
    # updating visibility
    if hidden_explicitly_defined and hidden_is_boolean:
        for layer_name in layerset_def.get('layers', []):
            yield layer_name, not layerset_def.get('hidden')
        return
    # if visible is explicitly defined and is a bool, iterate over the layers list and hidden isn't
    # defined, then iterate over the layers list, updating visiblity
    if visible_explicitly_defined and visible_is_boolean and (
            not hidden_explicitly_defined or hidden_explicitly_defined and hidden_is_boolean):
        for layer_name in layerset_def['layers']:
            yield layer_name, layerset_def.get('visible')
        return

    # if either visible or hidden was defined, then we're done
    if hidden_explicitly_defined or visible_explicitly_defined:
        return

    # but if neither hidden or visible were defined, assume visible and iterate
    # over layers
    if layerset_def.get('layers'):
        for layer_name in layerset_def['layers']:
            yield layer_name, True


def pagedef_pattern_visible_iterator(page_def, shared_layersets_dict):
    """
    iterator yielding pattern, visible tuples given a page definition
    as input
    """
    # yield shared layerset layer visibility info
    if page_def.get('include-layersets'):
        for layerset_name in page_def.get('include-layersets', []):
            layerset_def = shared_layersets_dict.get(layerset_name)
            for pattern, is_visible in layerset_def_to_pattern_visible_iterator(layerset_def):
                yield pattern, is_visible

    # yield per-page layerset layer visibility info
    if page_def.get('layersets'):
        for layerset_def in page_def.get('layersets', []):
            for pattern, is_visible in layerset_def_to_pattern_visible_iterator(layerset_def):
                yield pattern, is_visible


def pagedef_expanded_pattern_visible_iterator(page_def, shared_layersets_dict):
    """
    an iterator that will expand the (pattern, visible) tuples yielded by
    pagedef_pattern_visible_iterator() when visible is True such that parent
    layers are made visible as needed to effect the visibility of the
    yielded layer def.

    Note that this expansion does not happen when hiding layers since hiding
    a layer does not require the hiding of parent layers to have an impact
    on the output.
    """
    # iterate over the visibility patterns, expanding as required
    for pattern, is_visible in pagedef_pattern_visible_iterator(page_def, shared_layersets_dict):

        # if hidden, just yield and continue
        if not is_visible:
            yield pattern, is_visible
            continue

        # expand visible patterns
        root = []
        for part in pattern.split('>>'):
            yield '>>'.join(root + [part]), is_visible
            root.append(part)


def page_zoom_rectangle_id(page_def, shared_zoom_rectangles_def):
    """
    return the id to the rectangle to be used for zoom rect assignment
    """
    # just return it if it's defined directly
    zoom_rect_id = page_def.get('zoom-rectangle')
    if zoom_rect_id:
        return zoom_rect_id

    # otherwise, if the name of the shared zoom rectangle is given,
    # resolve the name to the id and return it
    zoom_rect_name = page_def.get('include-zoom-rectangle')
    if zoom_rect_name:
        for zoom_rect_def in shared_zoom_rectangles_def:
            if zoom_rect_def.get('name') == zoom_rect_name:
                return zoom_rect_def.get('id')
