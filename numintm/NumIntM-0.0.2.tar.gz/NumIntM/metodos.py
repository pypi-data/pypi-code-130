from math import cos, sin, atan




def funcion(x): #Función, se presentan dos funciones para aproximar su integral. Comente con el símbolo de gato la función que NO desea utilizar, al igual que en su respectiva integral analítica.
    return (1/(1+(x**2)))
    #return sin(x)

    # Nota 1: Primer función: intervalos testeados [a,b] = [1,2], [6,10]  
    # Nota 2: Segunda función: intervalos testeados [a,b] = [0,pi/4=0.78539816339], [0,pi=3.141592653589793]  


def trapecio(f,x_0,x_1,h):  # Método extra 1 (visto en clase)
    return ((h/2)*(f(x_0)+f(x_1)))

def Simpson(f,x_0,x_1,x_2,h): # Método extra 2
    return ((h/3)*(f(x_0)+(4*f(x_1))+f(x_2)))

def NewtonCotOpen(f,x_1,x_2,x_3,x_4,h): #aproximación mediante polinomios de Lagrange  (Tarea 1 ---> Ejercicio 4)
    return ((h/24)*((55*f(x_1))+(5*f(x_2))+(5*f(x_3))+(55*f(x_4))))

def trap_Comp(f,a,b,h,n):
    list1 = []
    sum = 0 
    inc = a+h
    for i in range(n-1):
        list1.append(inc)
        inc += h
        
    for _ in list1:
        sum += f(_)
    return ((h/2)*(f(a)+f(b)+(2*sum)))


def analitica(a,b): #Derivada analítica, comente con el símbolo de gato la función que NO desea utilizar.
    return (atan(b)- atan(a))
    #return -cos(b)+cos(a)


def error(analitica, numerica):
    return (abs((analitica-numerica)/analitica)*100) 

