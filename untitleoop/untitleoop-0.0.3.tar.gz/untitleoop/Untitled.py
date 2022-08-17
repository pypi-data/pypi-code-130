# Object Oriented Program

# -*-coding: utf-8 -*-

# Untitled.py

class Student:
    def __init__(self,name,lastname):
        self.name = name
        self.lastname = lastname
        self.exp = 0
        self.lesson = 0
        self.vehicle = 'Bus'

    @property
    def fullname(self):
        return '{} {}'.format(self.name, self.lastname)

    def Coding(self):
        self.AddExp()
        print('{} Studying Python'.format(self.fullname))

    def showExp(self):
        print('{} get {} exp ({} times)'.format(self.name,self.exp,self.lesson))

    def AddExp(self):
        self.exp += 10
        self.lesson += 1

    def __str__(self):
        return self.fullname

    def __repr__(self):
        return self.fullname

    def __add__(self,other):
        return self.exp + other.exp 

class Tesla:
    def __init__(self):
        self.model = 'Tesla Model S'

    def SelfDriving(self,st):
        print('Auto pilot is in progress...taking Mr.{} back home'.format(st.name))

    def __str__(self):
        return self.model

class SpecialStudent(Student):
    def __init__(self,name,lastname,father):
        super().__init__(name,lastname)
        
        self.father = father
        self.vehicle = Tesla()
        print('Do you know me?..!\nI am son of {}'.format(self.father))

    def AddExp(self):
        self.exp += 30
        self.lesson += 2

class Teacher:
    def __init__(self,fullname):
        self.fullname = fullname
        self.students = []

    def CheckStudents(self):
        print('--- Student in {} ---'.format(self.fullname))
        for i,st in enumerate(self.students):
            
            print('{}-->{} [{} exp][{} Times]'.format(i+1, st.fullname, st.exp, st.lesson))

    def AddStudent(self,st):
        self.students.append(st)

    def __str__(self):
        return self.fullname

# print('File : '__name__)
if __name__ == '__main__':
    

    # Day 0
    print('\n--- Day 0 ---')
    allstudent = []

    teacher1 = Teacher(fullname='Ada Lovelace')
    teacher2 = Teacher(fullname='Billy Gloves')
    print(teacher1.students)


    # Day 1
    print('\n--- Day 1 ---')
    st1 = Student('Alberto','Einsteino')
    allstudent.append(st1)
    teacher2.AddStudent(st1)  
    print(st1.fullname)

    # Day 2
    print('\n--- Day 2 ---')
    st2 = Student('Steven','Joops')
    allstudent.append(st2)
    teacher2.AddStudent(st2)
    print(st2.fullname)

    # Day 3
    print('\n--- Day 3 ---')
    for i in range(3):
        st1.Coding()
    st2.Coding()
    st1.showExp()
    st2.showExp()

    # Day 4
    print('\n--- Day 4 ---')
    stp1 = SpecialStudent('Helmut','Schmeicer','Zemo')
    allstudent.append(stp1)
    teacher1.AddStudent(stp1)
    print(stp1.fullname)
    print('Professor give me 20 points')
    stp1.exp = 20
    stp1.Coding()
    stp1.showExp()

    # Day 5
    print('\n--- Day 5 ---')
    print('How do you go home?')
    print('{}, {} and {}'.format(allstudent[0],allstudent[1],allstudent[2]))
    for st in allstudent:
        print('I\'m {}, going by {}'.format(st.name,st.vehicle))
        if isinstance(st,SpecialStudent):
            st.vehicle.SelfDriving(st)

    # Day 6
    print('\n--- Day 6 ---')
    teacher1.CheckStudents()
    teacher2.CheckStudents()

    print('Total exp for 2 guys is ',st1 + st2)