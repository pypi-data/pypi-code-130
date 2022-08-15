from unittest import main

from easy_sge.experiences_manager import ExperienceBase

if __name__ == "__main__":
    if ExperienceBase.is_in_SGE():
        parameters = ExperienceBase.load_only_current()
        n = parameters["n"]
        my_str = ""
        if n % 3 == 0:
            my_str += "Fizz"
        if n % 5 == 0:
            my_str += "Buzz"
        if my_str == "":
            my_str = str(n)
        print("(n={:04d}) -> {}".format(n, my_str))
