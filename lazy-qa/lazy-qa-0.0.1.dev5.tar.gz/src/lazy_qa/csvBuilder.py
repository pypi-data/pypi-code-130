import json
import csv
import pandas as pd
import os


# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate CSV data files                                         #
# ---------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------- CSV Functions ----------------------------------------------------#


def delete_output_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def load_csv(csv_file_path):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def load_csv_multiple_lines(csv_file, group_key, output_list_name, list_fields):
    result = {}
    with open(csv_file, 'r') as fh:
        csv_reader = csv.DictReader(fh)
        for row in csv_reader:
            group_key_joined = get_group_key(row, group_key)
            if group_key_joined not in result:
                result[group_key_joined] = row.copy()
                result[group_key_joined][output_list_name] = []
            result[group_key_joined][output_list_name].append({field: row[field] for field in list_fields})

    return [json.dumps(data) for data in result.values()]


def get_group_key(row, group_key):
    return "_".join(str(row[r]) for r in row if r in group_key)


def get_scenario_data_csv(csv_file_path, test_scenario_id):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if test_scenario_id == row["test_scenario_id"]:
                new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def get_each_line_data_csv(csv_file_path):
    new_json = []
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            new_json.append(json.dumps(row, sort_keys=True))
    return new_json


def converter_pandas_csv_json(data_path):
    df = pd.read_csv(data_path)
    new_json = df.to_json(orient='records')
    return new_json

