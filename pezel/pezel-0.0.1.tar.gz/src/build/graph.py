import networkx as nx
import yaml

from helper.artifact import ArtifactTypes
from helper.dictionary import flatten_dict
from helper.interface import BuildUI
from helper.logging import CriticalException
from rule.rules.abstract import AbstractRule


BUILD_FILE_NAME = 'BUILD.yaml'


class BuildGraph(object):
    def _build(self):
        for build_file in self.root_path.rglob(BUILD_FILE_NAME):
            self._build_from_file(build_file)

        self.assert_valid()

    def _build_from_file(self, file_path):
        with open(file_path, 'r') as file:
            file_data = yaml.load(file, self.rule_loader)

        rules_stack = [(None, None, rule) for rule in file_data['rule']]
        while rules_stack:
            dependent_node_id, current_key, current_rule = rules_stack.pop()

            if dependent_node_id is None:
                if current_rule.is_anonymous:
                    raise CriticalException(f'Invalid root node: {current_rule.str()}')

                self.rules.append(current_rule.node_id)
            else:
                if current_rule.is_anonymous:
                    current_rule.anonymous_node_location = dependent_node_id

                self.graph.add_edge(dependent_node_id, current_rule.node_id, key=current_key)

            if not current_rule.is_pointer():
                self.graph.add_node(current_rule.node_id, data=current_rule)
                rules_stack.extend([
                    (current_rule.node_id, key, rule)
                    for key, rule in flatten_dict(current_rule.get_inputs())
                    if isinstance(rule, AbstractRule)])
            else:
                current_node_references = self.graph.nodes.get(current_rule.node_id, {}).get('references', [])
                current_node_references.append(current_rule)
                self.graph.add_node(current_rule.node_id, references=current_node_references)

    def _register_artifacts(self, artifacts):
        for artifact_type, artifact in artifacts:
            try:
                self.artifacts[artifact_type].append(artifact)
            except KeyError:
                raise CriticalException(f'Bad artifact type {artifact_type}')

    def __init__(self, root_path, rule_loader, rule_builder):
        self.root_path = root_path
        self.rule_loader = rule_loader
        self.rule_builder = rule_builder

        self.artifacts = {ArtifactTypes.IMAGE_TAG: []}
        self.rules = []
        self.graph = nx.DiGraph()

        self._build()

    def assert_valid(self):
        for node_id, node in self.graph.nodes.items():
            if 'data' not in node:
                references = [f'- {reference.str()}\n' for reference in self.graph.nodes[node_id]['references']]
                references_str = '\n'.join(references)
                raise CriticalException(f'Undeclared node, "{node_id}", used in in the following {len(references)} place(s):\n{references_str}')

    def build_rule(self, node_id):
        build_tree = self.graph.subgraph(nx.descendants(self.graph, node_id) | {node_id})
        build_order = list(nx.dfs_postorder_nodes(build_tree, node_id))

        with BuildUI(node_id, build_tree) as build_ui:
            for current_node_i, current_node_id in enumerate(build_order):
                try:
                    build_ui.building_node(current_node_id)
                    current_rule = self.graph.nodes[current_node_id]['data']

                    inputs = []
                    for _, input_node_id in self.graph.edges(current_node_id):
                        input_key = self.graph.edges[(current_node_id, input_node_id)]['key']
                        input_rule = self.graph.nodes[input_node_id]['data']
                        inputs.append((input_key, input_rule))

                    output, artifacts = self.rule_builder.build(current_rule, inputs)
                    if artifacts is not None:
                        self._register_artifacts(artifacts)
                except CriticalException as err:
                    err.set_failed_execution_node(self.graph.nodes[current_node_id]['data'])
                    raise err
                except Exception as err:
                    new_error = CriticalException.build_from_exception(err)
                    new_error.set_failed_execution_node(self.graph.nodes[current_node_id]['data'])
                    raise new_error

        return output
