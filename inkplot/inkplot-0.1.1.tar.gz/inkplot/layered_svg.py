import os
import tempfile
import xml.etree.ElementTree as ET

from inkplot.exceptions import ZoomRectangleNotFound

SVGPRE = '{http://www.w3.org/2000/svg}'
INKSCAPEPRE = '{http://www.inkscape.org/namespaces/inkscape}'


class LayeredSVG(object):
    """
    A class that allows for simple:
      * layer visibility adjustment
      * viewbox definition
      * writing current state of the svg to svg
      * writing the current state of the svg to a pdf
    """
    class getElementById():
        """a getElementById implementation for python"""
        def __init__(self, tree):
            self.di = {}

            def v(node):
                i = node.attrib.get("id")
                if i is not None:
                    self.di[i] = node

                for child in node:
                    v(child)

            v(tree.getroot())

        def __call__(self, k):
            try:
                return self.di[k]
            except KeyError:
                raise ZoomRectangleNotFound(f'element id: {k} not found')

    def __init__(self, filepath):
        self.filepath = filepath

        # parse the svg and set a pointer to the root element
        self._tree = ET.parse(filepath)
        self._dom = self._tree.getroot()

    def _is_layer(self, element):
        if element.tag != f'{SVGPRE}g':
            return False
        if (f'{INKSCAPEPRE}groupmode' not in element.attrib or
                element.attrib[f'{INKSCAPEPRE}groupmode'] != 'layer'):
            return False
        return True

    def _layer_path_string(self, labels):
        return '>>'.join(labels)

    def _style_string_to_dict(self, s):
        r = {}
        if not s:
            return r
        for p in s.split(';'):
            if not p:
                continue
            k, v = p.split(':')
            r[k] = v
        return r

    def _style_dict_to_string(self, d):
        pairs = [f'{k}:{d[k]}' for k in d.keys()]
        return ';'.join(pairs)

    # def OLD_layer_data_iterator(self, layer_elem=None, stack=[]):
    #
    #     # if unspecified, start with root node
    #     elem = layer_elem or self.svg_root_element()
    #
    #     # iterate over all children with group tags and, if they're inkscape
    #     # layers, yield a tuple of name, layer element.
    #     #
    #     # Recurse over children.
    #     layer_elements = elem.findall(f'./{SVGPRE}g')
    #     for layer_element in layer_elements:
    #         if not self._is_layer(layer_element):
    #             continue
    #         labels = ([layer_element.attrib.get(f'{INKSCAPEPRE}label')] if not stack
    #                   else [e.attrib.get(f'{INKSCAPEPRE}label') for e in [*stack, layer_element]])
    #         yield self._layer_path_string(labels), layer_element
    #         for layer_name, element in self._layer_data_iterator(layer_elem=layer_element, stack=[*stack, layer_element]):
    #             yield layer_name, element

    def _layer_data_iterator(self, layer_elem=None, stack=[]):

        # determine which node will be searching from
        is_toplevel = True
        elem = None
        if not layer_elem:
            elem = self.svg_root_element()
        else:
            elem = layer_elem
            is_toplevel = False

        path_labels = []
        if not is_toplevel:
            layer_label = elem.attrib.get(f'{INKSCAPEPRE}label')
            path_labels = [layer_label] if len(stack) == 0 else [*stack, layer_label]
            yield self._layer_path_string(path_labels), elem

        # recurse
        layer_elements = elem.findall(f'./{SVGPRE}g')
        for layer_element in layer_elements:
            if not layer_element:
                continue
            if not self._is_layer(layer_element):
                continue
            for layer_name, element in self._layer_data_iterator(layer_elem=layer_element,
                                                                 stack=path_labels):
                yield layer_name, element


    def _match_layer_name_pattern(self, pattern, name):
        if pattern == name:
            return True
        pattern_parts = pattern.split('>>')
        name_parts = name.split('>>')
        for n, part in enumerate(name_parts):
            corr_pattern_part = pattern_parts[n] if n < len(pattern_parts) else None
            if not corr_pattern_part:
                return False
            if corr_pattern_part == '**':
                return True
            if part != corr_pattern_part:
                return False
        return False

    def _run_command(self, cmd):
        print(f'executing shell command: {cmd}')
        os.system(cmd)

    def layer_names(self):
        """
        iterator that generates layer names in the format that inkplot uses in the pages yml
        """
        for layer_name, layer_elem in self._layer_data_iterator():
            yield layer_name

    def get_layers_by_name(self, pattern):
        """
        generator that yields layer elements with names that match the pattern
        """
        for layer_name, layer_elem in self._layer_data_iterator():
            if self._match_layer_name_pattern(pattern, layer_name):
                yield layer_elem

    def svg_root_element(self):
        """
        return the top-level element of the DOM for the svg
        """
        return self._dom

    def is_visible(self, layer_name):
        """
        return True if the layer associated with the layer name is visible, False otherwise
        """
        elems = self.get_layers_by_name(layer_name)
        for elem in elems:
            stylestr = elem.attrib.get(f'style')
            style_dict = self._style_string_to_dict(stylestr)
            if not style_dict or style_dict.get('display') == 'inline':
                return True
        return False

    def set_layer_visibility(self, pattern='**', visible=False):
        """
        set layer visibility with select path as follows:

          **: matches all layers
          some>>deep>>layer: operates on layers 'some', 'deep', and 'layer'
          some>>**: operates on all children layers of 'some'
        """
        # print(f'setting visibility - pattern: {pattern}, visible: {visible}')
        for layer_elem in self.get_layers_by_name(pattern=pattern):
            stylestr = layer_elem.attrib.get(f'style')
            style_dict = self._style_string_to_dict(stylestr)
            style_dict['display'] = 'inline' if visible else 'none'
            label = layer_elem.attrib.get(f'{INKSCAPEPRE}label')
            # print(f'setting visibility on elem with label: {label}, visible: {visible}')
            layer_elem.set('style', self._style_dict_to_string(style_dict))

    def set_viewbox_to_rect(self, rect_id):
        """set view window to rect whose id is rect_id"""
        dom_root = self.svg_root_element()
        try:
            finder = self.getElementById(self._tree)
            rect_element = finder(rect_id)
            dom_root.set('viewBox',
                         '{x0} {y0} {w} {h}'.format(x0=float(rect_element.attrib.get('x')),
                                                    y0=float(rect_element.attrib.get('y')),
                                                    w=float(rect_element.attrib.get('width')),
                                                    h=float(rect_element.attrib.get('height'))))
        except ZoomRectangleNotFound:
            print(f'zoom rectangle with id: {rect_id} not found')

    def viewbox(self):
        """
        returns the current viewbox as a tuple of x, y, w, h
        """
        dom_root = self.svg_root_element()
        current_viewbox = dom_root.attrib['viewBox']
        x, y, w, h = [float(x) for x in current_viewbox.split(' ')]
        return x, y, w, h

    def write_svg(self, filepath):
        """
        write the current state of the DOM to an svg file
        """
        self._tree.write(filepath)

    def write_pdf(self, filepath):
        """
        export to a pdf
        """
        with tempfile.NamedTemporaryFile(suffix='.svg') as fp:
            self.write_svg(fp.name)
            os.system(f'cp {fp.name} /tmp/page.svg')
            self._run_command(f'inkscape --export-type=pdf --export-filename={filepath} {fp.name}')
