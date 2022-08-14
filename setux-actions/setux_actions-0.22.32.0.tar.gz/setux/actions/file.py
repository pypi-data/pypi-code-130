from setux.core.action import Action


class Directory(Action):
    @property
    def label(self):
        return f'dir {self.path}'

    def check(self):
        directory = self.target.dir.fetch(
            self.path,
            **self.spec,
        )
        return directory.check() is True

    def deploy(self):
        directory = self.target.dir.fetch(
            self.path,
            **self.spec,
        )
        return directory.deploy() is True
