"""A simple """
__version__="0.01"
import math as m
print("_________ LIMIT CALCULATOR _________________________" )
fnc_list=[m.sin,m.cos,m.tan,m.log,m.exp,m.acos,m.asin,m.atan,m.acosh,m.asinh,m.atanh,m.sinh,m.cosh,m.tanh]
const_list=[m.pi,m.e]
const_names=["pi","euler"]
for sec in fnc_list:
    print(str(fnc_list.index(sec) +1)+")" , sec.__name__)
        
print("\n")
print("---constant you can use"*2 ,end="\n")
print("")
for const in range(len(const_names)):
    print(str(const+1)+")",const_names[const])

print("")
select=int(input("Enter the number before the function to calculate limit :") )

print("\n limit of {} as  x-->c \n".format(fnc_list[select-1].__name__ ) )

user_input1=input("Enter the numbeer  'x':")
user_input2=input("Enter the number   'c':")

a=0
t=0
if ( user_input1 in const_names ) or (user_input2 in const_names):
    print("\n Calculting please wait...")
    try:
        index_of_user_input1=const_names.index(user_input1)
        index_of_user_input2=const_names.index(user_input2)
    except ValueError:
        if  user_input1.isnumeric():
            a=float(user_input1)
            t=float(const_list[const_names.index(user_input2)])
            
        if  user_input2.isnumeric() :
            t=float(user_input2)
            a=const_list[const_names.index(user_input1)]

    

            
   
else:
    print("\n Calculating please wait ....")
    a=float(user_input1)
    t=float(user_input2)
    
names=dir(m)


l=[]
l.append(a)
x=0
f=0

def parity(c):
    
    if c%2==0:
        return False
    else:
        return True
        
while True:
    n=t/( round(  m.pi /2 ,len(str(t))-2 ) )
    s=str(n)
    test=float(s[s.index("."):len(s):1])==0.0
    if(fnc_list[select-1]==m.tan and parity(n) and test):
        print("undefine")
        break
    if( fnc_list[select-1]==m.log and ( a ==0 or t==0) ):
        print("undefine")
        break
    sign=1
    if( t<a):
        sign=-1
    else:
        sign=1
    x+=1
    v=l.pop()
    p=m.nextafter(v,t)
    l.append(  abs(p+(0.000001)*sign)  )
    f=fnc_list[select-1](l[0])
    if x>( abs(a-t) /0.000001 ) :
        print("\n Result :")
        print("\n limit of the function {0} as x-->{1} is {2}".format(fnc_list[select-1].__name__,user_input2, round(f,4) ) )
        break


    
