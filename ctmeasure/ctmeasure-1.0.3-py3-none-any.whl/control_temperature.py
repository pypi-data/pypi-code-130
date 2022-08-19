from qcodes.instrument_drivers.oxford.triton import Triton
import time
from statistics import mean, variance


class Temperature_controller(Triton):
    def __init__(self):
        super(Temperature_controller, self).__init__(name="self_200", address="10.101.2.24", port=33576)
        self.T_channels = {"T1": self.T1, "T2": self.T2, "T3": self.T3, "T4": self.T4, "T5": self.T5,
                           "T6": self.T6, "T7": self.T7, "T8": self.T8, "T13": self.T13}

    def set_control_channel(self, channel):
        self.ask_raw("SET:DEV:T%d:TEMP:LOOP:HTR:H1" % channel)

    def et_pid_values(self, channel, pid):
        self.ask_raw("SET:DEV:T%d:TEMP:LOOP:P:%.6f:I:%.6f:D:%.6f" % (channel, pid[0], pid[1], pid[2]))

    def get_current_temperature(self, channel):
        return self.T_channels["T%d" % channel]()

    def set_heater_range(self, channel, range_value):
        range_options = [31.6e-6, 100e-6, 316e-6, 1.0e-3, 3.16e-3, 10e-3, 31.6e-3, 100e-3]
        if range_value not in range_options:
            raise RuntimeError('Wrong heater range!')
        else:
            range_value *= 1000  # convert to mA
            self.ask_raw("SET:DEV:T%d:TEMP:LOOP:RANGE:%.6f" % (channel, range_value))

    def temperature_control(self, control_channel, set_point, range_value, reading_interval=60):
        self.SET_CONTROL_CHANNEL(control_channel)  # set the control channel
        if control_channel != self.pid_control_channel():  # check by getting the control channel
            raise ValueError("Cannot set channel %d as control channel!" % control_channel)

        # self.pid_mode('off')  # turn off the pid
        self.pid_mode('on')  # turn of the pid
        self.pid_setpoint(set_point)  # set point temperature
        self.SET_HEATER_RANGE(control_channel, range_value)  # set heater range in unit of A
        # self.pid_range(heater_range*1e3)  # set heater range in unit of mA
        current_t = self.GET_CURRENT_TEMPERATURE(control_channel)
        criteria = set_point * 0.02  # set criteria
        start = time.time()
        t_ave_list = [current_t]
        t_ave = 0.0
        t_variance = 0.0
        n_t_ave = 10  # number of points to average to get T_ave

        while not (abs(t_ave - set_point) < criteria and len(t_ave_list) == n_t_ave):
            for i in range(100):
                time.sleep(reading_interval / 100.)

            end = time.time()
            current_t = self.GET_CURRENT_TEMPERATURE(control_channel)

            if len(t_ave_list) == n_t_ave:
                del t_ave_list[0]

            t_ave_list.append(current_t)
            t_ave = mean(t_ave_list)
            t_variance = (variance(t_ave_list)) ** 0.5
            print("%.2f second has passed, current temperature is %.6f%+.6f K." % (end - start, t_ave, t_variance))

        print("%.6f%+.6f K has been reached." % (t_ave, t_variance))
