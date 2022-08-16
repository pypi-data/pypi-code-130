import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JsonCompiler:
    template: str
    context: dict
    value = None
    _opening = '"{{'
    _closing = '}}"'

    def compile(self):
        t_ = str(self.template)
        for k_context, v_context in self.context.items():
            t_ = t_.replace(self._pattern(k_context), json.dumps(v_context))
        self.value = t_

    @classmethod
    def from_file(cls, template_path: Path, context_path: Path):
        with open(template_path, "r") as f_:
            template_ = f_.read()
        with open(context_path, "r") as f_:
            context_ = json.load(f_)
        return cls(template=template_, context=context_)

    def to_json(self):
        self.compile()
        return self.value

    def to_py(self):
        return json.loads(self.to_json())

    def to_file(self, save_path: Path):
        with open(save_path, "w") as f_:
            f_.write(self.to_json())

    def _pattern(self, key):
        return self._opening + key + self._closing
