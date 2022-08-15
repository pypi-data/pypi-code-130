import calendar
from datetime import date
from dateutil import relativedelta


def timeSinceStartedDating():
    start = date(2022, 6, 17)
    today = date.today()
    diff = relativedelta.relativedelta(today, start)

    return diff.years, diff.months, diff.days


def timePassed():
    print("Time Since Started Dating: {} Years, {} Months and {} Days!".format(*timeSinceStartedDating()))


def nextMilestone():
    t = timeSinceStartedDating()
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    months = (t[0] * 12) + t[1] + 1
    if months < 12:
        print("{} Months Anniversary will be in {} Days!".format(months, days_in_month - t[2]))
    else:
        print("{} Year Anniversary will be in {} Months and {} Days!".format(t[0] + 1, 12 - months, days_in_month - t[2]))


def heart():
    return"""     
              ******       ******
            **********   **********
          ************* *************
         *****************************
         *****************************
         *****************************
          ***************************
            ***********************
              *******************
                ***************
                  ***********
                    *******
                      ***
                       *
                       """
