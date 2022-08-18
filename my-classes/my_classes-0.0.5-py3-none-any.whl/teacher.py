from my_classes import Person


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
