from random import Random

r = Random()


def check_sort_result(func):
    arr = list()
    arr2 = list()
    for i in range(0, 100000):
        arr.append(int(r.random() * 100000))
    arr2 = arr[:]
    arr2.sort()
    func(arr)
    result = True
    print(arr)
    print(arr2)
    for i in range(len(arr)):
        if arr[i] != arr2[i]:
            print("结果不一致")
            result = False
            break
    print("结果一致")
    return result
