import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import typing 
from typing import List, Dict, Any, Tuple
import io
import inspect

 # Helpers
class ArtemisHelper:
    def assert_input_is_type(arg, type):
        if not isinstance(arg, type):
            raise Exception('[Artemis] ' + inspect.stack()[2][3] + ': arg must be of type ' + str(type))

    def matplotlib_plot_to_str():
        plot_bytes = ArtemisHelper.matplotlib_plot_to_bytes()
        return ArtemisHelper.b64_encode_bytes(plot_bytes)

    def b64_encode_bytes(data):
        return "data:image/png;base64," + base64.b64encode(data).decode('utf-8')

    def load_image(path):
        try:
            with open(path, "rb") as image_file:
                b64Encoding = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                return b64Encoding
        except Exception as e:
            print('[Artemis] Exception: Unable to load image')
            print('[Artemis] ' + str(e))

    def load_gif(path):
        try:
            with open(path, "rb") as image_file:
                b64Encoding = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                return b64Encoding
        except Exception as e:
            print('[Artemis] Exception: Unable to load image')
            print('[Artemis] ' + str(e))

    def matplotlib_plot_to_bytes():
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        return buffer.read()
        
    def matplotlib_fig_to_bytes(fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        return buffer.read()
