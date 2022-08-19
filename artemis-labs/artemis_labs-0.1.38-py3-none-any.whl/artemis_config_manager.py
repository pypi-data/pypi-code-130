import typing 

class ArtemisConfigManager:
    
    functions = {}

    def register_function(function: typing.Callable, name: str):
        ArtemisConfigManager.functions[name] = function
    
    def get_function(name: str):
        return ArtemisConfigManager.functions[name]
