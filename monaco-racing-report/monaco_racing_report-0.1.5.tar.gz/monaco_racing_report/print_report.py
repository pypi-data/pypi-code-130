import build_report
import operator


def generate_answer(num, el):
    return '{:<3} {:<18} | {:<30} | {:<50}'.format(num, el['name_surname'], el['car'], el['result_time'])


# функция, в которой алгоритм вывода данных
def print_result(ready_dict):
    print('{:<3} {:<20} {:<32} {:<50}'.format('№', 'Name Surname', 'Car', 'Result Time'))
    for num, el in enumerate(ready_dict, 1):
        if not num == 15:
            print(generate_answer(num, el))
        else:
            print(generate_answer(num, el))
            print("------------------------------------------------------------------------")


# функция, в которой получаем данные из командной строки
def print_report_cli(sort_by, folder_path):
    ready_dict = build_report.build_report(folder_path)

    print(sort_by)

    if sort_by == True:
        # сортеруем список словарей по ключу result_time
        ready_dict.sort(key=operator.itemgetter('result_time'))
    elif sort_by == False:
        ready_dict.sort(key=operator.itemgetter('result_time'), reverse=True)
    elif sort_by == None:
        ready_dict.sort(key=operator.itemgetter('result_time'))

    return print_result(ready_dict)


# функция, в которой алгоритм для вывода информации про конкретного гонщика
def show_statistic(name, folder_path):
    ready_dict = build_report.build_report(folder_path)

    for el in ready_dict:
        if el['name_surname'] == name:
            return f"{el['name_surname']} | car - {el['car']} | start time - {el['start_time']} | finish time - {el['finish_time']} | result - {el['result_time']}"