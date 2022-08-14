#!/usr/bin/python3

# ick, remote during packaging:
from pyfsdb import Fsdb
import matplotlib
import matplotlib.lines

plt = None
dates = None


class MultiKeyGraph(object):

    def __init__(self):
        self.anon_name_hash = {}

    def init_plt(self, interactive):
        if not interactive:
            matplotlib.use('Agg')  # avoids needing an X terminal
            font = {'size': 14}
            matplotlib.rc('font', **font)

        # delay these imports till after Agg
        global plt
        global dates
        import matplotlib.pyplot as plt
        import matplotlib.dates as dates

    def anonymize_name(self, name, pattern="Object %d"):
        if name in self.anon_name_hash:
            return self.anon_name_hash[name]
        newname = pattern % (len(self.anon_name_hash) + 1)
        self.anon_name_hash[name] = newname

    def reformat_large_tick_values(self, tick_val, pos):
        """Turns large tick values (in the billions, millions and thousands)
        such as 4500 into numbers like 4.5K.

        Source: https://dfrieds.com/data-visualizations/how-format-large-tick-values.html
        """
        if tick_val >= 1000000000000:
            val = round(tick_val/1000000000000, 3)
            new_tick_format = '{:}G'.format(val)
        elif tick_val >= 1000000000:
            val = round(tick_val/1000000000, 3)
            new_tick_format = '{:}G'.format(val)
        elif tick_val >= 1000000:
            val = round(tick_val/1000000, 3)
            new_tick_format = '{:}M'.format(val)
        elif tick_val >= 1000:
            val = round(tick_val/1000, 3)
            new_tick_format = '{:}K'.format(val)
        elif tick_val < 1000:
            new_tick_format = round(tick_val, 3)
        else:
            new_tick_format = tick_val

        # make new_tick_format into a string value
        new_tick_format = str(new_tick_format)

        return new_tick_format

    def read_data(self, file_handle, time_column, key_column, columns,
                  limit_keys, out_col_data,
                  anonymize_name_pattern=None):
        """Reads data in an FSDB formatted file_handle, adding the data
        to the out_col_data dictionary."""
        f = Fsdb(file_handle=file_handle)

        time_col = f.get_column_number(time_column)
        key_col = f.get_column_number(key_column)

        column_numbers = []
        column_map = {}
        for column in columns:
            try:
                colnum = f.get_column_number(column)
                column_numbers.append(colnum)
                column_map[colnum] = column
            except Exception:
                print("column '%s' not found in '%s' -- ignoring" %
                      (column, str(f.file_handle)))

        if len(column_numbers) == 0:
            raise ValueError("no valid columns specified")

        for column in columns:
            if column not in out_col_data:
                out_col_data[column] = {}

        for row in f.next_as_array():
            key = row[key_col]

            if limit_keys and key not in limit_keys:
                continue

            # maybe anonymize the printed key in the output
            anonkey = key
            if anonymize_name_pattern:
                anonkey = self.anonymize_name(key, anonymize_name_pattern)

            for column in column_numbers:
                colname = column_map[column]
                if anonkey not in out_col_data[colname]:
                    out_col_data[colname][anonkey] = {}
                    out_col_data[colname][anonkey]['x'] = []
                    out_col_data[colname][anonkey]['y'] = []
                # XXX: filter none
                if len(row) <= column:  # don't assume rows are complete
                    continue
                if row[column] == '':
                    continue
                out_col_data[colname][anonkey]['x'].append(float(row[time_col]))
                out_col_data[colname][anonkey]['y'].append(float(row[column]))

        return list(column_map.keys())

    def plot_it(self, col_data,
                limit_keys=None,
                xlabel="Time", ylabel="Count", title=None, scatter=False,
                anonymize_name_pattern=None, legend_map={}, time_markers=[],
                marker_size=2.0, no_legend=False, legend_outside=False,
                column_map={}, use_dots=False, line_width=3,
                yrange=None, dont_reformat_values=False,
                opacity=1.0, no_dates=False):

        # some of these don't look good, so we sub-select to good ones
        # markers=list(matplotlib.lines.Line2D.markers.keys())
        markers = ['o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's',
                   'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X',
                   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 'None', None, ' ', '']

        # create a figure and NxM subplots
        num_columns = len(col_data.keys())
        fig, axs = plt.subplots(nrows=num_columns, ncols=1, sharex=True)
        if num_columns == 1:
            axs = [axs]

        for n, column in enumerate(col_data.keys()):
            miny =  2**31
            maxy = -2**31
            # axs[n].set_xticks(col_ticks[column]['x'])
            # axs[n].set_yticks(col_ticks[column]['y'])
            axis_title = column
            if column in column_map:
               axis_title = column_map[column] 
            axs[n].set_title(axis_title)
            if not dont_reformat_values:
                axs[n].yaxis.set_major_formatter(self.reformat_large_tick_values)

            for m, key in enumerate(col_data[column]):

                label = key
                if label in legend_map:
                    label = legend_map[label]

                # convert the xaxis data to time data for better label printing
                if no_dates:
                    xdata = col_data[column][key]['x']
                else:
                    xdata = dates.epoch2num(col_data[column][key]['x'])
                    formatter = dates.DateFormatter("%Y/%m/%d\n%H:%M")
                    axs[n].xaxis.set_major_formatter(formatter)

                if use_dots:
                    marker = '.'
                else:
                    marker = markers[m % len(markers)]

                if scatter:
                    axs[n].scatter(xdata, col_data[column][key]['y'],
                                   label=label, marker=marker,
                                   s=marker_size, linewidth=line_width,
                                   alpha=opacity)
                else:
                    axs[n].plot(xdata, col_data[column][key]['y'],
                                label=label, marker=marker,
                                ms=marker_size, linewidth=line_width,
                                alpha=opacity)

                if len(col_data[column][key]['y']) > 0:
                    miny = min(miny, min(col_data[column][key]['y']))
                    maxy = max(maxy, max(col_data[column][key]['y']))

            if time_markers:
                for marker in time_markers:
                    if not no_dates:
                        marker = dates.epoch2num(marker)
                    axs[n].plot([marker, marker],
                                [miny, maxy],
                                alpha=.4, color='black')

            # if there was anything to actually plot... add the legend
            if n == 0:
                if (len(col_data[column]) <= 10 and not no_legend) or \
                   (len(col_data[column]) > 10 and no_legend):
                    if legend_outside:
                        axs[n].legend(bbox_to_anchor=(1.05, 1), loc=2,
                                      borderaxespad=0)
                    else:
                        axs[n].legend(loc='best')

            if yrange:  # allow cycling
                lower = yrange[n % len(yrange)]
                upper = yrange[n % len(yrange) + 1]
                axs[n].set_ylim([lower, upper])
                axs[n].margins(.1, 0)
            elif miny == maxy or maxy-miny < 0.1:
                axs[n].set_ylim([miny - 1, maxy + 1])
                axs[n].margins(.1, 0)
            else:
                axs[n].margins(.1, .1)
                #axs[n].set_ylim(miny, maxy)

 
                
           # axs[n].grid(True)

        # allow the date to rotate
        fig.autofmt_xdate()

        if xlabel:
            plt.xlabel(xlabel)

        if ylabel:
            plt.ylabel(ylabel)

        if title:
            plt.title(title)

