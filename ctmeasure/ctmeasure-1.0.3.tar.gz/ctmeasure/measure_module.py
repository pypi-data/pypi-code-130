import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
from numpy import ndarray
# import control_temperature
# import control_magnetic_field


# Calculate the resistance
def conductance(x, a, b):
    return a * x + b


def get_gpib_connection():
    rm = visa.ResourceManager()
    print(rm.list_resources())
    return


def reset_source_meter(source_meter):
    source_meter.apply_voltage()
    source_meter.compliance_current = 10e-5  # set compliance
    source_meter.enable_source()  # switch on the on/off


def plot_iv_result(measured_voltage_result, measured_current_result, measured_scan_points,
                   min_voltage, max_voltage, voltage_index, delay_time_measure, sweep, plot):
    if plot:
        plt.ion()
        plt.clf()
        plt.scatter(measured_voltage_result, measured_current_result, s=5, c='r')
        if not sweep:
            plt.scatter(measured_voltage_result,
                        measured_current_result, s=5, c='r')
        elif voltage_index < int(measured_scan_points / 2):
            plt.scatter(measured_voltage_result,
                        measured_current_result, s=5, c='r')
        else:
            plt.scatter(measured_voltage_result[:int(measured_scan_points / 2)],
                        measured_current_result[:int(measured_scan_points / 2)], s=5, c='r')
            plt.scatter(measured_voltage_result[int(measured_scan_points / 2):],
                        measured_current_result[int(measured_scan_points / 2):], s=5, c='b')
        plt.xlim([min_voltage * 1.1, max_voltage * 1.1])
        plt.xlabel('Voltage(V)', fontsize=14)
        plt.ylabel('Current(A)', fontsize=14)
        plt.show()
        plt.pause(delay_time_measure)
        print(voltage_index)
    if voltage_index == measured_scan_points - 1:
        plt.ioff()
        plt.scatter(measured_voltage_result, measured_current_result, s=5, c='r')
        plt.show()


def measure_iv_result(source_meter, measured_voltage_result, measured_current_result, measured_scan_points,
                      min_voltage, max_voltage, voltage_apply, ramp_voltage, delay_time_goto, delay_time_measure,
                      sweep, plot):
    source_meter.enable_source()
    ramp_steps = int(abs(min_voltage) / abs(ramp_voltage))
    source_meter.ramp_to_voltage(target_voltage=min_voltage, steps=ramp_steps, pause=delay_time_goto)
    for voltage_index, voltage in enumerate(voltage_apply):
        source_meter.source_voltage = voltage
        measured_voltage_result.append(voltage)
        measured_current_result.append(source_meter.current)
        plot_iv_result(measured_voltage_result, measured_current_result, measured_scan_points,
                       min_voltage, max_voltage, voltage_index, delay_time_measure, sweep, plot=plot)
    return measured_voltage_result, measured_current_result


def measure_iv_result_four_point(source_meter, voltage_meter, measured_voltage_result, measured_current_result,
                                 measured_voltage_result_voltage_meter, measured_scan_points,
                                 min_voltage, max_voltage, voltage_apply, ramp_voltage, delay_time_goto,
                                 delay_time_measure, sweep, plot):
    source_meter.enable_source()
    ramp_steps = int(abs(min_voltage) / abs(ramp_voltage))
    source_meter.ramp_to_voltage(target_voltage=min_voltage, steps=ramp_steps, pause=delay_time_goto)
    for voltage_index, voltage in enumerate(voltage_apply):
        source_meter.source_voltage = voltage
        measured_voltage_result.append(voltage)
        measured_current_result.append(source_meter.current)
        measured_voltage_result_voltage_meter.append(voltage_meter.voltage)
        plot_iv_result(measured_voltage_result, measured_current_result, measured_scan_points,
                       min_voltage, max_voltage, voltage_index, delay_time_measure, sweep, plot=plot)
    return measured_voltage_result, measured_current_result, measured_voltage_result_voltage_meter


