class Terminal:
    def __init__(self, name):
        self.name = name
        self.os = __import__('os')
        self.os.popen('@chcp 65001')
        self.username = self.os.popen('echo %username%').read()
    def command(self, c):
        print(self.name,self.os.popen(c).read(),sep=':')
    def input(self):
        print(self.name,self.os.popen(input(self.os.getcwd() + '>')).read(),sep=':')
    def delete(self):
        print(self.username,'删除了',self.name,sep='')
        del self

