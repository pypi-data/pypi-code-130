from copy import deepcopy
from zml.semantic import *
from zml.context import RenderingContext
from zml.exceptions import IndentationException, ParseException
from zml.model import Field, Model, Function
from zml.resource import Resource
import zml


num_spaces_per_indent = 2


def eval_combined_accessor(res, node):
    value = node
    __import__('pdb').set_trace()
    for item in res:
        if item.has('data_node_accessor'):
            if isinstance(value, dict):
                value = value[item.data_node_accessor.data_node_descriptor.value]
            elif isinstance(value, Node):
                value = value.get_var(item.data_node_accessor.data_node_descriptor.value)
            else:
                raise ParseException('Cannot access items of type {}.'.format(type(value)))
        elif item.has('property_accessor'):
            if not isinstance(value, Node):
                raise ParseException('Failed to access property "{}". Properties are only accessible from node objects.'.format(item.property_accessor.value))
            value = value.get_property(item.property_accessor.value)
        else:
            raise Exception('finish!')
    return value


def get_property(obj, property_descriptor):
    # check if property in local_context, othterwise use main object
    try:
        value = obj[property_descriptor]
    except:
        # dont use getattr but explicit properties to prevent security issues
        # value = getattr(obj, property_descriptor)
        value = obj.get_property(property_descriptor)
    return value


def get_meta_data(obj, property_descriptor):
    if property_descriptor == 'descriptor':
        value = obj.descriptor
    elif property_descriptor == 'label':
        value = obj.label
    elif property_descriptor == 'type':
        value = obj.type
    return value


def get_combined_properties(value, properties):
    for property_item in properties:
        # currently we only handle dict properties. future implementations will handle
        # list item accessors with dot-number syntax (.0 for first element, .1 for second etc.)
        property_descriptor = property_item.value
        if property_item._marker == 'property':
            value = get_property(value, property_descriptor)
        elif property_item._marker == 'meta_data':
            value = get_meta_data(value, property_descriptor)
    return value


def eval_model(model_descriptor, node):
    return node.document.models[model_descriptor]


def eval_translation(res, node):
    translation_descriptor = res.translation_descriptor.value
    if res.has('properties'):
        value = node.document.get_translation(translation_descriptor, node.document.language)
        for property_item in res.properties.list:
            property_descriptor = property_item.value
            value = value[property_descriptor]
    else:
        value = node.document.get_translation(translation_descriptor, node.document.language)
    return value


def render_translation(res, node):
    return str(eval_translation(res, node))


class NodeRenderingContext(RenderingContext):
    pass


class Path(object):

    def __init__(self, document):
        self.document = document

    def execute(self, context, *args, **kwargs):
        if 'action' in context['context']:
            action = context['context']['action']
        else:
            return ''
        if 'router' in context['context']:
            router = self.document.router[context['context']['router']]
        else:
            router = self.document.default_router
        if router and action in router:
            route = router[action]
            url = ''
            for item in route:
                if item.has('path_segment'):
                    url += '/' + item.path_segment.value

                elif item.has('path_variable'):
                    path_variable = item.path_variable.variable_descriptor.value
                    if path_variable in context['context']:
                        url += '/' + context['context'][path_variable]
            return url


framework_components = {
    'path': Path,
    'sin': math.sin,
    'pi': math.pi
}


