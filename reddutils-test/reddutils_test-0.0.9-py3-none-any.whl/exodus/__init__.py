# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 0.0.1
# date august 2022

import numpy as np
import pandas as pd
from PyAstronomy import pyasl
from tabulate import tabulate
import os

import matplotlib.pyplot as pl
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import ipywidgets
from ipywidgets import interactive, interact, TwoByTwoLayout, HBox, VBox

from IPython.display import display


# TABLES
reads = ['Planet Name', 'Host Name', 'Number of Stars', 'Number of Planets',
         'Discovery Method', 'Discovery Year', 'Controversial Flag', 'Orbital Period [days]', 'Orbit Semi-Major Axis [au])',
         'Planet Radius [Earth Radius]', 'Planet Radius [Jupiter Radius]', 'Planet Mass or Mass*sin(i) [Earth Mass]',
         'Planet Mass or Mass*sin(i) [Jupiter Mass]', 'Planet Mass or Mass*sin(i) Provenance', 'Eccentricity', 'Insolation Flux [Earth Flux]',
         'Equilibrium Temperature [K]', 'Data show Transit Timing Variations', 'Spectral Type', 'Stellar Effective Temperature [K]',
         'Stellar Radius [Solar Radius]', 'Stellar Mass [Solar mass]', 'Stellar Metallicity [dex]', 'Stellar Metallicity Ratio',
         'Stellar Surface Gravity [log10(cm/s**2)]','RA [sexagesimal]','RA [deg]','Dec [sexagesimal]','Dec [deg]',
         'Distance [pc]', 'V (Johnson) Magnitude', 'Ks (2MASS) Magnitude', 'Gaia Magnitude']

good_reads = ['Number of Stars',
              'Number of Planets',
              'Discovery Method',
              'Discovery Year',
              'Orbital Period [days]',
              'Orbit Semi-Major Axis [au])',
              'Planet Radius [Earth Radius]',
              'Planet Radius [Jupiter Radius]',
              'Planet Mass or Mass*sin(i) [Earth Mass]',
              'Planet Mass or Mass*sin(i) [Jupiter Mass]',
              'Eccentricity',
              'Insolation Flux [Earth Flux]',
              'Equilibrium Temperature [K]',
              'Data show Transit Timing Variations',
              'Stellar Effective Temperature [K]',
              'Stellar Radius [Solar Radius]',
              'Stellar Mass [Solar mass]',
              'Stellar Metallicity [dex]',
              'Stellar Surface Gravity [log10(cm/s**2)]',
              'RA [deg]',
              'Dec [deg]',
              'Distance [pc]',
              'V (Johnson) Magnitude',
              'Ks (2MASS) Magnitude',
              'Gaia Magnitude']

fav_met = [False, False, True, True, True, False, False, False, True, True, True]

good_cols = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22,
            24, 26, 28, 29, 30, 31, 32]

planet_names = ['mercury.png', 'venus.png', 'earth.png', 'mars.png',
                'jupiter.png', 'saturn.png', 'uranus.png', 'neptune.png']

planet_sizes = [0.025, 0.035, 0.03, 0.03, 0.03, 0.03, 0.025, 0.04]


_ROOT = os.path.dirname(__file__)
def get_data(path):
    return os.path.join(_ROOT, 'data', path)


dataloc = get_data('tables/exo_list.csv')
imageloc = get_data('images/')
ssloc = get_data('tables/ss_list.csv')


