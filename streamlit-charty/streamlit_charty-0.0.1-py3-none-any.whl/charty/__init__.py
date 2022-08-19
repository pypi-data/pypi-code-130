import os
import streamlit.components.v1 as components


MINIMAL_EXAMPLE_DATA = {
  "type": 'line',
  "data": {
    "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "y0": [-20, 0, 20, 23, 25, 28, 40, 50, 33, 23, 14, 3, 15, 16, 18, 20, 34, 44, 30, 31, 43, 22, 15, 27, 23]
  },
  "colors": {
    "y0": '#5FB641',
  },
  "names": {
    "y0": 'Temperature, C°'
  },
  "startX": 1,
  "endX": 25,
  "xAxisStep": 2,
#   showPreview: false,
#   showRangeText: false,
  "showLegendTitle": False
}

_RELEASE = False


if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_charty",
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_charty", path=build_dir)



def streamlit_charty(key=None,opt=MINIMAL_EXAMPLE_DATA):
    component_value = _component_func(key=key, opt=opt,default=0)
    return component_value


if not _RELEASE:
    import streamlit as st
    st.subheader("Charty Test")
    streamlit_charty("World",opt=MINIMAL_EXAMPLE_DATA)
