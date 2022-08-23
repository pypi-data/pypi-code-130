

def print_author_info():
    """print author information"""

    print('*'*53)
    print("*\tAuthor: C.L. Qin\tE-mail: clqin@foxmail.com\t*")
    print('*' * 53)


def print_properties(properties):
    """print properties"""

    print('-'*53)
    length = 0
    for i in properties.keys():
        i = len(i)
        if i > length:
            length = i
        # print(length)
    total_length = ((length // 4) + 2) * 4
    # print(total_length)
    for key, value in properties.items():
        num = (total_length - len(key)) // 4
        flag = (total_length - len(key)) % 4
        if flag == 0:
            num -= 1
        print("{}{}:\t{}".format(key, '\t' * num, value))
    print('-' * 53)


if __name__ == '__main__':

    properties = {'fafafasf555': 1, 'afa5': 2}
    print(print_properties(properties))