class NASA_Exoplanet_Archive:
    def __init__(self, data=dataloc):
        self.d = pd.read_csv(data, usecols=good_cols)
        self.keys = self.d.columns

        self.ss = pd.read_csv(ssloc)

        self.readable = {}
        for i in range(len(self.keys)):
            self.readable[self.keys[i]] = good_reads[i]

        self.unreadable = {v: k for k, v in self.readable.items()}
        self.unkeys = list(self.unreadable.keys())

        # SET COLORS
        self.methods = np.unique(self.d['discoverymethod'])

        self.method_colors = {}
        for i in range(len(self.methods)):
            self.method_colors[self.methods[i]] = 'C%i' % i

        # SET STYLES
        self.style_list = ['default', 'classic'] + sorted(
                        style for style in pl.style.available
                        if style != 'classic' and
                        style != 'fast' and not style.startswith('_'))

        self.xinit = 5
        self.yinit = 9

        # SET OUT
        self.out = ipywidgets.Output()
        self.out_h = ipywidgets.Output()

    def plot(self, b=None):
        pl.close('all')
        x_axis, y_axis = [b.value for b in [self.xaxis, self.yaxis]]

        by_method, alpha = [b.value for b in [self.methodbutton, self.alpha_slider]]

        TITLE = self.title_textbox.value
        xlog = self.xlog_button.value
        ylog = self.ylog_button.value

        minmask_x, maxmask_x = self.xlim1_textbox.value, self.xlim2_textbox.value
        minmask_y, maxmask_y = self.ylim1_textbox.value, self.ylim2_textbox.value

        pl.style.use(self.style_drop.value)


        add_ss_planets = self.ss_add_box.value
        ###############
        key1 = self.unreadable[x_axis]
        key2 = self.unreadable[y_axis]

        x, y = self.d[key1], self.d[key2]

        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        Ndat = x.size

        if True:
            lims_mask = (minmask_x<x)&(x<maxmask_x)&(minmask_y<y)&(y<maxmask_y)
            data = self.d[lims_mask]

            x0, y0 = data[key1], data[key2]
            Ndat = x0.size

        if by_method:
            Ndat = 0
            for m in self.methods:
                if self.method_dict[m].value:
                    mask = data['discoverymethod'] == m
                    xx = x0[mask]
                    yy = y0[mask]

                    #ax.plot(xx, yy, 'o', c=self.method_colors[m], label=m, alpha=alpha)
                    ax.scatter(xx, yy, alpha=alpha, facecolors='none',
                                edgecolors=self.method_colors[m], label=m)


                    Ndat += xx.size
                else:
                    pass
        else:
            ax.plot(x0, y0, 'C0o', label = 'Planets', alpha=alpha)


        if add_ss_planets:
            try:
                xs = self.ss[key1]
                ys = self.ss[key2]
                for p in range(len(xs)):
                    imscatter(xs[p], ys[p], imageloc+'%s' % planet_names[p], ax=ax,
                                zoom=planet_sizes[p])
            except:
                pass

        # AXIS
        ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
        ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
        ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
        ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

        ax.set_xlabel(self.readable[x.name], fontsize=22)
        ax.set_ylabel(self.readable[y.name], fontsize=22)

        # TITLE
        ax.set_title(TITLE+' N = %i' % Ndat, fontsize=28)


        # LEGEND
        TFP = {'style':'italic', 'size':'large', 'weight':'semibold'}
        pl.legend(title='Planet Discovery Method', title_fontproperties=TFP)

    def plot_h(self, b=None):
        pl.close('all')
        x_axis = self.xaxis.value

        by_method, alpha = [b.value for b in [self.methodbutton, self.alpha_slider]]

        TITLE = self.title_textbox.value
        ylog = self.ylogh_button.value

        NORM = self.norm_h.value

        bins = self.bins_textbox.value

        minmask_x, maxmask_x = self.xlim1_textbox.value, self.xlim2_textbox.value
        #minmask_y, maxmask_y = self.ylim1_textbox.value, self.ylim2_textbox.value

        pl.style.use(self.style_drop.value)
        #########################################################

        key1 = self.unreadable[x_axis]
        x = self.d[key1]

        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)

        #if xlog:
        #    ax.set_xscale('log')

        if ylog:
            ax.set_yscale('log')

        Ndat = x.size

        if True:
            lims_mask = (minmask_x<x)&(x<maxmask_x)
            data = self.d[lims_mask]

            x0 = data[key1]

        Ndat = 0
        xm = np.array([])
        for m in self.methods:
            if self.method_dict[m].value:
                mask = data['discoverymethod'] == m
                xm = np.append(xm, x0[mask].values)

        Ndat = len(xm)
        n, bins, patches = pl.hist(xm, bins, density=NORM, stacked=NORM, facecolor='green', alpha=0.75,
                               edgecolor='k')



        ax.set_xlabel(self.readable[x.name], fontsize=22)
        if NORM:
            ax.set_ylabel('frequency', fontsize=22)
        else:
            ax.set_ylabel('counts', fontsize=22)

        # TITLE
        ax.set_title(TITLE+' N = %i' % Ndat, fontsize=28)

        pass

    def set_buttons(self):
        if True:
            self.alpha_slider = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

            # axis

            self.xaxis = ipywidgets.Dropdown(options=self.unkeys,
                value=self.unkeys[self.xinit], description='x-axis:',
                disabled=False)


            self.yaxis = ipywidgets.Dropdown(options=self.unkeys,
                value=self.unkeys[self.yinit], description='y-axis:',
                disabled=False)

            self.xlog_button = ipywidgets.ToggleButton(
                value=True, description='x log',
                icon='check')

            self.ylog_button = ipywidgets.ToggleButton(
                value=True, description='y log',
                icon='check')

            self.ss_add_box = ipywidgets.ToggleButton(
                value=False, description='Add SS',
                icon='check')

            self.axis_restore =  ipywidgets.Button(description='Reset axis')
            self.axis_invert =  ipywidgets.Button(description='Invert axis')

            # axis limits
            self.xlim1_textbox = ipywidgets.FloatText(value=min(self.d[self.unreadable[self.xaxis.value]]), description='x Minimum:',disabled=False)
            self.xlim2_textbox = ipywidgets.FloatText(value=max(self.d[self.unreadable[self.xaxis.value]]), description='x Maximum:',disabled=False)

            self.ylim1_textbox = ipywidgets.FloatText(value=min(self.d[self.unreadable[self.yaxis.value]]), description='y Minimum:',disabled=False)
            self.ylim2_textbox = ipywidgets.FloatText(value=max(self.d[self.unreadable[self.yaxis.value]]), description='y Maximum:',disabled=False)

            self.xlims_restore = ipywidgets.Button(description='Reset x range')
            self.ylims_restore = ipywidgets.Button(description='Reset y range')

            # plot
            self.title_textbox = ipywidgets.Text(
                value='Exoplanet Population',
                description='Title: ')

            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                            value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                value='current_plot',
                description='File Name')


            self.button = ipywidgets.Button(
                description='Refresh')
            self.plot_save_button = ipywidgets.Button(
                description='Save plot')
            # figsize option
            self.hsize_slider = ipywidgets.IntSlider(
                value=9, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=6, min=2, max=20,
                description='Plot vsize:')


            # styles
            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style:',
                disabled=False)

            # histogram mode
        if True:
            self.bins_textbox = ipywidgets.IntText(value=60, description='Bins: ', disabled=False)

            self.button_h = ipywidgets.Button(description='Refresh')

            self.norm_h = ipywidgets.Checkbox(value=False,
                        description='Normalise', disabled=False)

            self.ylogh_button = ipywidgets.ToggleButton(
                value=False, description='y log',
                icon='check')

            self.axis_restoreh =  ipywidgets.Button(description='Reset axis')
            # methods
            self.methodbutton = ipywidgets.ToggleButton(
                value=True, description='By Method',
                icon='check')


            self.method_dict = {}
            for i in range(len(self.methods)):
                self.method_dict[self.methods[i]] = ipywidgets.ToggleButton(value=fav_met[i], description=self.methods[i], icon='check')

            self.method_restore = ipywidgets.Button(description='Reset Methods')
            self.method_invert = ipywidgets.Button(description='Invert Methods', button_style='warning')
            self.method_unselect = ipywidgets.Button(description='Unselect all', button_style='danger')

            self.method_restore.style.button_color = 'lightgreen'

            # ALL

            self.all_restore = ipywidgets.Button(description='Restart', button_style='danger')

    def set_methods(self):
        if True:
            # AXIS
            @self.axis_restore.on_click
            def restore_axis(b):
                self.xaxis.value = self.unkeys[self.xinit]
                self.yaxis.value = self.unkeys[self.yinit]
                self.xlog_button.value = True
                self.ylog_button.value = True

            @self.axis_invert.on_click
            def invert_axis(b):
                foo, bar = self.xaxis.value, self.yaxis.value
                self.xaxis.value = bar
                self.yaxis.value = foo

                foo, bar = self.xlog_button.value, self.ylog_button.value
                self.xlog_button.value = bar
                self.ylog_button.value = foo

            # LIMITS
            @self.xlims_restore.on_click
            def restore_xlims(b):
                self.xlim1_textbox.value = min(self.d[self.unreadable[self.xaxis.value]])
                self.xlim2_textbox.value = max(self.d[self.unreadable[self.xaxis.value]])

            @self.ylims_restore.on_click
            def restore_ylims(b):
                self.ylim1_textbox.value = min(self.d[self.unreadable[self.yaxis.value]])
                self.ylim2_textbox.value = max(self.d[self.unreadable[self.yaxis.value]])



            # METHODS
             #method_dict[methods[i]] = ipywidgets.ToggleButton(value=fav_met[i]

            @self.method_restore.on_click
            def restore_methods(b):
                for i in range(len(self.methods)):
                    self.method_dict[self.methods[i]].value = fav_met[i]

            @self.method_invert.on_click
            def invert_methods(b):
                for m in self.methods:
                    foo = self.method_dict[m].value
                    self.method_dict[m].value = not foo

            @self.method_unselect.on_click
            def unselect_methods(b):
                for m in self.methods:
                    if m == 'Radial Velocity':
                        pass
                    else:
                        self.method_dict[m].value = False


            @self.all_restore.on_click
            def restore_all(b):
                self.method_restore.click()
                self.axis_restore.click()
                self.xlims_restore()
                self.ylims_restore()

            @self.button.on_click
            def plot_on_click(b):
                self.out.clear_output(wait=True)
                with self.out:
                    self.plot()
                    pl.show()

            @self.plot_save_button.on_click
            def save_plot_on_click(b):
                self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)

        # HISTOGRAM
        if True:
            @self.axis_restoreh.on_click
            def restore_axish(b):
                self.xaxis.value = self.unkeys[self.xinit]
                self.bins_textbox.value = 60
                self.ylogh_button.value = False
                self.norm_h.value = False

            @self.button_h.on_click
            def plot_on_click(b):
                self.out_h.clear_output(wait=True)
                with self.out_h:
                    self.plot_h()
                    pl.show()
        pass

    def set_tabs(self):
        if True:
            # TABS
            t1_row1 = [self.xaxis, self.yaxis, self.axis_restore, self.axis_invert]
            t1_row2 = [self.xlim1_textbox, self.xlim2_textbox, self.xlims_restore]
            t1_row3 = [self.ylim1_textbox, self.ylim2_textbox, self.ylims_restore]
            t1_row4 = [self.all_restore]
            tab1 = [t1_row1, t1_row2, t1_row3, t1_row4]


            t2_row1 = [self.title_textbox, self.hsize_slider, self.vsize_slider]
            t2_row2 = [self.alpha_slider, self.xlog_button, self.ylog_button, self.methodbutton]
            t2_row3 = [self.style_drop, self.ss_add_box]
            tab2 = [t2_row1, t2_row2, t2_row3]


            t3_row1 = [self.method_dict[m] for m in self.methods[:4]]
            t3_row2 = [self.method_dict[m] for m in self.methods[4:8]]
            t3_row3 = [self.method_dict[m] for m in self.methods[8:11]]
            t3_row4 = [self.method_restore, self.method_invert, self.method_unselect]
            tab3 = [t3_row1, t3_row2, t3_row3, t3_row4]


            t4_row1 = [self.savefile_name, self.plot_fmt]
            t4_row2 = [self.plot_save_button]
            tab4 = [t4_row1, t4_row2]

            tab_names = ['Plot', 'Styling', 'Methods', 'Export']
            tabs = {'tab1':tab1, 'tab2':tab2, 'tab3':tab3, 'tab4':tab4}
            for tab in tabs:
                setattr(self, tab, VBox(children=[HBox(children=row) for row in tabs[tab]]))


            self.tab = ipywidgets.Tab(children=[getattr(self, t) for t in tabs])
            for i in range(len(tab_names)):
                self.tab.set_title(i, tab_names[i])

            ##########
        if True:
            th1_row1 = [self.xaxis, self.bins_textbox, self.norm_h, self.axis_restoreh]
            th1_row2 = [self.xlim1_textbox, self.xlim2_textbox, self.xlims_restore]
            #t1_row3 = [self.ylim1_textbox, self.ylim2_textbox, self.ylims_restore]
            th1_row3 = [self.all_restore]
            tabh1 = [th1_row1, th1_row2, th1_row3]


            th2_row1 = [self.title_textbox, self.hsize_slider, self.vsize_slider]
            th2_row2 = [self.alpha_slider, self.ylogh_button]
            th2_row3 = [self.style_drop]
            tabh2 = [th2_row1, th2_row2, th2_row3]


            th3_row1 = [self.method_dict[m] for m in self.methods[:4]]
            th3_row2 = [self.method_dict[m] for m in self.methods[4:8]]
            th3_row3 = [self.method_dict[m] for m in self.methods[8:11]]
            th3_row4 = [self.method_restore, self.method_invert, self.method_unselect]
            tabh3 = [th3_row1, th3_row2, th3_row3, th3_row4]

            th4_row1 = [self.savefile_name, self.plot_fmt]
            th4_row2 = [self.plot_save_button]
            tabh4 = [th4_row1, th4_row2]

            tabh_names = ['Plot', 'Styling', 'Methods', 'Export']
            tabsh = {'tabh1':tabh1, 'tabh2':tabh2, 'tabh3':tabh3, 'tab4':tabh4}
            for tabh in tabsh:
                setattr(self, tabh, VBox(children=[HBox(children=row) for row in tabsh[tabh]]))


            self.tabh = ipywidgets.Tab(children=[getattr(self, t) for t in tabsh])
            for i in range(len(tabh_names)):
                self.tabh.set_title(i, tabh_names[i])


        pass

    def setup(self):
        self.set_buttons()
        self.set_methods()
        self.set_tabs()
        pass

    def display(self):
        return VBox(children=[self.tab, self.button, self.out])

    def histogram(self):
        return VBox(children=[self.tabh, self.button_h, self.out_h])

    pass




def imscatter(x, y, image, ax=None, zoom=1, fmt=None):
    if ax is None:
        ax = pl.gca()
    try:
        image = pl.imread(image, format=fmt)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists












#
