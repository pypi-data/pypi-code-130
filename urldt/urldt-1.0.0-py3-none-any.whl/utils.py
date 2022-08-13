import csv
from typing import Tuple


def read_targets(filename: str) -> Tuple[str, list]:
    '''read targets from csv file, return csv_header and targets'''
    targets = list()
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            csv_header = next(csv_reader)
            targets = list(csv_reader)
            return csv_header, targets
    except FileNotFoundError:
        print(f'{filename} not exist!')


def write_result(filename: str, available_urls: list):
    '''write available targets into csv file'''
    with open(filename, mode='w', newline='', encoding='utf-8') as result_csv_file:
        csv_writer = csv.writer(result_csv_file, delimiter=',')
        csv_writer.writerow(['url', 'title'])
        for url in available_urls:
            csv_writer.writerow(url)
