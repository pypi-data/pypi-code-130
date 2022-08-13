"""
Here Configuration of your Extension (and maybe your Application) takes place
"""
import os

class BaseConfig:
    ''' This is a extension-based Config which is used as Base '''
    # FAUCET_SOMEKEY = "some value"

class ProductionConfig(BaseConfig):
    ''' This is a extension-based Config for Production '''
    pass
