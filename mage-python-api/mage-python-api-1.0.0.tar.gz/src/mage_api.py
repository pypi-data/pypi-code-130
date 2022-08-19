import requests
import json
import config
import time
import os
import ast
import mimetypes
import numpy as np
import pandas as pd
from datetime import datetime

from PIL import Image
from io import BytesIO

JSON_TYPE = 'application/json'

# session object containing functions for making requests, logs in and stores auth headers on __init__
class MageClient:
    def __init__(self):
        # set base url
        self.api_base_url = config.mage_environment

        # create requests session to be used for all API calls
        self.mage_session = requests.Session()

        # set initial headers, this attribute will be modified and re-used
        self.mage_session.headers = {'accept': JSON_TYPE}

        # this header will be added and removed as needed, used for sending data
        self.content_type_header = {'Content-type': JSON_TYPE}

        # provide username and password, receive response with auth id
        log_in = self.make_request('/auth/local/signin', 'post', payload=config.credentials)
        auth_info = log_in.response_body
        short_lived_token = auth_info['token']
        self.mage_session.headers['Authorization'] = f'Bearer {short_lived_token}'

        # provide token in exchange for , add token to headers for future requests
        auth = self.make_request('/auth/token', 'post')
        api_token = auth.response_body['token']
        self.mage_session.headers['Authorization'] = f'Bearer {api_token}'

        # get own mage user for verification of auth and later use
        self.own_user = self.get_self().response_body

    # framework for API calls
    def make_request(self, endpoint, method, payload=None, download_content=False, upload=None):
        # force 1 second wait for rate-limiting
        time.sleep(1)
        # get specific requests attribute from provided method, e.g. requests.get for method='get'
        request = getattr(self.mage_session, method)

        # if user needs to download content, change accept header
        if download_content:
            self.mage_session.headers['accept'] = '*/*'

        # if sending data, add temporary header
        if payload:
            self.mage_session.headers = {**self.mage_session.headers, **self.content_type_header}

        print(f'making request {method} {endpoint}...')

        # if files provided, change headers and prepare files param
        if upload:
            mime_type = mimetypes.guess_type(upload)[0]
            data = {'attachment': (upload, open(upload, 'rb').read(), mime_type)}
            response = request(self.api_base_url + endpoint,
                               headers=self.mage_session.headers, files=data)
        else:
            response = request(self.api_base_url + endpoint,
                               headers=self.mage_session.headers, data=json.dumps(payload))

        # re-format response object
        response = FormattedResponse(response)

        # display any problematic responses
        if response.response_code >= 300:
            response.pretty_print()
        # revert headers modified previously
        if payload:
            self.mage_session.headers.pop('Content-type')
        if download_content:
            self.mage_session.headers['accept'] = 'application/json'

        return response

    # AUTHENTICATION

    # log out, always put this at end of your scripts
    def log_out(self):
        log_out = self.make_request('/api/logout', 'post')
        return log_out

    # EVENTS

    # get event
    def get_event(self, event_id):
        event = self.make_request(f'/api/events/{event_id}', 'get')

        return event

    # get all events
    def get_events(self, populate=True):
        endpoint = '/api/events'
        endpoint = add_parameters(endpoint, [(populate, 'populate')])

        events = self.make_request(endpoint, 'get')

        return events

    # create new event
    def create_event(self, name, description):
        payload = dict(name=name, description=description)
        new_event = self.make_request('/api/events', 'post', payload=payload)

        # get event_id and request full event document
        new_event_id = new_event.response_body['id']
        new_event = self.get_event(new_event_id)

        # get event's team id, add self to event
        new_event_team = get_event_team(new_event.response_body)
        self.add_user_to_team(self.own_user, new_event_team)

        return new_event

    # OBSERVATIONS

    # get all observations in an event
    def get_observations(self, event_id, start_date=None, end_date=None, states='active',
                         observation_start_date=None, observation_end_date=None):
        endpoint = f'/api/events/{event_id}/observations'
        # add filter if parameters provided
        endpoint = add_parameters(endpoint, [
            (states, 'states'),
            (start_date, 'startDate'),
            (end_date, 'endDate'),
            (observation_start_date, 'observationStartDate'),
            (observation_end_date, 'observationEndDate')
        ])
        observations = self.make_request(endpoint, 'get')
        return observations

    # create new observation
    def create_observation(self, observation, event_id):
        new_observation_stub = self.make_request(f'/api/events/{event_id}/observations/id', 'post').response_body
        new_observation_id = new_observation_stub['id']

        # take stub and zip it together with user-provided observation dict
        new_observation = {**new_observation_stub, **observation}

        # add combined observation to event
        created_observation = self.make_request(f'/api/events/{event_id}/observations/{new_observation_id}',
                                                'put', payload=new_observation)
        if created_observation.response_code == 400:
            print(new_observation)

        return created_observation

    # archive observation
    def archive_observation(self, observation_id, event_id):
        state_change = {
                          "name": "archive"
                        }
        archived_observation = self.make_request(f'/api/events/{event_id}/observations/{observation_id}/states',
                                                 'post', payload=state_change)
        return archived_observation

    # TODO: support attachments
    # import file like csv generated through mage w/ observation data, create obs. from that
    def import_observations_from_file(self, filepath, origin_event_id, target_event_id, filetype='csv'):
        # change this later
        matching_form = None

        # get this for later
        origin_event = self.get_event(origin_event_id)
        origin_forms = get_event_forms(origin_event.response_body)
        target_event = self.get_event(target_event_id)
        target_forms = get_event_forms(target_event.response_body)
        devices_list = self.get_devices().response_body
        users_list = self.get_users().response_body

        # get timestamp for createdAt and lastModified
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        if filetype == 'csv':
            import_df = pd.read_csv(filepath).dropna(how='all').fillna('missing CSV import value')
            # first 11 columns are constant
            general_columns = import_df.iloc[:, 0:12]
            # last two columns are always attachment-related
            attachment_columns = import_df.iloc[:, -2:]
            # the rest are form-specific
            form_columns = import_df.iloc[:, 12:-2]
            # rename in case any column names got modified for being dupes
            form_columns.rename(columns={col: col.replace('.1', '') for col in form_columns.columns.values.tolist()},
                                inplace=True)

            column_names = form_columns.columns.values.tolist()

            # get list of unique users, so we don't have to iterate through this huge iterable for every observation
            unique_user_ids = {}
            for user in general_columns.User.unique():
                unique_user_ids[user] = [user_doc['id'] for user_doc in users_list if user_doc['username'] == user][0]


            # loop through each observation
            for forms_row, gen_row in zip(form_columns.iterrows(), general_columns.iterrows()):
                forms_row, gen_row = forms_row[1], gen_row[1]
                # get only relevant form columns
                for x, forms_col in enumerate(forms_row):
                    # find non-null form column
                    if not pd.isna(forms_col):
                        # if corresponding column name has form name in it
                        specific_col_components = form_columns.iloc[:, x].name.split('.')
                        if len(specific_col_components) > 1:
                            relevant_form_columns_names = [col for col in column_names
                                                          if col.split('.')[0] == specific_col_components[0]]
                            # stop loop if matched
                            break
                        else:
                            relevant_form_columns_names = column_names

                # find the right form
                for form in target_forms:
                    matching_fields_dict = {}
                    final_col_names = []
                    for col in relevant_form_columns_names:
                        # make sure to strip any Form.Field constructions down to just Field here
                        col_name_split = col.split('.')
                        # being extra careful here in case any field names have . in them
                        if len(col_name_split) > 2:
                            col_without_form_name = '.'.join(col_name_split[1:])
                        elif len(col_name_split) <= 2:
                            col_without_form_name = col_name_split[-1]
                        final_col_names.append(col_without_form_name)
                        for field in form['fields']:
                            if field['title'] == col_without_form_name:
                                matching_fields_dict[col_without_form_name] = field
                    # if all columns match a form field, proceed!
                    if len(matching_fields_dict) == len(relevant_form_columns_names):
                        matching_form = form
                        form_response_dict = {matching_fields_dict[short_col]['name']: forms_row[full_col]
                                              for short_col, full_col in
                                              zip(final_col_names, relevant_form_columns_names)}
                        # filter out any questions with NaN responses
                        form_response_dict = {key: form_response_dict[key] for key in form_response_dict
                                              if form_response_dict[key] != 'missing CSV import value'}

                        # check for any lists represented as strings, eval to list for import
                        form_response_dict_revision = {}
                        for key in form_response_dict:
                            try:
                                new_val = ast.literal_eval(form_response_dict[key])
                            except:
                                new_val = form_response_dict[key]
                            form_response_dict_revision[key] = new_val

                        form_response_dict = form_response_dict_revision

                        # add form id
                        form_response_dict.update(formId=matching_form['id'])

                if matching_form:
                    observation = {
                                    "createdAt": now,
                                    "deviceId": [device['id'] for device in devices_list if device['uid'] == gen_row['Device']][0],
                                    "geometry": {
                                      "type": gen_row['Shape Type'],
                                      "coordinates": [
                                       gen_row['Longitude'],
                                       gen_row['Latitude']
                                      ]
                                    },
                                    "lastModified": now,
                                    "properties": {
                                      "timestamp": gen_row["Date (ISO8601)"],
                                      "forms": [form_response_dict]
                                    },
                                    "type": "Feature",
                                    "userId": unique_user_ids[gen_row['User']],
                                    "favoriteUserIds": [],
                                  }

                    self.create_observation(observation, target_event_id)

                else:
                    print('no matching form found, skipping ...')
                    return

    # clone observation to new event
    def clone_observation(self, observation, event_id):
        # create copy to modify and submit
        copied_observation = observation.copy()
        # trim observation to allow for api to change the correct properties for new event
        for attr in ('id', 'eventId', 'url', 'state'):
            copied_observation.pop(attr)

        # create new observation in target event
        cloned_observation = self.create_observation(copied_observation, event_id).response_body

        # if observation has attachments, download and re-upload them to new observation
        if observation['attachments']:
            attachments_mapping = self.get_observation_attachments(observation)
            attachments_mapping['observationId'] = cloned_observation['id']
            attachments_mapping['eventId'] = event_id
            self.create_observation_attachments(attachments_mapping)

        return cloned_observation

    def clone_event_observations(self, origin_event_id, target_event_ids, start_date=None, end_date=None,
                                 observation_start_date=None, observation_end_date=None, suppress_confirmation=False):
        # get numpy array from int or list/tuple passed as target_event_ids
        target_event_ids = np.unique(target_event_ids)

        # confirm the events are correct before copying
        origin_event = self.get_event(origin_event_id).response_body
        target_events = [self.get_event(target_id).response_body for target_id in target_event_ids]

        if suppress_confirmation:
            proceed = True
        else:
            confirmation = input(f'\nAre you sure you want to copy observations fom {origin_event["name"]} '
                                 f'to {", ".join([event["name"] for event in target_events])}?\n'    "Y/N"'\n').lower()
            if confirmation in ('y', 'yes', 'si', 'naam'):
                proceed = True
            else:
                proceed = False
        if proceed:
            # loop through target events
            for target_event_id in target_event_ids:
                # get observations and forms from origin event each iteration to avoid modifying them
                origin_observations = self.get_observations(origin_event_id, start_date=start_date, end_date=end_date,
                                                            observation_start_date=observation_start_date,
                                                            observation_end_date=observation_end_date).response_body
                origin_forms = get_event_forms(self.get_event(origin_event_id).response_body)

                # sync forms first
                form_id_mapping = self.clone_forms(origin_forms, target_event_id)

                # then copy observations
                for obs in origin_observations:
                    # use mapping returned above to replace old formId with new one

                    # if forms, map new ids
                    if obs['properties']['forms']:
                        try:
                            origin_form_id = list(form_id_mapping['origin'].values()).index(obs['properties']['forms'][0]['formId'])
                            target_form_name = list(form_id_mapping['origin'].keys())[origin_form_id]
                            obs['properties']['forms'][0]['formId'] = form_id_mapping['target'][target_form_name]
                        except IndexError:
                            print('no form found, ingesting without form!')
                    self.clone_observation(obs, target_event_id)
            return origin_observations
        else:
            print('cancelling observation copying...')
            return

    # download attachment, takes whole observation document as input
    def get_observation_attachments(self, observation):
        # get necessary ids for request
        event_id, observation_id = observation['eventId'], observation['id']

        # look for attachments folder, create if necessary
        attachments_dir = 'observation_attachments'
        if not os.path.exists(attachments_dir):
            os.makedirs(attachments_dir)

        # iterate through attachments and download
        attachments_mapping = {
                                'observationId': observation_id,
                                'eventId': event_id,
                                'attachments': []
                               }

        for attachment in observation['attachments']:
            attachment_id, attachment_name,attachment_type = attachment['id'], attachment['name'], attachment['contentType']
            attachment = self.make_request(f'/api/events/{event_id}/observations/{observation_id}/attachments/{attachment_id}',
                                           'get', download_content=True)
            # get file from bytes
            destination_file_path = os.path.join(attachments_dir, attachment_name)
            if 'image' in attachment_type:
                attachment_file = Image.open(BytesIO(attachment.content))
                attachment_file.save(destination_file_path)

            else:
                attachment_file = open(destination_file_path, 'wb')
                attachment_file.write(attachment.content)
                attachment_file.close()

            # add file info to mapping dict for this observation, return for later re-uploading
            attachments_mapping['attachments'].append({'id': attachment_id,
                                                       'name': destination_file_path})

        return attachments_mapping

    # add new observation attachments, takes observation document and file path to attachment file as inputs
    # if not re-uploading ids with mapping...provide dict like this
    # {
    #     'observationId': observation_id,
    #     'eventId': event_id,
    #     'attachments': [attachment_paths]
    # }
    def create_observation_attachments(self, attachments_mapping):
        observation_id, event_id = attachments_mapping['observationId'], attachments_mapping['eventId']
        attachments = attachments_mapping['attachments']
        # upload listed attachments
        responses_list = []
        for attachment in attachments:
            new_attachment = self.make_request(f'/api/events/{event_id}/observations/{observation_id}/attachments',
                                               'post', upload=attachment['name'])
            responses_list.append(new_attachment)

        return responses_list

    # FORMS

    # TODO: enable easier form input (currently requires fully formed dictionary)
    # add new form to event
    def create_form(self, form, event_id):
        form = self.make_request(f'/api/events/{event_id}/forms', 'post', payload=form)
        return form

    # replace existing form with new json
    def update_form(self, form, event_id, form_id):
        updated_form = self.make_request(f'/api/events/{event_id}/forms/{form_id}', 'put', payload=form)
        return updated_form

    # sync forms from one event to another, useful for copying observations
    def clone_forms(self, forms_list, event_id):
        target_event = self.get_event(event_id).response_body
        target_event_id, target_event_forms = target_event['id'], get_event_forms(target_event)

        # make sure all forms in list exist in target event
        origin_forms_dict = {form['name']: form for form in forms_list}
        target_forms_dict = {form['name']: form for form in target_event_forms}
        missing_forms = list(set(origin_forms_dict) - set(target_forms_dict))

        # remove ids from above forms before comparing form objects (id's won't match)
        origin_form_ids = {origin_name: origin_forms_dict[origin_name].pop('id') for origin_name in origin_forms_dict}
        target_form_ids = {target_name: target_forms_dict[target_name].pop('id') for target_name in target_forms_dict}

        # if any forms are missing in target event, copy them
        for form_name in missing_forms:
            for form_object in forms_list:
                if form_object['name'] == form_name:
                    new_form = self.create_form(form_object, event_id).response_body
                    target_form_ids[new_form['name']] = new_form['id']
                    break

        # update matching forms in target event to bring them in sync
        matching_form_names = list(set(origin_forms_dict).intersection(target_forms_dict))
        for form_name in matching_form_names:
            origin_forms_dict['id'] = target_form_ids[form_name]
            updated_form = self.update_form(form=origin_forms_dict[form_name],
                                            event_id=event_id, form_id=target_form_ids[form_name])

        return {'origin': origin_form_ids, 'target': target_form_ids}

    # TEAMS

    # add user to team, useful when creating events
    def add_user_to_team(self, user, team_id):
        team = self.make_request(f'/api/teams/{team_id}/users', 'post', payload=user)
        return team

    # ROLES

    # get available roles
    def get_roles(self):
        roles = self.make_request('/api/roles', 'get')
        return roles

    def grant_event_role(self, event_id, user_id, role):
        payload = {'role': role.upper()}
        new_role = self.make_request(f'/api/events/{event_id}/acl/{user_id}', 'put', payload=payload)
        return new_role

    # USERS

    # get own MAGE user document, usually for testing
    def get_self(self):
        mage_self = self.make_request('/api/users/myself', 'get')
        return mage_self

    # get users for specific event
    def get_event_users(self, event_id):
        event_users = self.make_request(f'/api/events/{event_id}/users', 'get')
        return event_users

    # get all users...this is very slow, returns very large iterable
    def get_users(self):
        all_users = self.make_request('/api/users', 'get')
        return all_users



    # DEVICES

    # get all devices
    def get_devices(self):
        devices_list = self.make_request(f'/api/devices', 'get')
        return devices_list