def measure_iv_result_six_point(source_meter, voltage_meter_1, voltage_meter_2, measured_voltage_result,
                                measured_current_result,
                                measured_voltage_result_voltage_meter_1,
                                measured_voltage_result_voltage_meter_2, measured_scan_points,
                                min_voltage, max_voltage, voltage_apply, ramp_voltage, delay_time_goto,
                                delay_time_measure, sweep, plot):
    source_meter.enable_source()
    ramp_steps = int(abs(min_voltage) / abs(ramp_voltage))
    source_meter.ramp_to_voltage(target_voltage=min_voltage, steps=ramp_steps, pause=delay_time_goto)
    for voltage_index, voltage in enumerate(voltage_apply):
        source_meter.source_voltage = voltage
        measured_voltage_result.append(voltage)
        measured_current_result.append(source_meter.current)
        measured_voltage_result_voltage_meter_1.append(voltage_meter_1.voltage)
        measured_voltage_result_voltage_meter_2.append(voltage_meter_2.voltage)
        plot_iv_result(measured_voltage_result, measured_current_result, measured_scan_points,
                       min_voltage, max_voltage, voltage_index, delay_time_measure, sweep, plot=plot)
    return measured_voltage_result, measured_current_result, measured_voltage_result_voltage_meter_1, \
        measured_voltage_result_voltage_meter_2


