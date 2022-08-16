from silas import FileConfig, FileType


class MyFileConfig(FileConfig):

    sqlalchemy_binds = {}
    SQLALCHEMY_BINDS = {}
    a = 10

    class Meta:
        file_env = 'Aot'
        file_path = r'C:\Users\cxiong\Desktop\my\silas\local\migration.yaml'
        file_type = FileType.yaml


config = MyFileConfig()
print(config.g)
