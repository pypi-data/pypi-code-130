from helper.logging import CriticalException
from rule.rules.abstract import AbstractExecutionRule


class GetItemRule(AbstractExecutionRule):
    def _get_inputs(self):
        return {'data', 'index'}

    def _str(self):
        return f'"data": {self.data.node_id}, "index": {self.index}'

    @classmethod
    def run(cls, inputs):
        if inputs['index'] not in inputs['data']:
            raise CriticalException(f'Index "{inputs["index"]}" not found in data.')

        return inputs['data'][inputs['index']], None

    @staticmethod
    def get_yaml_tag():
        return u'!get_item'
