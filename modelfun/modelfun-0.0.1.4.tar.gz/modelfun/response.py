class ModelfunObject():
    def __repr__(self) -> str:
        contents = ''
        exclude_list = ['iterator']

        for k in self.__dict__.keys():
            if k not in exclude_list:
                contents += f'\t{k}: {self.__dict__[k]}\n'

        output = f'modelfun.{type(self).__name__} {{\n{contents}}}'
        return output