class Two_point_method_2400:
    def __init__(self, source_meter):
        self.measured_voltage_result = []
        self.measured_current_result = []
        self.measured_scan_points = 0
        self.source_meter = source_meter
        self.measurement_type = 0

    def measure_iv(self, min_voltage, max_voltage, step_voltage, ramp_voltage,
                   delay_time_goto, delay_time_measure, compliance_current, sweep=False, plot=True):
        voltage_apply = np.arange(min_voltage, max_voltage+step_voltage, step_voltage)
        voltage_apply_back = np.arange(max_voltage, min_voltage-step_voltage, -step_voltage)
        voltage_apply_fb = np.concatenate((voltage_apply, voltage_apply_back), axis=0)

        self.source_meter.reset()
        self.measurement_type = 1
        self.measured_scan_points = len(voltage_apply)
        self.source_meter.apply_voltage()
        self.source_meter.measure_current()
        self.source_meter.compliance_current = compliance_current

        if sweep:
            voltage_apply = voltage_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        measure_iv_result(self.source_meter, self.measured_voltage_result, self.measured_current_result,
                          self.measured_scan_points, min_voltage, max_voltage, voltage_apply, ramp_voltage,
                          delay_time_goto, delay_time_measure, sweep, plot=plot)

        ramp_steps = int(abs(self.measured_voltage_result[-1]) / abs(ramp_voltage))
        self.source_meter.ramp_to_voltage(target_voltage=0, steps=ramp_steps, pause=delay_time_goto)
        self.source_meter.reset()

    def measure_vi(self, min_current, max_current, step_current, delay_time_goto, delay_time_measure,
                   compliance_voltage, sweep=False):
        current_apply = np.arange(min_current, max_current, step_current)
        current_apply_back = np.arange(max_current, min_current, step_current)
        current_apply_fb = np.concatenate((current_apply, current_apply_back), axis=0)

        self.source_meter.reset()
        self.measurement_type = 2
        self.measured_scan_points = len(current_apply)
        self.source_meter.apply_current()
        self.source_meter.measure_voltage()
        self.source_meter.compliance_voltage = compliance_voltage  # 2.5

        if sweep:
            current_apply = current_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        plt.ion()
        self.source_meter.enable_source()
        self.source_meter.ramp_to_current(target_current=min_current, steps=100, pause=delay_time_goto)
        for current_index, current in enumerate(current_apply):
            self.source_meter.source_current = current
            self.measured_current_result.append(current)
            self.measured_voltage_result.append(self.source_meter.voltage)
            plt.clf()
            plt.scatter(self.measured_current_result, self.measured_voltage_result, s=5, c='r')
            if not sweep:
                plt.scatter(self.measured_current_result,
                            self.measured_voltage_result, s=5, c='r')
            elif current_index < int(self.measured_scan_points / 2):
                plt.scatter(self.measured_current_result,
                            self.measured_voltage_result, s=5, c='r')
            else:
                plt.scatter(self.measured_current_result[:current_index],
                            self.measured_voltage_result[:current_index], s=5, c='r')
                plt.scatter(self.measured_current_result[int(self.measured_scan_points / 2):],
                            self.measured_voltage_result[int(self.measured_scan_points / 2):], s=5, c='b')
            plt.xlim([min_current * 1.1, max_current * 1.1])
            plt.xlabel('Current(A)', fontsize=14)
            plt.ylabel('Voltage(V)', fontsize=14)
            plt.show()
            plt.pause(delay_time_measure)
        plt.ioff()
        plt.show()
        # self.source_meter.ramp_to_current(target_current=0, steps=100, pause=self.delay_time_goto)
        # self.source_meter.reset()

    def save(self, pathria, file_name):  # Do you hate statistic mechanics?
        folder_path = pathria
        # save data to txt
        if self.measurement_type == 1:
            data: ndarray = np.concatenate((np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                            np.reshape(self.measured_current_result, (self.measured_scan_points, 1))),
                                           axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Voltage Current\nV I", comments='')
            print('Measurement data saved!')

        elif self.measurement_type == 2:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Voltage Current\nV I", comments='')
            print('Measurement data saved!')

        else:
            print('There is no data to save.')


class Four_point_method_2400_2000:
    def __init__(self, source_meter, voltage_meter):
        self.measured_voltage_result = []
        self.measured_current_result = []
        self.measured_voltage_result_2000 = []
        self.measured_current_result_2000 = []
        self.measured_scan_points = 0
        self.source_meter = source_meter
        self.voltage_meter = voltage_meter
        self.measurement_type = 0

    def measure_iv(self, min_voltage, max_voltage, step_voltage, ramp_voltage,
                   delay_time_goto, delay_time_measure, compliance_current, sweep=False, plot=True, keep=False):
        voltage_apply = np.arange(min_voltage, max_voltage+step_voltage, step_voltage)
        voltage_apply_back = np.arange(max_voltage, min_voltage-step_voltage, -step_voltage)
        voltage_apply_fb = np.concatenate((voltage_apply, voltage_apply_back), axis=0)

        self.source_meter.reset()
        self.voltage_meter.reset()
        self.measurement_type = 1
        self.measured_scan_points = len(voltage_apply)
        self.source_meter.apply_voltage()
        self.source_meter.measure_current()
        self.source_meter.compliance_current = compliance_current
        self.voltage_meter.measure_voltage()

        if sweep:
            voltage_apply = voltage_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        measure_iv_result_four_point(self.source_meter, self.voltage_meter, self.measured_voltage_result
                                     , self.measured_current_result, self.measured_voltage_result_2000,
                                     self.measured_scan_points, min_voltage, max_voltage, voltage_apply, ramp_voltage,
                                     delay_time_goto, delay_time_measure, sweep, plot=plot)

        ramp_steps = int(abs(self.measured_voltage_result[-1]) / abs(ramp_voltage))
        self.source_meter.ramp_to_voltage(target_voltage=0, steps=ramp_steps, pause=delay_time_goto)
        self.source_meter.reset()

    def save(self, pathria, file_name):  # Do you hate statistic mechanics?
        folder_path = pathria
        # save data to txt
        if self.measurement_type == 1:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result_2000, (len(self.measured_voltage_result_2000), 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Current Voltage Voltage\nI V V\nsource_current source_voltage meter_voltage"
                       , comments='')
            print('Measurement data saved!')

        elif self.measurement_type == 2:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result_2000, (len(self.measured_voltage_result_2000), 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Current   Voltage\nI V V\nsource_current source_voltage meter_voltage"
                       , comments='')
            print('Measurement data saved!')

        else:
            print('There is no data to save.')


class Six_point_method_2400_2000_2000:
    def __init__(self, source_meter, voltage_meter_1, voltage_meter_2):
        self.measured_voltage_result = []
        self.measured_current_result = []
        self.measured_voltage_result_2000_1 = []
        self.measured_current_result_2000_1 = []
        self.measured_voltage_result_2000_2 = []
        self.measured_current_result_2000_2 = []
        self.measured_scan_points = 0
        self.source_meter = source_meter
        self.voltage_meter_1 = voltage_meter_1
        self.voltage_meter_2 = voltage_meter_2
        self.measurement_type = 0

    def measure_iv(self, min_voltage, max_voltage, step_voltage, ramp_voltage,
                   delay_time_goto, delay_time_measure, compliance_current, sweep=False, plot=True, keep=False):
        voltage_apply = np.arange(min_voltage, max_voltage+step_voltage, step_voltage)
        voltage_apply_back = np.arange(max_voltage, min_voltage-step_voltage, -step_voltage)
        voltage_apply_fb = np.concatenate((voltage_apply, voltage_apply_back), axis=0)

        self.source_meter.reset()
        self.voltage_meter_1.reset()
        self.voltage_meter_2.reset()
        self.measurement_type = 1
        self.measured_scan_points = len(voltage_apply)
        self.source_meter.apply_voltage()
        self.source_meter.measure_current()
        self.source_meter.compliance_current = compliance_current
        self.voltage_meter_1.measure_voltage()
        self.voltage_meter_2.measure_voltage()

        if sweep:
            voltage_apply = voltage_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        measure_iv_result_six_point(self.source_meter, self.voltage_meter_1, self.voltage_meter_2
                                    , self.measured_voltage_result, self.measured_current_result
                                    , self.measured_voltage_result_2000_1, self.measured_voltage_result_2000_2
                                    , self.measured_scan_points, min_voltage, max_voltage, voltage_apply
                                    , ramp_voltage, delay_time_goto, delay_time_measure, sweep, plot=plot)

        ramp_steps = int(abs(self.measured_voltage_result[-1]) / abs(ramp_voltage))
        self.source_meter.ramp_to_voltage(target_voltage=0, steps=ramp_steps, pause=delay_time_goto)
        self.source_meter.reset()

    def save(self, pathria, file_name):  # Do you hate statistic mechanics?
        folder_path = pathria
        # save data to txt
        if self.measurement_type == 1:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result_2000_1, (len(self.mㄋeasured_voltage_result_2000_1), 1)),
                                   np.reshape(self.measured_voltage_result_2000_2, (len(self.measured_voltage_result_2000_2), 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Current Voltage Voltage Voltage\nI V V V\nsource_current source_voltage meter1_voltage meter2_voltage"
                       , comments='')
            print('Measurement data saved!')

        elif self.measurement_type == 2:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result_2000_1, (len(self.measured_voltage_result_2000_1), 1)),
                                   np.reshape(self.measured_voltage_result_2000_2, (len(self.measured_voltage_result_2000_2), 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header="Current Voltage Voltage Voltage\nI V V V\nsource_current source_voltage meter1_voltage meter2_voltage"
                       , comments='')
            print('Measurement data saved!')

        else:
            print('There is no data to save.')


class Two_point_method_2635B:
    def __init__(self, source_meter):
        self.delay_time_goto = 0.05
        self.delay_time_measure = 0.05
        self.measured_voltage_result = []
        self.measured_current_result = []
        self.measured_scan_points = 0
        self.source_meter = source_meter
        self.measurement_type = 0

    def measure_iv(self, min_voltage, max_voltage, step_voltage, sweep=False):
        voltage_apply = np.arange(min_voltage, max_voltage, step_voltage)
        voltage_apply_back = np.arange(max_voltage, min_voltage, step_voltage)
        voltage_apply_fb = np.concatenate((voltage_apply, voltage_apply_back), axis=0)

        self.source_meter.reset()
        self.measurement_type = 1
        self.measured_scan_points = len(voltage_apply)
        self.source_meter.compliance_current = 10e-4

        if sweep:
            voltage_apply = voltage_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        # plt.ion()
        # self.source_meter.enable_source()
        self.source_meter.voltage_sweep_single_smu(smu=self.source_meter.smua, smu_sweeplist=np.arange(0, 1, 0.01),
                                                   t_int=0.1, delay=0.5, pulsed=False)

        for voltage_index, voltage in enumerate(voltage_apply):
            self.source_meter.apply_voltage(self.source_meter.smua, voltage)
            self.measured_voltage_result.append(voltage)
            self.measured_current_result.append(self.source_meter.smua.measure.i())
            plt.clf()
            plt.scatter(self.measured_voltage_result, self.measured_current_result, s=5, c='r')
            if not sweep:
                plt.scatter(self.measured_voltage_result,
                            self.measured_current_result, s=5, c='r')
            elif voltage_index < int(self.measured_scan_points / 2):
                plt.scatter(self.measured_voltage_result,
                            self.measured_current_result, s=5, c='r')
            else:
                plt.scatter(self.measured_voltage_result[:voltage_index],
                            self.measured_current_result[:voltage_index], s=5, c='r')
                plt.scatter(self.measured_voltage_result[int(self.measured_scan_points / 2):],
                            self.measured_current_result[int(self.measured_scan_points / 2):], s=5, c='b')
            plt.xlim([min_voltage * 1.1, max_voltage * 1.1])
            plt.xlabel('Voltage(V)', fontsize=14)
            plt.ylabel('Current(A)', fontsize=14)
            plt.show()
            plt.pause(self.delay_time_measure)
        plt.ioff()
        plt.scatter(self.measured_voltage_result, self.measured_current_result, s=5, c='r')
        plt.show()
        self.source_meter.ramp_to_voltage(target_volt=0, delay=self.delay_time_goto, step_size=5e-3)
        self.source_meter.reset()

    def measure_vi(self, min_current, max_current, step_current, sweep=False):
        current_apply = np.arange(min_current, max_current, step_current)
        current_apply_back = np.arange(max_current, min_current, step_current)
        current_apply_fb = np.concatenate((current_apply, current_apply_back), axis=0)

        self.source_meter.reset()
        self.measurement_type = 2
        self.measured_scan_points = len(current_apply)
        self.source_meter.apply_current()
        self.source_meter.measure_voltage()
        self.source_meter.compliance_voltage = 2.5

        if sweep:
            current_apply = current_apply_fb
            self.measured_scan_points *= 2
        else:
            pass

        plt.ion()
        self.source_meter.enable_source()
        self.source_meter.ramp_to_current(target_current=min_current, steps=100, pause=self.delay_time_goto)
        for current_index, current in enumerate(current_apply):
            self.source_meter.source_current = current
            self.measured_current_result.append(current)
            self.measured_voltage_result.append(self.source_meter.voltage)
            plt.clf()
            plt.scatter(self.measured_current_result, self.measured_voltage_result, s=5, c='r')
            if not sweep:
                plt.scatter(self.measured_current_result,
                            self.measured_voltage_result, s=5, c='r')
            elif current_index < int(self.measured_scan_points / 2):
                plt.scatter(self.measured_current_result,
                            self.measured_voltage_result, s=5, c='r')
            else:
                plt.scatter(self.measured_current_result[:current_index],
                            self.measured_voltage_result[:current_index], s=5, c='r')
                plt.scatter(self.measured_current_result[int(self.measured_scan_points / 2):],
                            self.measured_voltage_result[int(self.measured_scan_points / 2):], s=5, c='b')
            plt.xlim([min_current * 1.1, max_current * 1.1])
            plt.xlabel('Current(A)', fontsize=14)
            plt.ylabel('Voltage(V)', fontsize=14)
            plt.show()
            plt.pause(self.delay_time_measure)
        plt.ioff()
        plt.show()
        self.source_meter.ramp_to_current(target_current=0, steps=100, pause=self.delay_time_goto)
        self.source_meter.reset()

    def save(self, pathria, file_name):  # Do you hate statistic mechanics?
        folder_path = pathria
        # save data to txt
        if self.measurement_type == 1:
            data = np.concatenate((np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_current_result, (self.measured_scan_points, 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header='V(V) I(A)', comments='')

        elif self.measurement_type == 2:
            data = np.concatenate((np.reshape(self.measured_current_result, (self.measured_scan_points, 1)),
                                   np.reshape(self.measured_voltage_result, (self.measured_scan_points, 1))), axis=1)
            date = time.asctime(time.localtime(time.time()))
            date = date.replace(':', '_')
            np.savetxt("%s%s_%s.txt" % (folder_path, file_name, date), data, fmt="%.3e"
                       , header='I(A) V(V)', comments='')

        else:
            print('There is no data to save.')


