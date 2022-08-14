from pybrary.command import Command


class OutRun(Command):
    '''show commands history
    '''
    def run(self):
        target = self.get('target')
        log = target.outrun
        print(open(log).read())
