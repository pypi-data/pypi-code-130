
import math

class math_fuction() :
    def inch_change_cm(inch) :
        '''인치를 cm로 바꾸는 함수'''
        cm = inch * 2.54
        return cm

    def cir_area(radius) :
        '''원 넓이를 구하는 함수'''
        return radius * radius * math.pi()

    def cir_circum(radius) :
        '''원 둘레?를 구하는 함수(뭔지 모르겠음)'''
        return 2 * math.pi() * radius

    def gcd(x, y) :
        '''최대공약수를 구하는 함수'''
        if x > y :
            small = y
        else : 
            small = x
        for i in range(1, small + 1) :
            if((x % i == 0) and (y % i == 0)) :
                result = i
        return result

    def factorial(n) :
        '''팩토리얼을 계산하는 함수'''
        return math.factorial(n)

    def plus(a, b) :
        '''더하기를 해주는 함수'''
        return a + b

    def minus(a, b) :
        '''두 수를 빼는 함수'''
        return a - b

    def multiply(a, b) :
        '''a와 b값을 곱하는 함수'''
        return a * b

    def divide(a, b) :
        '''a와 b를 나누어주는 함수이다.'''
        return a / b

    