class TreeNode:

    def __init__(self, line='', line_number=1, is_root=False, is_ancestor=False, ancestor=None, base_indent=0):
        self.line = line
        self.base_indent = base_indent
        self.children = []
        self.body = None
        self.value = None
        self.link = None
        self.is_root = is_root
        self.is_ancestor = is_ancestor
        if ancestor is None:
            # explicitly state logic here to be clear that in both cases ancestor is set to self
            if self.is_ancestor:
                self.ancestor = self
            else:
                self.ancestor = self
        else:
            self.ancestor = ancestor
        indentation = len(line) - len(line.lstrip(' '))
        if indentation % num_spaces_per_indent != 0:
            raise IndentationException('Wrong indentation in line-#.: {} line: "{}"'.format(line_number, line))
        self.level = int(indentation / num_spaces_per_indent)
        self.render_level = 0
        self.base_render_level = 0

    def __repr__(self):
        # return '{}\n{}'.format(self.line, json.dumps(self.local_context, indent=2))
        return "{}({})\n".format(self.__class__.__name__, self.line)

    def add_children(self, nodes):
        if nodes:
            childlevel = nodes[0].level
            while nodes:
                node = nodes.pop(0)
                node.ancestor = self
                if node.level == childlevel:
                    if self.is_ancestor:
                        node.ancestor = self
                        node.local_context = {}
                    # add node as a child
                    self.children.append(node)
                elif node.level > childlevel:
                    # add nodes as grandchildren of the last child
                    # if self.children[-1].is_ancestor:
                    #     node.ancestor = self.children[-1]
                    #     node.local_context = self.children[-1].local_context
                    nodes.insert(0, node)
                    last_non_empty_child = self.get_last_non_empty_child()
                    if last_non_empty_child:
                        last_non_empty_child.add_children(nodes)
                    else:
                        raise Exception('Last empty child was not found')
                        # self.children[-1].add_children(nodes)
                elif node.level <= self.level:
                    # this node is a sibling, no more children
                    nodes.insert(0, node)
                    return

    def is_data(self):
        if self.is_root:
            return False
        else:
            return self.parent.is_data()

    def is_function(self):
        if self.is_root:
            return False
        else:
            return self.parent.is_function()

    def get_last_non_empty_child(self):
        children_reversed = reversed(self.children)
        for child in children_reversed:
            # child must be nonempty
            if child.line != '':
                return child
        # TODO: fallback?


class Egg(TreeNode):

    expression = EGG

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        res = parse(self.expression, self.line)
        if res.has('node_key'):
            self.body = res.node_key.value
        if res.has('node_value'):
            self.link = res.node_value.value

    def get_last_non_empty_child(self):
        children_reversed = reversed(self.children)
        for child in children_reversed:
            # child must be nonempty
            if child.line != '':
                return child
        # TODO: fallback?


