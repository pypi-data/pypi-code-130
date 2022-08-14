from setux.logger import silent
from setux.core.action import Action


class Updater(Action):
    @property
    def label(self):
        return f'upd {self.path}'

    def check(self):
        cont = self.target.read(
            self.path,
            sudo = self.sudo,
            report = 'quiet',
        )
        return self.line in cont

    def deploy(self):
        self.target.deploy('upd_cfg',
            path   = self.path,
            line   = self.line,
            select = self.select,
            user   = self.user,
            group  = self.group,
            mode   = self.mode,
            sudo   = self.sudo,
        )

        self.target.file(
            self.path,
            user  = self.user,
            group = self.group,
            mode  = self.mode,
            sudo  = self.sudo,
            verbose = False,
        )

        return True
