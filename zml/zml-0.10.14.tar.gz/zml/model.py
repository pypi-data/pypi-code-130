class Field:

    def __init__(self, descriptor, type=None, *args, **kwargs):
        self.descriptor = descriptor
        self.type = type
        self.label = ''


class Model:

    def __init__(self, descriptor, **kwargs):
        self.descriptor = descriptor
        self.fields = dict()
        self.functions = dict()

    def create_object(self, arguments=list(), keyword_arguments=dict()):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        obj = Object(self)
        obj.init(arguments, keyword_arguments)
        return obj

    def get_field(self, descriptor):
        if descriptor in self.field:
            return self.fields[descriptor]
        else:
            raise Exception('Field {} not defined.'.format(descriptor))

    def add_field(self, descriptor, field):
        self.fields[descriptor] = field

    # @property
    # def fields(self):
    #     return self.fields.values()

    def get_function(self, descriptor):
        if descriptor in self.functions:
            return self.functions[descriptor]
        else:
            raise Exception('Function {} not defined.'.format(descriptor))

    def add_function(self, descriptor, arguments=list(), keyword_arguments=dict()):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        self.functions[descriptor] = Function(descriptor, arguments, keyword_arguments)

    def set_function(self, descriptor, function):
        self.functions[descriptor] = function

    def call_function(self, instance, descriptor, arguments=list(), keyword_arguments=dict()):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        if descriptor in self.functions:
            self.functions[descriptor].call(instance, arguments, keyword_arguments)
        else:
            raise Exception('Function not defined')


class Object:

    def __init__(self, model=None):
        self.model = model
        self.properties = dict()
        self.functions = dict()
        # self.add_function('init')

    def init(self, arguments=list(), keyword_arguments=dict()):
        self.init_properties()
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        # First call model init then call object init
        # TODO: decide about strategy for initialisation
        if 'init' in self.model.functions:
            self.model.functions['init'].call(self, arguments, keyword_arguments)
        if 'init' in self.functions:
            self.functions['init'].call(self, arguments, keyword_arguments)

    def init_properties(self):
        init_value_mapping = {
            'str': '',
            'int': 0
        }
        if self.model:
            for field in self.model.fields.values():
                self.properties[field.descriptor] = init_value_mapping[field.type]

    def get_function(self, descriptor):
        if descriptor in self.model.functions:
            return self.model.functions[descriptor]
        elif descriptor in self.functions:
            return self.functions[descriptor]
        else:
            raise Exception('Function {} not defined.'.format(descriptor))

    def get_property(self, property):
        return self.properties[property]

    def add_property(self, property):
        self.properties[property] = None

    def set_property(self, property, value):
        self.properties[property] = value

    def add_function(self, descriptor, arguments=None, keyword_arguments=None):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        self.functions[descriptor] = Function(descriptor, arguments, keyword_arguments)

    def call_function(self, descriptor, arguments=None, keyword_arguments=None):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        if descriptor in self.functions:
            self.functions[descriptor].call(arguments, keyword_arguments)
        elif descriptor in self.model.functions:
            self.model.functions[descriptor].call(arguments, keyword_arguments)
        else:
            raise Exception('Function not defined')


class Function:

    def __init__(self, descriptor, arguments=list(), keyword_arguments=dict(), *args, **kwargs):
        self.descriptor = descriptor
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments
        self.local_context = dict()

    def call(self, instance, arguments=list(), keyword_arguments=dict()):
        if arguments is None:
            arguments = list()
        if keyword_arguments is None:
            keyword_arguments = dict()
        if len(arguments) > len(self.arguments):
            raise Exception('Too many arguments in function call')
        if not isinstance(arguments, list):
            raise Exception('Arguments must be list')
        if not isinstance(keyword_arguments, dict):
            raise Exception('Keyword arguments must be dict')
        for i, argument in enumerate(arguments):
            self.local_context[self.arguments[i]] = argument
        for keyword_argument in keyword_arguments:
            if keyword_argument not in self.keyword_arguments.keys():
                raise Exception('Keyword argument {} is not allowed '.format(keyword_argument))
            self.local_context[keyword_argument] = keywords_arguments[keyword_argument]
        for child in self.children:
            child.process(obj=instance)
        # print('Function {} of instance {} called with {}, {}'.format(self.descriptor, instance, arguments, keyword_arguments))
