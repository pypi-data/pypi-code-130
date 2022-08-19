import pkgutil

import alphaui.components as components
import alphaui.inputs as inputs
import alphaui.outputs as outputs
import alphaui.processing_utils
import alphaui.templates
from alphaui.blocks import Blocks, skip, update
from alphaui.components import (
    HTML,
    JSON,
    Audio,
    Button,
    Carousel,
    Chatbot,
    Checkbox,
    Checkboxgroup,
    CheckboxGroup,
    ColorPicker,
    DataFrame,
    Dataframe,
    Dataset,
    Dropdown,
    File,
    Gallery,
    Highlightedtext,
    HighlightedText,
    Image,
    Interpretation,
    Json,
    Label,
    Markdown,
    Model3D,
    Number,
    Plot,
    Radio,
    Slider,
    StatusTracker,
    Textbox,
    TimeSeries,
    Timeseries,
    Variable,
    Video,
    component,
)
from alphaui.examples import Examples
from alphaui.flagging import (
    CSVLogger,
    FlaggingCallback,
    HuggingFaceDatasetSaver,
    SimpleCSVLogger,
)
from alphaui.interface import Interface, TabbedInterface, close_all
from alphaui.ipython_ext import load_ipython_extension
from alphaui.layouts import Box, Column, Group, Row, TabItem, Tabs
from alphaui.mix import Parallel, Series
from alphaui.templates import (
    Files,
    Highlight,
    List,
    Matrix,
    Mic,
    Microphone,
    Numpy,
    Pil,
    PlayableVideo,
    Sketchpad,
    Text,
    TextArea,
    Webcam,
)

current_pkg_version = pkgutil.get_data(__name__, "version.txt").decode("ascii").strip()
__version__ = current_pkg_version
