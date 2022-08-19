import error
def main(self):
    while True:
        print(self.meun)
        try:
            s=int(input('请输入您要执行的操作序号'))
        except:
            error('int')
        if s==1:
            if self.server_list=={}:
                error('not_server')