# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 0.0.1
# date 18 aug 2022

# dependencies
import numpy as np
import pandas as pd
from tabulate import tabulate
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from scipy.stats import kendalltau

import matplotlib.pyplot as pl
from matplotlib import ticker
import matplotlib.gridspec as gridspec

import ipywidgets
from ipywidgets import interactive, interact, HBox, VBox

from IPython.display import display

# body

class correlator:
    def __init__(self, data=None, headers=None):
        # STYLES
        self.style_list = ['default', 'classic'] + sorted(
                        style for style in pl.style.available
                        if style != 'classic' and
                        style != 'fast' and not style.startswith('_'))

        #self.xx, self.yy = D[x_axis].values, D[y_axis].values
        #self.colors = self.data[self.xinit].values
        self.alpha = 0.05 # sensitivity

        self.out = ipywidgets.Output()
        self.out_text = ipywidgets.Output()
        pass

    def plot(self):
        # define values from buttons
        self.x = self.data[self.xaxis.value].values
        self.y = self.data[self.yaxis.value].values
        colors = self.data[self.color_by.value].values


        scatter_size = 100
        ##############
        # TAB 2
        TITLE = self.title_textbox.value
        cm = pl.cm.get_cmap(self.cmap_drop.value)

        xlog = self.xlog_button.value
        ylog = self.ylog_button.value

        pl.style.use(self.style_drop.value)




        ##############
        #PLOT

        #self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)

        sc = ax.scatter(self.x, self.y, c=colors, cmap=cm, ec='k', lw= 0.2,
                        s=scatter_size, alpha=self.alpha_slider.value)

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        ax.set_title(TITLE, fontsize=28)
        ax.set_xlabel(self.xaxis.value, fontsize=22)
        ax.set_ylabel(self.yaxis.value, fontsize=22)

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        pl.minorticks_on()

        #ax = fig.add_axes([0, 0, 1, 1])

        ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
        ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
        ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
        ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

        pl.colorbar(sc)
        pass

    def calc_stats(self):
        # STATS
        funcs = [pearsonr, spearmanr, kendalltau]
        names = ['Pearson', 'Spearman', 'Kendall']
        taball = []
        tab_header = ['Correlation', 'Rank', 'p-value', 'Info']
        try:
            for i in range(3):
                coefx, px = funcs[i](self.x, self.y)
                if px > self.alpha:
                    text = 'Uncorrelated (fail to reject H0) p=%.5f' % px
                else:
                    text = 'Correlated (reject H0) p=%.5f' % px
                taball.append([names[i], coefx, px, text])

            #print(tabulate(taball, headers=tab_header))
        except:
            print('Cant calculate coeficients, figure it out man')
        return tabulate(taball, headers=tab_header)

    def set_data(self, data=None):
        if type(data) == np.ndarray:
            if headers:
                try:
                    self.headers = headers
                    self.data = pd.DataFrame(data, columns=headers)
                except:
                    print('Headers are invalid for data.type ndarray')
                    self.data = pd.DataFrame(data, columns = ['Time','RV','RVe'])
        if type(data) == pd.DataFrame:
            self.data = data

        self.keys = self.data.columns
        self.xinit = self.keys[0]
        self.yinit = self.keys[1]

    def set_buttons(self):
        self.xaxis = ipywidgets.Dropdown(options=self.keys,
                value=self.xinit, description='x-axis:',
                disabled=False)

        self.yaxis = ipywidgets.Dropdown(options=self.keys,
                value=self.yinit, description='y-axis:',
                disabled=False)

        self.color_by = ipywidgets.Dropdown(options=self.keys,
                value=self.xinit, description='Color by:',
                disabled=False)

        # TAB 2
        if True:
            self.title_textbox = ipywidgets.Text(
                value=self.xaxis.value,
                description='Title: ')

                # figsize option
            self.hsize_slider = ipywidgets.IntSlider(
                value=8, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=4, min=2, max=20,
                description='Plot vsize:')

            self.alpha_slider = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

            self.xlog_button = ipywidgets.Checkbox(
                        value=False, description='x log',
                        disabled=False)

            self.ylog_button = ipywidgets.Checkbox(
                    value=False, description='y log')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style:',
                disabled=False)

            self.cmap_drop = ipywidgets.Dropdown(
                options=pl.colormaps(),
                value='winter',
                description='Colormap:',
                disabled=False)

        ######
        self.button = ipywidgets.Button(description='Refresh')
        @self.button.on_click
        def plot_on_click(b):
            self.out.clear_output(wait=True)
            self.out_text.clear_output(wait=True)
            with self.out:
                self.plot()
                pl.show()
            with self.out_text:
                print(self.calc_stats())
        ######
        # TAB 4
        if True:
            self.title_textbox = ipywidgets.Text(
                value='Correlation',
                description='Title: ')

            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                            value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                value='current_plot',
                description='File Name')

            self.plot_save_button = ipywidgets.Button(
                    description='Save plot')
            @self.plot_save_button.on_click
            def save_plot_on_click(b):
                self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)


        pass

    def set_tabs(self):
        tab1_row1 = []
        tab1_row2 = [self.xaxis, self.yaxis, self.color_by]
        #tab1_row3 = [self.button]
        tab1 = [tab1_row1, tab1_row2]

        tab2_row1 = [self.title_textbox, self.hsize_slider, self.vsize_slider]
        tab2_row2 = [self.alpha_slider, self.xlog_button, self.ylog_button]
        tab2_row3 = [self.style_drop, self.cmap_drop]
        tab2 = [tab2_row1, tab2_row2, tab2_row3]

        tab3_row1 = []
        tab3_row2 = []
        tab3_row3 = []
        tab3 = [tab3_row1, tab3_row2, tab3_row3]

        tab4_row1 = [self.savefile_name, self.plot_fmt]
        tab4_row2 = [self.plot_save_button]
        tab4 = [tab4_row1, tab4_row2]

        tabs = {'tab1':tab1, 'tab2':tab2, 'tab3':tab3, 'tab4':tab4}
        tab_names = ['Plot', 'Styling', 'Method', 'Export']
        for tab in tabs:
            setattr(self, tab, VBox(children=[HBox(children=row) for row in tabs[tab]]))

        self.tab = ipywidgets.Tab(children=[getattr(self, t) for t in tabs])
        for i in range(len(tab_names)):
            self.tab.set_title(i, tab_names[i])
        pass

    def setup(self):
        self.set_buttons()
        self.set_tabs()
        pass

    def display(self, data=None):
        self.set_data(data)
        self.setup()
        return VBox(children=[self.tab, self.button, self.out, self.out_text])
    pass






























#
