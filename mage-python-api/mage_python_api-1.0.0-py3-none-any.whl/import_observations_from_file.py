import mage_api

# collect necessary information from user
import_filepath = input('\nPlease enter the full path to your '
                        'CSV (it must be in the format of a MAGE export)\n')

origin_event_id = int(input('\nWhich event did your observation export come FROM?'
                            '\nPlease enter the event ID\n (e.g. 266)\n'))

target_event_id = int(input('\nWhich event would you like to import your observations '
                            'into? Please enter the event ID \n (e.g. 266)\n'))

session = mage_api.MageClient()

session.import_observations_from_file(import_filepath, origin_event_id, target_event_id)