from setuptools import setup,find_packages
setup(name='easyBar',
      version='0.0.2',
      description='an easy processbar',
      author='Lfanke',
      author_email='chengkelfan@foxmail.com',
      requires= [], # 定义依赖哪些模块
      packages=["."],  # 系统自动从当前目录开始找包
      # 如果有的文件不用打包，则只能指定需要打包的文件
           license="apache 3.0",
long_description='一个简易的进度条'
      )
