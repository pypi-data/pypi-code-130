import qcodes.instrument_drivers.oxford.MercuryiPS_VISA as mercury_ips
import numpy as np
import time
from IPython import display


def field_limit(x: int, y: int, z: int) -> bool:
    if z > 13.1:
        return False
    else:
        return True


def m_to_zero(machine, ramp_rate, delay=1.0):
    current_field = machine.z_measured()
    mer.GRPZ.field_ramp_rate(ramp_rate / 60 / 8.82)  # 8.82 for Triton 200  #14.575 for Triton 500
    if abs(current_field) > 0:
        points = int(abs(current_field) * 200)
        for i in np.linspace(current_field, 0, points + 1):
            print(f'Ramping Z to %.4f T...' % (mer.z_target()))
            mer.z_target(i)
            mer.ramp(mode='simul')  # 開始的指令
            flag = True
            while flag:
                flag = (mer.GRPZ.ramp_status() != "HOLD")
                time.sleep(delay)
            display.clear_output(wait=True)
            # sleep(delay)
        print('到零磁場囉')
    else:
        print('已經歸零囉')


def m_to_zero_to_zero(machine, ramp_rate, delay=1.0):
    mer.z_target(0.)
    mer.GRPZ.field_ramp_rate(ramp_rate / 60 / 8.82)
    mer.ramp(mode='simul')
    flag = True
    while flag:
        flag = (mer.GRPZ.ramp_status() != "HOLD")
        print('歸零中,目前磁場%.4f T' % (mer.z_measured()))
        time.sleep(delay)
        display.clear_output(wait=True)
        # sleep(delay)
    print('到零磁場囉')


def m_to_target(machine, ramp_rate, target, delay=1.0):
    mer.z_target(target)
    mer.GRPZ.field_ramp_rate(ramp_rate / 60 / 8.82)
    mer.ramp(mode='simul')
    flag = True
    while flag:
        flag = (mer.GRPZ.ramp_status() != "HOLD")
        print('目前磁場%.4f T' % (mer.z_measured()))
        time.sleep(delay)
        display.clear_output(wait=True)
        # sleep(delay)
    print('到磁場囉')


# address 為分享器的address
mer = mercury_ips.MercuryiPS(name='Mercury_IPS', address="TCPIP0::192.168.1.6::7020::SOCKET",
                             visalib=None, field_limits=field_limit)

# mer.set_new_field_limits(FIELD_LIMIT)
mer.print_readable_snapshot(update=True)
