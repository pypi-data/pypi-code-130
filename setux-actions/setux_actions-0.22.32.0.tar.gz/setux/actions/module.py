from setux.core.action import Runner, Actions


class Moduler(Runner):
    @property
    def label(self):
        return self.module

    def deploy(self):
        return self.target.deploy(self.module)


class Modules(Actions):
    @property
    def label(self):
        return f'Modules {self.name}'

    @property
    def actions(self):
        return [
            Moduler(self.target, module=module)
            for module in self.modules
        ]

