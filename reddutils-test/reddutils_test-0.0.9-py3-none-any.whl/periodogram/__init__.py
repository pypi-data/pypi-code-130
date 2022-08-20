# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 0.0.1
# date 18 aug 2022

# dependencies
import numpy as np
import pandas as pd
from scipy.signal import lombscargle, get_window
from astropy.timeseries import LombScargle as lomb_scargle

from gatspy.periodic import LombScargle
from gatspy.periodic import LombScargleFast
import matplotlib.pyplot as pl
from tabulate import tabulate

import ipywidgets
from ipywidgets import interactive, interact, HBox, VBox

from IPython.display import display

# body

method_dict = {'Scipy':0, 'AstroML':1, 'Gatspy LS':2, 'Gatspy LSF':3}

class LSP:
    def __init__(self, data, headers=['Time', 'RV', 'RVe']):
        if type(data) == np.ndarray:
            self.data = pd.DataFrame(data, columns = ['Time','RV','RVe'])
        if type(data) == pd.DataFrame:
            self.data = data

        self.headers=headers
        self.keys = self.data.columns

        # STYLES
        self.style_list = ['default', 'classic'] + sorted(
                        style for style in pl.style.available
                        if style != 'classic' and
                        style != 'fast' and not style.startswith('_'))

        self.xinit = 'Time'
        self.yinit = 'RV'
        self.rinit = 'RVe'

        ##############
        #self.t = np.ascontiguousarray(x)
        #self.mag = np.ascontiguousarray(y)
        #self.dmag = np.ascontiguousarray(yerr)

        self.tab_header = ['Rank', 'Period', 'Power']
        ###
        self.out = ipywidgets.Output()
        self.out_text = ipywidgets.Output()
        pass


    def getExtremePoints(self, data, typeOfExtreme = None):
        #data = np.array([self.t, self.mag])
        mp = self.maxpoints_textbox.value

        a = np.diff(data)
        asign = np.sign(a)
        signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
        idx = np.where(signchange == 1)[0]

        if typeOfExtreme == 'max' and data[idx[0]] < data[idx[1]]:
            idx = idx[1:][::2]

        elif typeOfExtreme == 'min' and data[idx[0]] > data[idx[1]]:
            idx = idx[1:][::2]

        elif typeOfExtreme is not None:
            idx = idx[::2]

        if 0 in idx:
            idx = np.delete(idx, 0)
        if (len(data) - 1) in idx:
            idx = np.delete(idx, len(data)-1)

        idx = idx[np.argsort(data[idx])]
        if mp is not None:
            idx = idx[-mp:]
            if len(idx) < mp:
                return (np.arange(mp) + 1) * (len(data)//(mp + 1))
        return idx


    def deploy_lsp(self):
        pl.close('all')
        # data
        x = self.xinit
        y = self.yaxis.value
        yerr = self.rinit

        # other params
        Nfreq = self.nfreq.value
        min_per = self.permin.value
        max_per = self.permax.value
        periods = np.linspace(min_per, max_per, Nfreq)
        ang_freqs = 2 * np.pi / periods

        # mark how many
        maxpoints = self.maxpoints_textbox.value
        ide = np.arange(maxpoints)+1

        method = method_dict[self.method_drop.value]
        # PLOT
        TITLE = self.title_textbox.value

        xlog = self.xlog_button.value
        ylog = self.ylog_button.value

        pl.style.use(self.style_drop.value)
        #######################################################
        t = self.data[x].values
        mag = self.data[y].values
        dmag = self.data[yerr].values

        t = np.ascontiguousarray(t)
        mag = np.ascontiguousarray(mag)
        dmag = np.ascontiguousarray(dmag)

        for i in range(1):
            if method==0:
                power = lombscargle(t, mag - np.mean(mag), ang_freqs)
                N = len(t)
                power *= 2 / (N * np.std(mag) ** 2)
                periods = periods

            if method==1:
                periods = periods
                power = lomb_scargle(t, mag, dmag).power(ang_freqs)

            if method==2:
                periods = periods
                model = LombScargle(fit_offset=True).fit(t, mag, dmag)
                power = model.score(periods)

            if method==3:
                fmin = 1. / periods.max()
                fmax = 1. / periods.min()
                N = Nfreq
                df = (fmax - fmin) / Nfreq

                model = LombScargleFast().fit(t, mag, dmag)
                periods, power = model.periodogram_auto(nyquist_factor=200)

                freqs = fmin + df * np.arange(N)

        #pl.savefig('periodogram.png')
        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        pl.title(TITLE, fontsize=16)

        idx = self.getExtremePoints(power, typeOfExtreme='max')
        #idx = idx[-2:]

        pl.plot(periods, power, 'k-')
        # fap line
        ax.annotate('0.1% significance level', (3, 0.13))
        pl.plot(periods, np.ones_like(periods)*0.12, 'k--')
        pl.scatter(periods[idx], power[idx], s= 40, c = 'red')

        for i in idx:
            ax.annotate(f' Max = {np.round(periods[i], 2)}', (periods[i]+10, power[i]))


        ax.set(xlabel='Period (days)', ylabel='Lomb-Scargle Power', xlim=[min(periods), max(periods)])
        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        tabable = np.array([periods[idx][::-1], power[idx][::-1]])


        taball = np.vstack([ide, tabable])
        self.display_text = tabulate(taball.T, headers=self.tab_header)

        #return taball.T
        pass


    def set_buttons(self):
        # TAB 1
        if True:
            self.upload_file = ipywidgets.FileUpload(
                        accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
                        multiple=False  # True to accept multiple files upload else False
                        )

            self.yaxis = ipywidgets.Dropdown(options=self.keys,
                    value=self.yinit, description='Column:',
                    disabled=False)

            self.maxpoints_textbox = ipywidgets.IntText(value=3, description='Maxpoints', disabled=False)

            self.method_drop = ipywidgets.Dropdown(options=method_dict.keys(),
                    value='Scipy', description='Method:',
                    disabled=False)

            self.button = ipywidgets.Button(description='Refresh')

            self.nfreq = ipywidgets.IntText(value=10000, description='Frequencies',disabled=False)

            self.permin = ipywidgets.FloatText(value=1, description='Period min.:',disabled=False)
            self.permax = ipywidgets.FloatText(value=10000, description='Period max.:',disabled=False)

        # TAB 2
        if True:
            self.title_textbox = ipywidgets.Text(
                value=self.method_drop.value,
                description='Title: ')

                # figsize option
            self.hsize_slider = ipywidgets.IntSlider(
                value=8, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=4, min=2, max=20,
                description='Plot vsize:')

            self.xlog_button = ipywidgets.Checkbox(
                        value=True, description='x log',
                        disabled=False)

            self.ylog_button = ipywidgets.Checkbox(
                    value=False, description='y log')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style:',
                disabled=False)
        ##############################
        #TAB 3
        ##############################
        #TAB 4
        if True:
            self.plot_save_button = ipywidgets.Button(
                    description='Save plot')

            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                                value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                    value='current_plot',
                    description='File Name')
        pass


    def set_methods(self):
        @self.button.on_click
        def plot_on_click(b):
            self.out.clear_output(wait=True)
            self.out_text.clear_output(wait=True)
            with self.out:
                self.deploy_lsp()
                pl.show()
            with self.out_text:
                print(self.display_text)

        @self.plot_save_button.on_click
        def save_plot_on_click(b):
            self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)


        def on_value_change(change):
            with open('input.temp', 'w+b') as file:
                file.write(self.upload_file.data[0])
            try:
                data = np.loadtxt('input.temp')
                self.data = pd.DataFrame(data, columns=self.headers)
            except ValueError:
                self.data = pd.read_csv('input.temp')
            except:
                print('FAILED TO UNPACK THE FILE. SORRY :(')
            self.keys = self.data.columns
        self.upload_file.observe(on_value_change, names='value')


    def set_tabs(self):
        t1r0 = [self.upload_file]
        t1r1 = [self.yaxis, self.maxpoints_textbox]
        t1r2 = [self.nfreq, self.permin, self.permax]

        tab1 = [t1r0, t1r1, t1r2]

        t2r1 = [self.title_textbox, self.hsize_slider, self.vsize_slider]
        t2r2 = [self.xlog_button, self.ylog_button]
        t2r3 = [self.style_drop]
        tab2 = [t2r1, t2r2, t2r3]

        t3r1 = [self.method_drop]
        tab3 = [t3r1]

        t4_row1 = [self.savefile_name, self.plot_fmt]
        t4_row2 = [self.plot_save_button]
        tab4 = [t4_row1, t4_row2]


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
        self.set_methods()
        self.set_tabs()
        pass


    def display(self):
        return VBox(children=[self.tab, self.button, HBox(children=[self.out, self.out_text])])





'''
color_picker = widgets.ColorPicker(
    concise=True,
    description='Background color:',
    value='#efefef',
)
color_picker
'''











#
