from unittest.mock import patch 
import pytest 
import matplotlib.pyplot as plt 
from BusinessAnalytics import plot
import pandas as pd
import numpy as np

data = {"Date": pd.date_range(end="31.12.2021", periods=1000),
        "y1": np.random.randint(1,5,1000), 
        "y2": np.random.randint(4,8, 1000), 
        "y3": np.random.randint(12,19, 1000), 
        "y4": np.random.randn(1000),
        "names": np.random.choice(["male", "female"], size=1000)}

df = (pd.DataFrame(data)
     )

def plot_line():
    # Test standard x,y
    plot(x="Date", y="y1", show_legend=False, data=df)
    plot(x="Date", y="y1", show_legend=True, data=df)

    # Test multiple columns for y
    plot(x="Date", y=["y1", "y2"], show_legend=False, data=df)
    plot(x="Date", y=["y1", "y2", "y3"], show_legend=True, data=df)

    # Test hue
    plot(x="Date", y="y1", hue="names", show_legend=False, title="Test", data=df)
    plot(x="Date", y="y1", hue="names", show_legend=True, title="Test", data=df)

@patch("matplotlib.pyplot.show")
def test_line(mock_show):
    plot_line()