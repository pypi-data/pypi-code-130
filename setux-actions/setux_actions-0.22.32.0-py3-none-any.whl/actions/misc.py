from setux.logger import silent
from setux.core.action import Runner


class Pinger(Runner):
    @property
    def labeler(self):
        return silent

    @property
    def label(self):
        return 'ping'

    def deploy(self):
        return self.target.ping()

