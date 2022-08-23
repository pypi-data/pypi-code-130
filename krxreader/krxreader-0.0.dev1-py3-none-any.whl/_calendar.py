from datetime import datetime, timezone, timedelta


def today():
    return datetime.now(tz=timezone(timedelta(hours=9))).date()


def is_weekend(date):
    week = date.weekday()

    if week == 5 or week == 6:
        return True
    else:
        return False


def is_holiday(date):
    """
    NotImplemented
    """
    return False


def is_trading_day(date):
    if is_weekend(date) or is_holiday(date):
        return False
    else:
        return True


if __name__ == '__main__':
    today = today()
    print(today)

    if is_trading_day(today):
        print('trading day')
    else:
        print('closing day')
