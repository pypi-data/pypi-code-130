class Person:
    def __init__(self, name: str, age: int) -> None:
        self._name = name
        self._age = age

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, age: int) -> None:
        self._age = age


class Student(Person):
    def __init__(self, name: str, age: int, avg_grades: float) -> None:
        super().__init__(name, age)
        self._avg_grades = avg_grades

    @property
    def avg_grades(self) -> float:
        return self._avg_grades

    @avg_grades.setter
    def avg_grades(self, avg_grades: float):
        self._avg_grades = avg_grades

    def __str__(self):
        return f'Student name is {self._name} and age is {self._age} and avg is {self._avg_grades}'

    def __repr__(self):
        return f'{self.__dict__}'


class Teacher(Person):
    def __init__(self, name: str, age: int, salary: float) -> None:
        super().__init__(name, age)
        self._salary = salary

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, salary: float):
        self._salary = salary

    def __str__(self):
        return f'Teacher name is {self._name} and age is {self._age} and salary is {self._salary}'

    def __repr__(self):
        return f'{self.__dict__}'