#        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)

        # deals with long labels:
        plt.tight_layout()

        fig.set_dpi(150)
        fig.set_size_inches(16, 9)
        return plt

    def graph(self, input_file_handles,
              columns,
              time_column="timestamp",
              key_column="key",
              limit_keys=None,
              title=None,
              anonymize_name_pattern=None,
              legend_map={},
              interactive=False,
              output_file=None,
              xlabel=None,
              ylabel=None,
              scatter=False,
              time_markers=[],
              marker_size=2.0,
              no_legend=False,
              legend_outside=False,
              column_map={},
              use_dots=False,
              line_width=3,
              yrange=None,
              dont_reformat_values=False,
              opacity=1.0,
              no_dates=False):

        self.init_plt(interactive)

        limited_list = None
        if limit_keys:
            limited_list = {}
            for key in limit_keys:
                limited_list[key] = 1

        col_data = {}

        # read in specified files into the col_data dict
        for file_handle in input_file_handles:
            self.read_data(file_handle, time_column, key_column,
                           columns, limited_list, col_data)

        # drop empty plots
        delete_these = []
        for column_name in col_data:
            if len(col_data[column_name]) == 0:
                delete_these.append(column_name)
        for item in delete_these:
            del col_data[item]

        plt = self.plot_it(col_data,
                           limited_list, xlabel=xlabel, ylabel=ylabel,
                           title=title, scatter=scatter,
                           anonymize_name_pattern=anonymize_name_pattern,
                           legend_map=legend_map, time_markers=time_markers,
                           marker_size=marker_size,
                           no_legend=no_legend,
                           legend_outside=legend_outside,
                           column_map=column_map,
                           use_dots=use_dots,
                           line_width=line_width,
                           yrange=yrange,
                           dont_reformat_values=dont_reformat_values,
                           opacity=opacity, no_dates=no_dates)

        if interactive:
            plt.show()
        if output_file:
            plt.savefig(output_file, bbox_inches="tight", pad_inches=0)

        plt.clf()
        plt.cla()
        plt.close()

