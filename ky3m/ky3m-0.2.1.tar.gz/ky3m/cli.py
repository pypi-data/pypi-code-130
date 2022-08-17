import ky3m.methods
from ky3m import methods
from ky3m.common.latin import *


# methods.py adapter
def use_method(_input_data):
    report = None

    # "m" := "method"
    m_fields = _input_data.split(' ')
    m_name = m_fields[0]

    # specification definition
    try:
        m_spec = m_fields[1:]
    except IndexError:  # if no spec. provided
        m_spec = []

    try:
        if m_name.casefold() in dir(methods):  # check for method existence
            m = getattr(methods, m_name.casefold())
            report = m(tuple(m_spec))  # method call, report.Report class returned
            if report is None:
                print('Nothing to report!')
            else:
                print(report)
        else:
            print(f'Method {m_name} does not exist!')
    except ky3m.methods.InvalidSpecification:
        print(f'Method {m_name} accepts a different specification format!')
    except NotImplementedError:
        print(f'Method {m_name} is not implemented!')

    return report


# developer function
def use_method_adv(_input_data):
    report = use_method(_input_data)

    # check log for presence
    if report:
        log = ''
        for record in report.log:
            log += record + '\n'
        print(f'\nLog intercepted:\n{log}')
    else:
        pass


def main():
    while True:
        print('\nKy3M :> ', end='')
        input_data = input().strip()

        # for METHODS (if first word is capitalized)
        if all(char in latin_upper for char in input_data.split(' ')[0]):
            use_method(input_data)

        # for METHODS (for developers)
        elif (all(char in latin_upper for char in input_data[3:].strip().split(' ')[0]) and
              input_data.split(' ')[0][:3] == 'adv'):
            use_method_adv(input_data[3:])

        else:
            print('Unknown syntax!')


if __name__ == '__main__':
    main()
