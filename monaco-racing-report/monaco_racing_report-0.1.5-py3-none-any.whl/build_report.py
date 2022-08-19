import itertools
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


def generate_record(which_file, what_time):
    return [{'racer_abbreviation': el.split("_")[0][:3], "date": el.split("_")[0][3:], what_time: el.split("_")[-1]}
            for el in which_file.read().splitlines()]


def read_from_start_end_files(file_name_start, file_name_finish, folder_path):
    with open(f"{folder_path}/{file_name_start}", "r", encoding="utf-8") as file_start, \
            open(f"{folder_path}/{file_name_finish}", "r", encoding="utf-8") as file_finish:

        start_data = generate_record(file_start, "start_time")
        finish_data = generate_record(file_finish, "finish_time")

    return start_data, finish_data


def build_report(folder_path):
    # получаем результаты из функции read_from_start_end_files
    data = read_from_start_end_files('start.log', 'end.log', folder_path)

    # объединяем словари с start и end файлов
    start_end_data = merge_dictionaries(data[0], data[1])

    # объединяем словари с start_end_data and read_from_abbr
    ready_dict = merge_dictionaries(read_from_abbr('abbreviations.txt', folder_path), start_end_data)

    # в готовый список словарей ready_dict добавляем время итоговое время
    for el in ready_dict:
        el.update({"result_time": str(abs(datetime.strptime(el['finish_time'], "%H:%M:%S.%f") - datetime.strptime(el['start_time'], "%H:%M:%S.%f")))})

    # возвращаем готовый список словарей со всеми данными (еще не отсортированный)
    return ready_dict
