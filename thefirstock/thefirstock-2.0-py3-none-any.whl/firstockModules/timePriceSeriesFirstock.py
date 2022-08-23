from thefirstock.firstockModules.timePriceSeriesFunctionality.execution import *


def firstock_TimePriceSeries(exchange, token, startTime, endTime):
    try:

        timePrice = FirstockTimePriceSeries(
            exch=exchange,
            token=token,
            st=startTime,
            et=endTime
        ).firstockTimePriceSeries()

        return timePrice

    except Exception as e:
        print(e)
