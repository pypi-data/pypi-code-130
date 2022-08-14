from pybrary.command import Command


class OutLog(Command):
    '''show commands log
    '''
    def run(self):
        target = self.get('target')
        log = target.outlog
        print(open(log).read())
