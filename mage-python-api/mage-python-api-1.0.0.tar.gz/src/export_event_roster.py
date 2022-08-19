import mage_api
import pandas as pd

# collect necessary information from user
event_id = int(input('\nPlease enter the event ID from which '
                             'you would like to export the roster\n'))

# instantiate MAGE session
session = mage_api.MageClient()

users_json = session.get_event_users(event_id).response_body

users_dict = {'email': [user['email'] for user in users_json]}

users_df = pd.DataFrame.from_dict(users_dict)

print(users_df)

users_df.to_csv(f'MAGE_event_{event_id}_roster_export.csv')
