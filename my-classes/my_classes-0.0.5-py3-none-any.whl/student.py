from my_classes import Person


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