class Node(TreeNode, NodeRenderingContext):

    expression = ELEMENT

    def __init__(self, line, document=None, expression=None, global_context=None, local_context=None,
                 meta_data={}, descriptor=None, base_indent=0, renderer=None, tokens=None, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        if local_context is None:
            local_context = {}
        if global_context is None:
            global_context = {}
        self.line = line
        self.data = dict()
        self.descriptor = descriptor
        self.local_context = local_context
        self.meta_data = meta_data
        self.global_context = global_context
        self.renderer = renderer
        self.minimise = False
        self.leading = ''
        self.trailing = ''
        self.is_component = False
        self.is_code = False
        self.has_list_items = False
        self.line = line.strip()
        self.document = document
        self.out = ()
        if self.is_root:
            self.level = -1

    def get_path(self):
        node = self
        path = ''
        while node != self.document.root:
            segment = ''
            if node.glyph:
                segment += node.glyph
            segment += node.descriptor
            path = segment + path
            if node.parent:
                node = node.parent
            else:
                return path
        return path

    def eval_segment(self, segment):
        if 'data_node_descriptor' in segment[1]:
            return self.data[segment[1]['data_node_descriptor']]

    def get_address(self):
        if self.document.cid:
            return self.document.cid + self.get_path()
        else:
            return self.get_path()

    def process(self, lazy=False):
        if not lazy and self.is_root is False:
            res = parse(self.expression, self.line)
            self.tokens = res
            self.render_parts(res)

    def render(self):
        # element = self.expression.parseString(self.line)
        if self.is_root:
            return ''
        element = parse(self.expression, self.line)
        if element.has('inline_content'):
            value = self.render_inline_content(element.inline_content)
            self.set_var('_value', value)
        else:
            self.set_var('_value', None)
        self.render_parts(element)

    def get_combined_properties(self, properties):
        return get_combined_properties(self, properties)

    def get_meta_data(self, property_descriptor):
        return get_meta_data(self, property_descriptor)

    # def eval_context_item(self, res):
    #     # raise Exception('finish this function')
    #     return eval_context_item(res, self)

    def eval_combined_accessor(self, res):
        return eval_combined_accessor(res, self)

    def is_list(self):
        return self.has_list_items

    def xparse(self, s, l, t):
        return t

    def render_parts(self, res):
        self.leading = self.render_leading(res)
        self.trailing = self.render_trailing(res)

    def render_indent(self):
        render_level = (self.ancestor.base_render_level + self.render_level)
        indent = ' ' * self.base_indent + ' ' * render_level * 2
        return indent

    def render_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        if res.has('attributes'):
            attributes = self.render_attributes(res)
        else:
            attributes = ''
        id_classes = self.render_id_classes(res)
        out = '<{}{}{}>'.format(descriptor, id_classes, attributes)
        return out

    def render_inline_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        attributes = self.render_attributes(res)
        id_classes = self.render_id_classes(res)
        value = ''

        if res.has('inline_content'):
            value = self.render_inline_content(res.inline_content)
        elif res.has('expression'):
            value = self.eval_expression(res['expression'].token)
        out = '<{}{}{}>{}'.format(descriptor, id_classes, attributes, value)
        return out

    def render_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = ''
        if descriptor in void_elements:
            out += ''
        else:
            if not self.minimise and descriptor not in inline_elements:
                render_level = (self.ancestor.base_render_level + self.render_level)
                out += ' ' * self.base_indent + ' ' * render_level * 2
            out += '</{}>'.format(descriptor)
            if not self.minimise:
                out += '\n'
        return out

    def render_inline_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = '</{}>'.format(descriptor)
        return out

    def render_inline_semantics(self, res):
        out = ''
        if res.has('inline_semantics_element'):
            out += self.render_inline_start_tag(res.inline_semantics_element)
            out += res.inline_semantics_element.inline_semantics_content.inline_semantic_content_words.value
            out += self.render_inline_end_tag(res.inline_semantics_element)
        if res.has('trailing_space'):
            out += ' '
        return out

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        if res.has('descriptor'):
            start_tag = self.render_start_tag(res)
        else:
            start_tag = ''
        value = ''
        if res.has('inline_content'):
            value = self.render_inline_content(res.inline_content)
        elif res.has('expression'):
            value = self.eval_expression(res.expression)
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + value
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading

    def render_trailing(self, res):
        if res.has('descriptor'):
            return self.render_end_tag(res)
        else:
            return ''

    def render_descriptor(self, res):
        if res.has('descriptor'):
            return res.descriptor.value
        else:
            return ''

    def eval_arith_expression(self, res):
        expr = ''.join(res.arith_expression)
        del exprStack[:]
        ARITH_EXPRESSION.parseString(expr, parseAll=True)
        return evaluateStack(exprStack)

    def eval_boolean(self, res):
        if res.boolean.value == 'True':
            return True
        elif res.boolean.value == 'False':
            return False

    def render_boolean(self, res):
        return str(self.eval_boolean(res))

    def eval_literal(self, res):
        # note that this works by using addParseAction(removeQuotes) in LITERAL
        value = res.literal.value
        return value

    def render_literal(self, res):
        return str(self.eval_literal(res))

    def eval_model_instantiation(self, res):
        model_descriptor = res.descriptor.value
        argument_values = list()
        if res.has('arguments'):
            for argument in res.arguments.list:
                argument_value = self.eval_expression(argument)
                argument_values.append(argument_value)
        if model_descriptor in self.document.models:
            model = self.document.models[model_descriptor]
            return model.create_object(arguments=argument_values)
        else:
            raise Exception('Model {} is not defined.'.format(model_descriptor))

    def eval_expression(self, res):
        if res.has('combined_accessor'):
            return eval_combined_accessor(res.combined_accessor.list, self)
        elif res.has('model_instantiation'):
            return self.eval_model_instantiation(res.model_instantiation)
        elif res.has('arith_expression'):
            return self.eval_arith_expression(res)
        elif res.has('boolean'):
            return self.eval_boolean(res)
        elif res.has('literal'):
            return self.eval_literal(res)
        elif res.has('descriptor'):
            return self.eval_framework_component(res)
        elif res.has('component_descriptor'):
            return self.eval_component(res)
        elif res.has('value_accessor'):
            # might lead to endless loop ?
            return self.eval_value_accessor(res)
        elif res.has('resource_accessor'):
            document = zml.document.Document()
            resource = self.document.resources[res.resource_accessor.resource.value]
            resource.import_resource(document)
            return document
        elif res.has('meta_data') or res.has('resource') or res.has('context_item') or res.has('context_item_with_property'):
            return self.eval_context_item(res)
        elif res.has('translation_accessor'):
            return eval_translation(res.translation_accessor, self)

    def eval_attribute_value(self, attribute_value):
        if attribute_value.has('quoted_moustache'):
            return self.render_moustache(attribute_value.quoted_moustache)
        elif attribute_value.has('quoted_string'):
            return attribute_value.quoted_string.value
        elif attribute_value.has('number'):
            return attribute_value.number.value
        elif attribute_value.has('literal'):
            return attribute_value.literal.value
        elif attribute_value.has('context_item'):
            return self.eval_context_item(attribute_value)
        elif attribute_value.has('context_item_with_property'):
            return self.eval_context_item(attribute_value)
        elif attribute_value.has('model_descriptor'):
            return eval_model(attribute_value.model_descriptor.value, self)
        elif isinstance(attribute_value, str):
            return attribute

    def render_attribute(self, attribute):
        out = ' '
        out += attribute.attribute_key.value
        if attribute.has('attribute_value'):
            out += '="{}"'.format(self.eval_attribute_value(attribute.attribute_value))
        return out

    def render_attributes(self, res):
        if res.attributes:
            return ' '.join(
                [''.join(
                    [self.render_attribute(attribute) for attribute in res.attributes.list]
                )]
            )
        else:
            return ''

    def render_id_classes(self, res):
        out = ''
        if res.has('id_classes'):
            id_classes = res.id_classes
            if id_classes.has('uid'):
                out += ' id="{}"'.format(id_classes.uid.value)
            if id_classes.has('classes') and len(id_classes.classes.list) > 0:
                classes = [item.value for item in id_classes.classes.list]
                out += ' class="{}"'.format(' '.join(classes))
        return out

    def render_segment(self, segment):
        out = ''
        if segment.has('inline_content_words'):
            # if segment.has('inline_content_newlines_leading'):
            #     out += '\n'
            out += self.render_words(segment.inline_content_words)
            # if segment.has('inline_content_newlines_trailing'):
            #     out += '\n'
        if segment.has('inline_content_newlines'):
            # out += ''.join(self.get_token(item))
            out += 'deleteme'
        if segment.has('inline_content_newlines_prefix'):
            out += '\n'
        if segment.has('inline_content_newlines_leading'):
            out += '\n'
        if segment.has('inline_content_newlines_trailing'):
            out += '\n'
        if segment.has('inline_semantics'):
            # out += self.render_inline_semantics(self.get_token(item))
            out += self.render_inline_semantics(segment.inline_semantics)
        if segment.has('moustache'):
            moustache = segment.moustache
            out += self.render_moustache(moustache)
#                if item_type == 'translation_accessor':
#                    out += render_translation(item[1], self)
        return out

    def render_inline_content(self, res):
        # todo: add inline slot rendering
        out = ''
        if res.has('inline_content_segments'):
            for segment in res.inline_content_segments.list:
                out += self.render_segment(segment)
        return out

    def render_words(self, res):
        out = res.value
        return out

    def eval_value_accessor(self, res):
        return self.get_var('_value')

    def render_value_accessor(self, res):
        return self.eval_value_accessor(res)

    def _render_component(self, component_descriptor):
        namespace = self.document.namespace
        component = None
        # rendered_view_source = local_indent
        rendered_view_source = ''
        if component_descriptor in self.document.namespaces[namespace]:
            component = self.document.namespaces[namespace][component_descriptor]
        elif component_descriptor in self.inherited_document.namespaces[namespace]:
            component = self.inherited_document.namespaces[namespace][component_descriptor]
        if component:
            component_node = deepcopy(component)
            component_node.parent = self
            # component_node.ancestor = self.ancestor
            component_node.base_render_level = self.render_level
            if not self.parent.is_component and not self.parent.is_code:
                component_node.base_render_level += 1

            component_node.render_level = component_node.base_render_level
            # local_indent = ' ' * self.render_level * 2
            self.renderer.base_render_level = self.render_level
            rendered_component = component_node.render_subtree(self.renderer)
            rendered_view_source += rendered_component
        # strip last newline, as it would double with the inline content's trailing newline
        rendered_view_source = rendered_view_source.rstrip()
        return rendered_view_source

    def render_component(self, res):
        # prepend local indent on each line
        component_descriptor = res.component_descriptor.value
        # prepend newline, because view will be included in inline content,
        # which is missing a leading newline
        return '\n' + self._render_component(component_descriptor)

    def eval_framework_component(self, res):
        framework_component = res.framework_component.value
        if res.has('moustache_attributes'):
            params = dict()
            for attribute in res.moustache_attributes.list:
                key = attribute.moustache_attribute_key.value
                value = attribute.moustache_attribute_value.value
                if attribute.moustache_attribute_value.has('context_accessor'):
                    value = self.local_context
                params[key] = value
            return framework_components[framework_component](self.document).execute(params)

    def render_framework_component(self, res):
        return self.eval_framework_component(res)

    def render_combined_accessor(self, res):
        return str(eval_combined_accessor(res, self))

    def get_token(self, res):
        raise "xxx get_token not implemented"
        if isinstance(res, ResultToken):
            token = res.token[res.marker]
            return token
        else:
            return res

    def render_moustache(self, res):
        res = res.expression
        out = ''
        # out += self.get_token(res)
        if res.has('framework_component'):
            out += self.render_framework_component(res)
        elif res.has('component_descriptor'):
            out += self.render_component(res)
        elif res.has('value_accessor'):
            out += self.render_value_accessor(res)
        # elif res.has('context_item'):
        #     out += self.render_combined_accessor(res)
        elif res.has('combined_accessor'):
            out = self.render_combined_accessor(res.combined_accessor.list)
        elif res.has('translation_accessor'):
            out += render_translation(res.translation_accessor, self)
        return out

    def process_subtree(self, processor=None):
        processor.process(self)

    def render_subtree(self, renderer=None):
        out = renderer.render(self)
        return out

    def get_children_type(self):
        return None


# class TextNode(Node):
#
#     expression = ELEMENT

#     def xrender_leading(self, res):
#         descriptor = self.render_descriptor(res)
#         start_tag = ''
#         if 'inline_content' in res:
#             inline_content = self.render_inline_content(res['inline_content'].token)
#             self.set_var('_value', inline_content)
#         else:
#             inline_content = ''
#         leading = ''
#         if not self.minimise:
#             leading += self.render_indent()
#         leading += start_tag + inline_content
#         if not self.minimise and descriptor not in inline_elements:
#             leading += '\n'
#         return leading

    # def render_subtree(self, renderer=None):
    #     return ''


class EmptyNode(Node):

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        start_tag = ''
        inline_content = ''
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + inline_content
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading

    def render_subtree(self, renderer=None):
        return ''


class ComponentNode(Node, Function):

    expression = LINE
    glyph = '*'

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        Function.__init__(self, **kwargs)
        # super().__init__(*args, **kwargs)
        self.is_component = True
        self.caller_inline_content = None
        self.caller_children = None

    def is_function(self):
        return True

    def process(self, lazy=False):
        self.tokens = parse(self.expression, self.line).component_definition
        descriptor = self.tokens.descriptor.value
        if self.document.namespace not in self.document.namespaces:
            self.document.namespaces[self.document.namespace] = dict()
        self.document.namespaces[self.document.namespace][descriptor] = self
        if self.tokens.has('arguments'):
            self.arguments = [argument.value for argument in self.tokens.arguments.list]
        if isinstance(self.parent, ModelNode):
            self.parent.set_function(self.descriptor, self)

    def render(self):
        pass

    def process_subtree(self, processor=None):
        # dont process subtree, as we only process the subtree when calling the component
        # processor.process(self)
        # only define the function arguments and keyword_arguments
        self.process()


class ComponentCallNode(Node):

    expression = COMPONENT_CALL
    glyph = '*'

    def process(self, lazy=False):
        if not lazy:
            self.tokens = parse(self.expression, self.line)

    def render(self):
        self.process()
        namespace = self.tokens.namespace.value
        descriptor = self.tokens.component_descriptor.value
        component_node = deepcopy(self.document.namespaces[namespace][descriptor])
        component_node.parent = self.parent
        component_node.ancestor = self.ancestor
        # the component call inherits the total render_level of parent and the parent's ancestor to the component
        component_node.base_render_level = self.parent.render_level + self.parent.ancestor.base_render_level
        if self.tokens.has('inline_content'):
            component_node.caller_inline_content = self.tokens.inline_content
        component_node.caller_children = self.children
        self.renderer.base_render_level = self.render_level
        if not self.parent.is_component and not self.parent.is_code:
            component_node.base_render_level += 1
        if self.tokens.has('attributes'):
            for attribute in self.tokens.attributes.list:
                attribute_key = attribute.attribute_key.value
                attribute_value = self.eval_attribute_value(attribute.attribute_value)
                component_node.set_var(attribute_key, attribute_value)
        if self.tokens.has('inline_content'):
            value = self.render_inline_content(self.tokens.inline_content)
            component_node.set_var('_value', value)
        children = []
        for child in self.children:
            children.append(child.render_subtree(self.renderer))
        component_node.set_var('_children', children)
        out = ''
        out += component_node.render_subtree(self.renderer)
        self.leading = out
        return out


class ListItemNode(Node):

    expression = LIST_ITEM

    def process(self, lazy=False):
        if not lazy:
            self.tokens = parse(self.expression, self.line)
            self.parent.has_list_items = True
            # if self.parent.descriptor not in self.local_context:
            #    self.set_var(self.parent.descriptor, list())
            if not isinstance(self.parent.value, list):
                self.parent.value = list()
            if isinstance(self.parent, DataNode):
                # self.document.local_context[self.parent.descriptor] = self.parent.value
                self.local_context[self.parent.descriptor] = self.parent.value
            if self.tokens.has('inline_content'):
                self.value = self.render_inline_content(self.tokens.inline_content)
            elif self.tokens.has('expression'):
                self.value = self.eval_expression(res.expression)
            else:
                self.value = dict()
            self.parent.value.append(self.value)

    def render(self):
        self.process()


class TranslationNode(Node):

    expression = TRANSLATION
    glyph = '!'

    def process(self, lazy=False):
        self.value = dict()
        self.document.translations[self.descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return AssignmentNode


class AssignmentNode(Node):

    expression = ASSIGNMENT

    def process(self, obj=None, lazy=False):
        # first set local context to objects local context
        # TODO: correct this to set local_context to empty dict?
        # if obj is not None:
        #     self.local_context = obj.local_context
        res = parse(self.expression, self.line).assignment
        descriptor = res.descriptor.value
        value = ''
        if res.has('assignment_value'):
            if res.assignment_value.has('inline_content'):
                value = self.render_inline_content(res.assignment_value.inline_content)
            elif res.assignment_value.has('expression'):
                value = self.eval_expression(res.assignment_value.expression)
        # self.parent.set_var(descriptor, value)
        if res.glyph.value == '.':
            # assignment to property, set value to object property
            obj.set_property(res.descriptor.value, value)
        if isinstance(self.parent, AssignmentNode) or isinstance(self.parent, ListItemNode) or isinstance(self.parent,
                                                                                                          TranslationNode):
            if self.parent.value is None:
                self.parent.value = dict()
            if value:
                self.parent.value[descriptor] = value
            else:
                self.value = dict()
                self.parent.value[descriptor] = self.value
        elif isinstance(self.parent, DataNode):
            if self.local_context[self.parent.descriptor] in [None, '']:
                self.local_context[self.parent.descriptor] = dict()
            if value:
                self.local_context[self.parent.descriptor][descriptor] = value
            else:
                self.value = dict()
                self.local_context[self.parent.descriptor][descriptor] = self.value
        else:
            # TODO: check, if this works with all tests
            # TODO: differntiate between property and data node assignment
            self.local_context[descriptor] = value

    def render(self):
        pass
        # self.process()


class FieldPropertyNode(Node):

    expression = ASSIGNMENT

    def process(self, lazy=True):
        res = parse(self.expression, self.line).assignment
        descriptor = res.descriptor.value
        glyph = res.glyph.value
        if res.has('inline_content'):
            value = self.render_inline_content(res.inline_content)
        elif res.has('assignment_value'):
            value = self.eval_expression(res.assignment_value.expression)
        if glyph == '&':
            # define meta data
            if descriptor == 'type':
                # self.parent.value.type = value
                self.parent.type = value
            if descriptor == 'label':
                # self.parent.value.label = value
                self.parent.label = value

    def render(self):
        self.process()


class FieldNode(Node, Field):

    expression = FIELD_DEFINITION
    glyph = '.'

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        Field.__init__(self, **kwargs)

    def process(self, lazy=False):
        res = parse(self.expression, self.line)
        descriptor = res.field_definition.descriptor.value
        # self.value = Field(descriptor)
        # self.parent.value.fields[descriptor] = self.value
        # self.parent.fields[descriptor] = self.value
        self.parent.fields[descriptor] = self

    def render(self):
        self.process()

    def get_children_type(self):
        return FieldPropertyNode


class ModelNode(Node, Model):

    expression = MODEL
    glyph = '+'

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        Model.__init__(self, **kwargs)
        res = parse(self.expression, self.line)
        self.descriptor = res.model_descriptor.value

    def process(self, lazy=False):
        # we want to isolate the document tree and nodes from the model in order to keep the model decoupled and
        # simple, TODO: decide if we keep this pattern
        # self.value = Model(self.descriptor)
        self.document.models[self.descriptor] = self

    def render(self):
        self.process()

    # def get_children_type(self):
    #     return FieldNode


class ResourceNode(Node):

    expression = RESOURCE
    glyph = '@'

#    def __init__(self):
#        super(ResourceNode, self).__init__()
#        if self.line:
#            res = self.expression.parseString(self.line)
#            self.address = res['source']
#            self.resource = Resource(address, lazy=True)

    def process(self, lazy=False):
        res = parse(self.expression, self.line)
        address = res.source.value
        self.resource = Resource(address)
        self.document.resources[self.descriptor] = self.resource

    def render(self):
        self.process()


class RouteNode(Node):

    expression = ROUTE

    def process(self, lazy=False):
        res = parse(self.expression, self.line)
        router_descriptor = self.parent.descriptor
        route_descriptor = res.descriptor.value
        # currently also nodes have a global_context and a local_context
        # todo design decision for rendering contexts (see module's render_source function)
        router = self.document.router
        if router_descriptor not in router:
            router[router_descriptor] = dict()

            router[router_descriptor][route_descriptor] = res.route_path.path_items.list
            self.document.default_router = router[router_descriptor]
        else:
            router[router_descriptor][route_descriptor] = res.route_path.path_items.list

    def render(self):
        self.process()


class RouterNode(Node):

    expression = LINE
    glyph = '~'

    def process(self, lazy=False):
        pass

    def get_children_type(self):
        return RouteNode

    def render(self):
        self.process()
        # we have to overwrite render to prevent rendering as Node
        pass


class DataNode(Node):

    expression = DATA_NODE
    glyph = '#'

    def is_data(self):
        return True

    def process(self, lazy=False):
        res = parse(self.expression, self.line)
        descriptor = res.data_node_descriptor.value
        if res.has('data_node_value'):
            data_node_value = res.data_node_value
            value = ''
            if data_node_value.has('inline_content'):
                value = self.render_inline_content(data_node_value.inline_content)
            elif data_node_value.has('expression'):
                value = self.eval_expression(data_node_value.expression)
            self.local_context[descriptor] = value

    def render(self):
        self.process()

    # def get(self, path):
    #    res = COMBINED_ACCESSOR.parseString(path)
    #    return res


class MetaNode(Node):

    expression = LINE
    glyph = '&'

    def is_meta(self):
        return True

    def process(self, lazy=False):
        res = parse(self.expression, self.line, parse_all=False)
        descriptor = res.descriptor.value
        self.meta_data[descriptor] = self.value

    def render(self):
        self.process()


class SlotNode(Node):

    expression = SLOT_NODE
    glyph = '|'

    def __init__(self, *args, **kwargs):
        self.descriptor = kwargs['descriptor']
        super().__init__(*args, **kwargs)

    def render(self):
        if self.descriptor in self.document.dispatched_views:
            view_name = self.document.dispatched_views[self.descriptor]
            namespace = self.document.namespaces[self.document.namespace]
            if view_name in namespace:
                rendered_component = self._render_component(view_name)
                self.leading = rendered_component + '\n'
                return ''  # rendered_component
        else:
            return ''


class CodeNode(Node):

    expression = CODE
    glyph = '%'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_code = True

    def is_instruction(self):
        if self.descriptor in ['inherit', 'import', 'include', 'namespace']:
            return True
        else:
            return False

    def process_subtree(self, processor):
        self.tokens = parse(self.expression, self.line)
        __import__('pdb').set_trace()
        if self.tokens.has('for_loop'):
            processor.subtree_handler_for_loop(self)
        elif self.tokens.has('if_statement'):
            processor.subtree_handler_if_statement(self)
        if self.is_instruction():
            processor.process(self)

    def render_subtree(self, renderer):
        self.tokens = parse(self.expression, self.line)
        out = ''
        if self.tokens.has('for_loop'):
            out += renderer.subtree_handler_for_loop(self)
        elif self.tokens.has('if_statement'):
            out += renderer.subtree_handler_if_statement(self)
        if self.is_instruction():
            out += renderer.render(self)
        return out

    def process_inherit(self, res):
        if res.has('documentfile'):
            documentfile = res.documentfile.value
            if not documentfile.endswith('.zml'):
                documentfile += '.zml'
            self.document.inheriting_document = documentfile
        elif res.has('resource_accessor'):
            resource_name = res.resource_accessor.resource.value
            if resource_name in self.document.resources:
                self.document.inheriting_document = self.document.resources[resource_name]

    def process_import(self, res):
        if res.has('documentfile'):
            documentfile = res.documentfile.value
            if not documentfile.endswith('.zml'):
                documentfile += '.zml'
            self.document.import_document(documentfile)
        elif res.has('resource_accessor'):
            resource_descriptor = res.resource_accessor.resource.value
            self.document.resources[resource_descriptor].import_resource(self.document)
        # return root

    def process_include(self, res):
        out = render(filename,
                     local_context=self.document.local_context,
                     base_indent=base_indent)
        return out

    def process_namespace(self, res):
        self.document.namespace = res.namespace.value

    def process(self, lazy=False):
        res = parse(self.expression, self.line)
        if res.has('instruction'):
            instruction = res.instruction.value
            if instruction == 'inherit':
                self.process_inherit(res)
            elif instruction == 'import':
                self.process_import(res)
            elif instruction == 'include':
                self.process_include(res)
            elif instruction == 'namespace':
                self.process_namespace(res)

    def render(self, lazy=False):
        self.process(lazy)
        return ''
