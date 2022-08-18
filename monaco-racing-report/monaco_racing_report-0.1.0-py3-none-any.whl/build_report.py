import itertools
import operator
from collections import defaultdict
from datetime import datetime


def merge_dictionaries(dict1, dict2):
    temp = defaultdict(dict)

    for item in itertools.chain(dict1, dict2):
        temp[item['racer_abbreviation']].update(item)

    data = list(temp.values())
    return data


def read_from_abbr(file_name_abbr, folder_path):
    list_of_dicts = []

    with open(f'{folder_path}/{file_name_abbr}', 'r', encoding="utf-8") as fp1:
        read_data = fp1.read().splitlines()
        # записываем в список словари из имени гонщика, имя и фамилии и название машины
        [list_of_dicts.append({"racer_abbreviation": el.split("_")[0], "name_surname": el.split("_")[1], "car": el.split("_")[2]}) for el in read_data]

    return list_of_dicts


def read_from_start_end_files(file_name_start, file_name_finish, folder_path):
    start_data = []
    finish_data = []

    with open(f"{folder_path}/{file_name_start}", "r", encoding="utf-8") as file_start,\
         open(f"{folder_path}/{file_name_finish}", "r", encoding="utf-8") as file_finish:
        for el in file_start.read().splitlines():
            racer_abbreviation = el.split("_")[0][:3]
            date_race = el.split("_")[0][3:]
            time = el.split("_")[-1]
            start_data.append({'racer_abbreviation': racer_abbreviation, "date": date_race, "start_time": time})

        for el in file_finish.read().splitlines():
            racer_abbreviation = el.split("_")[0][:3]
            date_race = el.split("_")[0][3:]
            time = el.split("_")[-1]
            finish_data.append({'racer_abbreviation': racer_abbreviation, "date": date_race, "finish_time": time})

    return start_data, finish_data


def build_report(folder_path):
    # получаем результаты из функции read_from_start_end_files
    data = read_from_start_end_files('start.log', 'end.log', folder_path)

    # объединяем словари с start и end файлов
    start_end_data = merge_dictionaries(data[0], data[1])

    # объединяем словари с start_end_data and read_from_abbr
    ready_dict = merge_dictionaries(read_from_abbr('abbreviations.txt', folder_path), start_end_data)

    # в готовый список словарей ready_dict добавляем время итоговое время
    [el.update({"result_time": str(abs(datetime.strptime(el['finish_time'], "%H:%M:%S.%f") - datetime.strptime(el['start_time'], "%H:%M:%S.%f")))}) for el in ready_dict]

    # возвращаем готовый список словарей со всеми данными (еще не отсортированный)
    return ready_dict