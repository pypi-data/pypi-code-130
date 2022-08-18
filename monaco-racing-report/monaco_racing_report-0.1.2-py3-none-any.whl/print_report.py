from build_report import *


# функция, в которой алгоритм вывода данных
def print_result(ready_dict):
    for num, el in enumerate(ready_dict, 1):
        if not num == 15:
            print(f"{num}. {el['name_surname']} | {el['car']} | {el['result_time']}")
        else:
            print(f"{num}. {el['name_surname']} | {el['car']} | {el['result_time']}")
            print("------------------------------------------------------------------------")


# функция, в которой получаем данные из командной строки
def print_report_cli(sort_by, folder_path):
    print(folder_path)
    ready_dict = build_report(folder_path)

    if sort_by == '--asc':
        # сортеруем список словарей по ключу result_time
        ready_dict.sort(key=operator.itemgetter('result_time'))
    elif sort_by == "--desc":
        ready_dict.sort(key=operator.itemgetter('result_time'), reverse=True)

    return print_result(ready_dict)


# функция, в которой алгоритм для вывода информации про конкретного гонщика
def show_statistic(name, folder_path):
    ready_dict = build_report(folder_path)

    for el in ready_dict:
        if el['name_surname'] == name:
            return f"{el['name_surname']} | car - {el['car']} | start time - {el['start_time']} | finish time - {el['finish_time']} | result - {el['result_time']}"