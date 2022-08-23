import math


def solve(reynold):
    """
    求解方程 1/x = 2lg(Re*x-0.8)，返回x的解析解。

    因为雷诺数必然大于0，因此x>0.8/Re>0。
    进一步，因为x>0，因此Re*x-0.8>10，所以x>10.8/Re.

    :param reynold: 方程中的雷诺数
    :return: 返回x的计算结果，类型为float
    """

    def f(x):
        return 1 / (2 * math.log10((reynold * x - 0.8)))

    x0 = 100 / reynold  # 给定初值大于10.8/Re即可
    x1 = f(x0)
    i = 0
    while abs(x0 - x1) > 0.0000001 and i < 100:
        x0 = x1
        print(f"{x1=}")
        x1 = f(x0)
        i += 1
    if i == 100:
        return "计算未收敛"
    else:
        return x1


x = solve(10000)
lambda0 = x ** 2
print(f"{lambda0=}")
