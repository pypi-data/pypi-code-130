import mage_api
import datetime

# collect necessary information from user
sandbox_event_id = int(input('\nPlease enter the event ID from which '
                             'you would like to PULL observations\n (e.g. 10)\n'))

live_event_ids = input('\nPlease enter the event ID(s) to which '
                          '\nyou would like to PUSH observations\n (e.g. 14, 15, 16)\n')


# get most recent weekday for start_date, pull observations from only that day
today = datetime.date.today()


def get_latest_weekday(date):
    curr_weekday = date.weekday()
    if (curr_weekday > 0) and (curr_weekday <= 5):
        latest_weekday = date - datetime.timedelta(days=1)
    elif curr_weekday == 0:
        # get last friday for Mon
        latest_weekday = date - datetime.timedelta(days=curr_weekday) + datetime.timedelta(days=4, weeks=-1)
    elif curr_weekday == 6:
        # get current week's friday for Sun
        latest_weekday = date - datetime.timedelta(days=curr_weekday) + datetime.timedelta(days=4)
    return latest_weekday


start_date = get_latest_weekday(today)
end_date = start_date + datetime.timedelta(days=1)
# convert dates to strings
start_date = datetime.datetime.strftime(start_date, "%Y-%m-%d")
end_date = datetime.datetime.strftime(end_date, "%Y-%m-%d")

# convert single or multiple live_events passed as string to list of ints
live_event_ids = [int(event_id) for event_id in "".join(live_event_ids.split()).split(',')]

# instantiate MAGE session
session = mage_api.MageClient()

session.clone_event_observations(sandbox_event_id, live_event_ids,
                                 observation_start_date=start_date, observation_end_date=end_date)
session.log_out()
