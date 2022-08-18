from msilib.schema import Condition
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import typing 
from typing import List, Dict, Any, Tuple
import io
import inspect
from enum import Enum

# Enum class
class ArtemisType(Enum):
    MATPLOTLIB_PLOT = 1
    MATPLOTLIB_FIGURE = 2
    LIST = 3
    DICT = 4
    NUMPY_ARRAY = 5


 # Helpers
class ArtemisHelper:

    # ================================================================
    # General Functions
    # ================================================================
    def convert(arg, from_type : ArtemisType, to_type : ArtemisType):
        if from_type == ArtemisType.LIST and to_type == ArtemisType.NUMPY_ARRAY:
            return np.array(arg)
        elif from_type == ArtemisType.NUMPY_ARRAY and to_type == ArtemisType.LIST:
            return arg.tolist()
        return arg

    def convert_if(arg, from_type : ArtemisType, to_type : ArtemisType):
        if from_type == ArtemisType.LIST and to_type == ArtemisType.NUMPY_ARRAY and isinstance(arg, list):
            return np.array(arg)
        elif from_type == ArtemisType.NUMPY_ARRAY and to_type == ArtemisType.LIST and isinstance(arg, np.ndarray):
            return arg.tolist()
        return arg

    def assert_true(Condition):
        if not Condition:
            raise Exception('[Artemis] ' + inspect.stack()[2][3] + ': Condition is false')

    def assert_input_is_type(arg, type):
        if not isinstance(arg, type):
            raise Exception('[Artemis] ' + inspect.stack()[2][3] + ': arg must be of type ' + str(type))

    def serialize(data, data_type : ArtemisType) -> str:
        if data_type == ArtemisType.MATPLOTLIB_PLOT:
            return ('graph', ArtemisHelper.__matplotlib_plot_to_str())
        elif data_type == ArtemisType.MATPLOTLIB_FIGURE:
            return ('graph', ArtemisHelper.__b64_encode_bytes(ArtemisHelper.__matplotlib_fig_to_bytes(data)))
        else:
            raise Exception('[Artemis] ' + inspect.stack()[2][3] + ': data_type must be one of the following: ' + str(ArtemisType))

    # ================================================================
    # Serialize Functions
    # ================================================================

    def __matplotlib_plot_to_str():
        plot_bytes = ArtemisHelper.__matplotlib_plot_to_bytes()
        return ArtemisHelper.__b64_encode_bytes(plot_bytes)

    def __matplotlib_plot_to_bytes():
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        return buffer.read()
        
    def __matplotlib_fig_to_bytes(fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        return buffer.read()

    # ================================================================
    # Serialize Functions
    # ================================================================
    def __b64_encode_bytes(data):
        return "data:image/png;base64," + base64.b64encode(data).decode('utf-8')


    # ================================================================
    # Image Functions
    # ================================================================
    def __load_image(path):
        try:
            with open(path, "rb") as image_file:
                b64Encoding = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                return b64Encoding
        except Exception as e:
            print('[Artemis] Exception: Unable to load image')
            print('[Artemis] ' + str(e))

    def __load_gif(path):
        try:
            with open(path, "rb") as image_file:
                b64Encoding = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                return b64Encoding
        except Exception as e:
            print('[Artemis] Exception: Unable to load image')
            print('[Artemis] ' + str(e))