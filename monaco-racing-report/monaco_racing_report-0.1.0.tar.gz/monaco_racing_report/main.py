from print_report import print_result
from build_report import *


# главная функция
def main():
    ready_dict = build_report('../data_files')
    return print_result(ready_dict)


if __name__ == "__main__":
    print(main())