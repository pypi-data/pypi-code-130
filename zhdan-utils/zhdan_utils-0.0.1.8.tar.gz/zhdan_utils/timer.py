import time

def timer(time_mark_name, avg=True, pr=True,*,time_measurements={}):
    """
    function that times parts of code in a convenient way
    :param time_mark_name: string - name of unique time marker
    :param avg: bool - True calculates and outputs average time difference
    :param pr: bool - True print output and doesn't return it, False returns output and doesn't print it
    [print or]:return: time difference, [optional] average time difference

    example:

    timer("kek")

    ...

    timer("kek", avg=True, pr=True)

    result:

    kek -- time: 0.003926992416381836 -- average time: 0.001919304452291349

    """
    current_time = time.time()
    if time_mark_name in time_measurements:
        if time_measurements[time_mark_name][3]:
            time_difference = current_time - time_measurements[time_mark_name][0]
            time_measurements[time_mark_name] = [current_time, time_measurements[time_mark_name][1] + time_difference,
                                                 time_measurements[time_mark_name][2] + 1, False]
            if avg:
                average_time_difference = time_measurements[time_mark_name][1] / time_measurements[time_mark_name][2]
                if pr:
                    print(f"{time_mark_name} -- time: {time_difference} -- average time: {average_time_difference}")
                else:
                    return time_difference, average_time_difference
            else:
                if pr:
                    print(f"{time_mark_name} -- time: {time_difference}")
                else:
                    return time_difference
        else:
            time_measurements[time_mark_name] = [current_time, time_measurements[time_mark_name][1], time_measurements[time_mark_name][2], True]
    else:
        time_measurements[time_mark_name] = [current_time, 0, 1, True]