# format for handling responses
class FormattedResponse:
    def __init__(self, response):
        self.response_code = response.status_code
        try:
            self.response_body = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            self.response_body = response.text

        # save
        if response.content:
            self.content = response.content

    # used for printing / logging
    def pretty_print(self):
        print(f'Response\n{self.response_code}\n{self.response_body}\n')

# SEPARATE FUNCTIONS AND VARIABLES (might make into utils.py)


# used in individual class methods to add query strings with parameters
# takes dict of parameter values and their corresponding MAGE API string
def add_parameters(endpoint, params):
    query_string = ''
    for counter, param in enumerate(params):
        # check if value in question is None
        if param[0]:
            var_string = param[-1]
            if counter == 0:
                prefix = '?'
            else:
                prefix = '&'
            # add to string with appropriate prefix
            query_string += f'{prefix}{var_string}={param[0]}'

    endpoint += query_string
    return endpoint


# extract team ID from already retrieved event object (does not make API call)
def get_event_team(event_document):
    team_id = event_document['teams'][0]['id']
    return team_id


# extract list of forms for an event
def get_event_forms(event_document):
    forms = event_document['forms']
    return forms


# get MAGE timestamp string of current time for new objects
def get_timestamp_string(datetime_obj):
    timestamp_string = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    timestamp_string += 'Z'
    return timestamp_string

