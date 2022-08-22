from sys import exit as sys_exit
from .zetsubou import main as zet_main
# import cProfile
# import time

# import yaml
# from yaml.composer import Composer
# from yaml.constructor import Constructor

# import ruamel.yaml as ruamel

# def load_content(filename:str):
#     with open(filename, 'r') as file:
#         return file.read()

# class ProfileScope:
#     def __init__(self, print_stats:bool, label:str = ''):
#         self.pr = cProfile.Profile()
#         self.print_stats = print_stats
#         self.label = label

#     def __enter__(self):
#         self.pr.enable()
#         self.start_time = time.time()

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         end_time = time.time()
#         self.pr.disable()

#         print(f'{self.label} took: {end_time - self.start_time}')

#         if self.print_stats:
#             self.pr.print_stats(sort='time')


# def test_ruamel(content:str):
#     with ProfileScope(print_stats=False, label='Ruamel'):
#         ruamel.load(content)


# def test_ruamel_new(content:str):
#     with ProfileScope(print_stats=False, label='Ruamel New'):
#         yml = ruamel.YAML(typ='rt', pure=True)
#         yml.load(content)


# def test_yaml(content:str):
#     with ProfileScope(print_stats=False, label='Yaml'):
#         yaml.load(content)


# def test_yaml_lines(content:str):
#     with ProfileScope(print_stats=False, label='Yaml Lines'):
#         loader = yaml.Loader(content)
#         def compose_node(parent, index):
#             # the line number where the previous token has ended (plus empty lines)
#             line = loader.line
#             node = Composer.compose_node(loader, parent, index)
#             node.__line__ = line + 1
#             return node
#         def construct_mapping(node, deep=False):
#             mapping = Constructor.construct_mapping(loader, node, deep=deep)
#             mapping['__line__'] = node.__line__
#             return mapping
#         loader.compose_node = compose_node
#         loader.construct_mapping = construct_mapping
#         data = loader.get_single_data()


# def profile_yaml_loaders(filename:str):
#     content = load_content(filename)

#     test_yaml_lines(content)
#     test_yaml(content)
#     test_ruamel(content)
#     test_ruamel_new(content)


# profile_yaml_loaders('example/configurations/MsvcRules.yml')

sys_exit(zet_main())
