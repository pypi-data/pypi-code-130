import print_report
import build_report


# главная функция
def main():
    ready_dict = build_report.build_report('../data_files')
    return print_report.print_result(ready_dict)


if __name__ == "__main__":
    print(main())