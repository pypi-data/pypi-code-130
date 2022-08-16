import abc
import copy
import pathlib
import uuid
import yaml

from abc import ABCMeta

from helper.logging import CriticalException, dev_log_root


dev_log = dev_log_root.getChild(__name__)


class YamlNode(object):
    def __init__(self, node, root_path):
        self.node = node
        self.current_dir = pathlib.Path(self.node.start_mark.name).parent
        self.relative_path = pathlib.Path(self.node.start_mark.name).relative_to(root_path)

    def get_location_str(self):
        start_line = self.node.start_mark.line + 1
        end_line = self.node.end_mark.line + 1
        start_column = self.node.start_mark.column
        end_column = self.node.end_mark.column
        is_same_line = start_line == end_line
        is_same_column = start_column == end_column

        start_str = f'{self.relative_path} line {start_line} column {start_column}'
        if is_same_line and is_same_column:
            return start_str
        else:
            node_end_mark_line_str = f'line {end_line} ' if not is_same_line else ''
            node_end_mark_column_str = f'column {end_column} ' if not is_same_column else ''
            return f'{start_str} to {node_end_mark_line_str}{node_end_mark_column_str}'

    def get_value(self, loader):
        if isinstance(self.node, yaml.ScalarNode):
            return self.node.value
        elif isinstance(self.node, yaml.SequenceNode):
            return loader.construct_sequence(self.node, deep=True)
        elif isinstance(self.node, yaml.MappingNode):
            return loader.construct_mapping(self.node, deep=True)
        else:
            raise CriticalException(f'Unknown Node type {type(yaml.MappingNode)}.')

    def str(self):
        return f'{self.node.tag} in {self.get_location_str()}'


class AbstractRule(abc.ABC):
    BUILD_RULE_FLAG = ':'
    YAML_TAG_ARRAY_ENDING = '-array'

    @staticmethod
    def _build_node(from_yaml_fn, root_path, loader, node, host_root_path=None):
        yaml_node = YamlNode(node, root_path)
        try:
            return from_yaml_fn(root_path, loader, yaml_node, host_root_path=host_root_path)
        except CriticalException as err:
            err.set_failed_build_node(yaml_node)
            raise err
        except Exception as err:
            new_error = CriticalException.build_from_exception(err)
            new_error.set_failed_build_node(yaml_node)
            raise new_error

    @classmethod
    def _build_array_constructor(cls, root_path, from_yaml_fn, host_root_path=None):
        def _from_yaml_wrapper(loader, node):
            out = []
            for item in node.value:
                out.append(cls._build_node(from_yaml_fn, root_path, loader, item, host_root_path=host_root_path))

            return out

        return _from_yaml_wrapper

    @classmethod
    def _build_constructor(cls, root_path, from_yaml_fn, host_root_path=None):
        def _from_yaml_wrapper(loader, node):
            return cls._build_node(from_yaml_fn, root_path, loader, node, host_root_path=host_root_path)

        return _from_yaml_wrapper

    @classmethod
    @abc.abstractmethod
    def from_yaml(cls, root_path, loader, yaml_node, host_root_path=None):
        raise NotImplementedError('from_yaml function not implemented.')

    @staticmethod
    @abc.abstractmethod
    def get_yaml_tag():
        raise NotImplementedError('yaml_tag function not implemented.')

    @staticmethod
    def is_pointer():
        return False

    @classmethod
    def register_constructor(cls, loader, root_path, host_root_path=None):
        loader.add_constructor(
            cls.get_yaml_tag(),
            cls._build_constructor(root_path, cls.from_yaml, host_root_path=host_root_path))
        loader.add_constructor(
            f'{cls.get_yaml_tag()}{cls.YAML_TAG_ARRAY_ENDING}',
            cls._build_array_constructor(root_path, cls.from_yaml, host_root_path=host_root_path))


class AbstractBasicRule(AbstractRule, metaclass=ABCMeta):
    @abc.abstractmethod
    def _str(self):
        raise NotImplementedError('_str function not implemented.')

    def __init__(self, root_path, yaml_node, name=None, host_root_path=None):
        is_anonymous = name is None
        current_dir = yaml_node.current_dir

        if name is None:
            name = f':anonymous_{self.get_yaml_tag()}_{str(uuid.uuid4())}'
        elif self.BUILD_RULE_FLAG not in name:
            name = f'{self.BUILD_RULE_FLAG}{name}'

        if name[0] == self.BUILD_RULE_FLAG:
            node_id = f'{current_dir.relative_to(root_path)}{name}'
        else:
            node_id = name

        self.root_path = root_path
        self.current_dir = current_dir
        self.yaml_node = yaml_node
        self.host_root_path = host_root_path
        self.node_id = node_id
        self.is_anonymous = is_anonymous
        self.anonymous_node_location = None

    @classmethod
    def from_yaml(cls, root_path, loader, yaml_node, host_root_path=None):
        node_value = yaml_node.get_value(loader)
        if isinstance(node_value, dict):
            return cls(root_path, yaml_node, **node_value, host_root_path=host_root_path)
        else:
            return cls(root_path, yaml_node, node_value, host_root_path=host_root_path)

    def str(self):
        if not self.is_anonymous:
            return f'{self.node_id}'

        if self.anonymous_node_location is not None:
            return f'{self.anonymous_node_location} - Anonymous {self.get_yaml_tag()} node ({self._str()})'
        else:
            return f'Anonymous {self.get_yaml_tag()} node ({self._str()}), {self.yaml_node.get_location_str()}'


class AbstractExecutionRule(AbstractBasicRule):
    @classmethod
    def _args_to_kwargs(cls, args):
        raise CriticalException(f'{cls.get_yaml_tag()} doesn\'t support non keyword arguments')

    @abc.abstractmethod
    def _get_inputs(self):
        raise NotImplementedError('_get_inputs function not implemented.')

    def __init__(self, root_path, yaml_node, *args, name=None, host_root_path=None, **kwargs):
        if args:
            if len(args) > 1:
                raise CriticalException(f'Maximum of 1 non keyword argument. Found {len(args)} non keywords.')

            args = self._args_to_kwargs(args)
        else:
            args = {}

        kwargs = {**args, **kwargs}

        super().__init__(root_path, yaml_node, name, host_root_path=host_root_path)

        base_class_attributes = {'root_path', 'current_dir', 'host_root_path'}
        kwargs_inputs = set(kwargs.keys())
        inputs = self._get_inputs() - base_class_attributes
        if kwargs_inputs != inputs:
            try:
                self_str = self.str()  # Catch errors if properties missing are used by the `str` function
            except Exception:
                dev_log.warn('Failed to run str().')
                self_str = f'a {self.get_yaml_tag()} node'

            if kwargs_inputs - inputs:
                raise CriticalException(f'Unknown propertie(s) {kwargs_inputs - inputs} for {self_str}.')
            else:
                raise CriticalException(f'Missing propertie(s) {inputs - kwargs_inputs} for {self_str}.')

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_inputs(self):
        return {attr: copy.deepcopy(getattr(self, attr)) for attr in self._get_inputs()}

    @classmethod
    @abc.abstractmethod
    def run(cls, inputs):
        raise NotImplementedError('run function not implemented.')


class AbstractFileResult(abc.ABC):
    @abc.abstractmethod
    def get_file(self):
        raise NotImplementedError('get_file function not implemented.')

    def get_files(self):
        raise NotImplementedError('get_file function not implemented.')
