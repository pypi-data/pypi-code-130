SUBMIT_GIT = False
NAME = 'zqpy'
DESCRIPTION = '使用老版本:pip install zqpy==0.1.48 \n 使用新版本:pip install zqpy \n 新老版本区别在于：最前面位 0（老版本）1（新版本）'
URL = 'https://gitee.com/qingBB/zqpy'
EMAIL = '1620829248@qq.com'
AUTHOR = '周清'
REQUIRES_PYTHON = '>=3'
# use in __version__.py
VERSION = False
# use in requirements.txt
REQUIRED = False 
# opertion require package


import os, sys
from setuptools import find_packages, setup, Command
import setup_file as zq_file

here_curr = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here_curr, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# VERSION 每次提交自动升级，所以不需要再手动改，除非是大版本提交
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here_curr, project_slug, '__version__.py')) as f:
        about = {}
        exec(f.read(), about)
        VERSION = about['__version__']

if not REQUIRED:
    content = zq_file.file_read('%s/%s/requirements.txt'%(here_curr, NAME))
    content = content.replace('~pencv_python', 'opencv_python')
    zq_file.file_write('%s/%s/requirements.txt'%(here_curr,NAME), content)
    REQUIRED = content.splitlines()

class UploadCommand(Command):
    """setup.py  upload"""

    user_options = []
    @staticmethod
    def status(s):
        """print"""
        print('\033[1m{0}\033[0m'.format(s))
    

    def initialize_options(self):
        print('初始化选项')

    def finalize_options(self):
        print('最终选项')

    def run(self):
        print('开始运行')

        self.status('build source wheel(general) distribution')
        os.system('%s setup.py sdist bdist_wheel --universal'%(sys.executable))

        self.status('pass twine upload PyPI')
        os.system('twine upload --repository-url https://upload.pypi.org/legacy/ dist/*')

        print(sys.executable, os.getcwd(), os.path.abspath('./build/lib'))
        for item in sys.path:
            if item.endswith("\\lib\\site-packages"):
                zq_file.dir_copy("./build/lib", item)
                print('./build/lib -> 复制到 %s\n\n'%item)

        self.status('push to git')
        if SUBMIT_GIT:
            os.system('git tag v{0}'.format(VERSION))
            os.system('git push --tags')
            os.system('git add .')
            os.system('git stage')
            os.system('git commit -m "{0}{1}"'.format(VERSION, input('请输入提交日志信息-> ')))
            os.system('git push')

        os.chdir(here_curr)
        # 自动升级下一个小版本
        versionPath = os.path.join(here_curr, NAME, '__version__.py')
        strValue = zq_file.file_read(versionPath)
        versionList = VERSION.split('.')
        strValue = strValue.replace(versionList[2],str(int(versionList[2])+1), -1)
        zq_file.file_write(versionPath, strValue)
        print('自动版本号+1  完成\n\n')

        Clear()
        # sys.exit()
        input()

def Clear():
    for item in ["build", "dist", "__pycache__", "%s.egg-info"%NAME]:
        zq_file.dir_remove('%s/%s'%(here_curr, item), True)
Clear()
setup(
    name=NAME,                      #包名称
    version=VERSION,                #包版本
    author=AUTHOR,                  #程序的作者
    author_email=EMAIL,             #程序的作者的邮箱地址
    maintainer=AUTHOR,              #维护者
    maintainer_email=EMAIL,         #维护者的邮箱地址
    url=URL,                        #程序的官网地址
    license='MIT',                  #程序的授权信息
    description=DESCRIPTION,        #程序的简单描述
    long_description=long_description,  #程序的详细描述
    long_description_content_type='text/markdown', #程序的详细描述类型
    # platforms=,                   #程序适用的软件平台列表
    classifiers=[                   #程序的所属分类列表
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # keywords=,                    #程序的关键字列表
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),   #需要处理的包目录(通常为包含 __init__.py 的文件夹)
    py_modules=[],                  #需要打包的 Python 单文件列表
    # download_url=,                #程序的下载地址
    cmdclass={                      #添加自定义命令
        'upload': UploadCommand,
    },
    # package_data=[],                   #指定包内需要包含的数据文件
    include_package_data=True,      #自动包含包内所有受版本控制(cvs/svn/git)的数据文件
    # exclude_package_data=[],        #当 include_package_data 为 True 时该选项用于排除部分文件
    # data_file=[],                   #打包时需要打包的数据文件，如图片，配置文件等
    ext_modules=[],                 #指定扩展模块
    scripts=[],                     #指定可执行脚本,安装时脚本会被安装到系统 PATH 路径下
    package_dir=[],                 #指定哪些目录下的文件被映射到哪个源码包
    # entry_points={                #动态发现服务和插件，下面详细讲
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },    
    python_requires=REQUIRES_PYTHON,    #指定运行时需要的Python版本
    requires=[],                    #指定依赖的其他包
    provides=[],                    #指定可以为哪些模块提供依赖
    install_requires=REQUIRED,      #安装时需要安装的依赖包
    extras_require={                #当前包的高级/额外特性需要依赖的分发包
        # 'fancy feature': ['django'],
    },          
    tests_require=[],               #在测试时需要使用的依赖包
    setup_requires=[],              #指定运行 setup.py 文件本身所依赖的包
    # dependency_links='',            #指定依赖包的下载地址
    zip_safe=False,                  #不压缩包，而是以目录的形式安装
)
