import mage_api

# collect necessary information from user
sandbox_event_id = int(input('\nPlease enter the event ID from which '
                             'you would like to PULL observations\n (e.g. 10)\n'))

live_event_ids = input('\nPlease enter the event ID(s) to which '
                          '\nyou would like to PUSH observations\n (e.g. 14, 15, 16)\n')

start_date = input('\nPlease enter the start of the time range '
                   'for observations you would like to copy \n (e.g. 2020-12-22)\n')

end_date = input('\nPlease enter the end of the time range '
                 'for observations you would like to copy \n (e.g. 2020-12-29)\n')

# convert single or multiple live_events passed as string to list of ints
live_event_ids = [int(event_id) for event_id in "".join(live_event_ids.split()).split(',')]

# instantiate MAGE session
session = mage_api.MageClient()

session.clone_event_observations(sandbox_event_id, live_event_ids,
                                 observation_start_date=start_date, observation_end_date=end_date)
session.log_out()
