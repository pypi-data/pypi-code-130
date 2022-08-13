# def add(a, b):
#     return a + b

def maximum():

    n = int(input())

    a = list(map(int, input().split()))

    nu = a[0]
    bb = a[0]

    for i in range(1, n):
        if nu + a[i] >= bb:
            bb = nu + a[i]
        nu = nu + a[i]
        if nu + a[i] < 0:
            nu = 0
    return bb