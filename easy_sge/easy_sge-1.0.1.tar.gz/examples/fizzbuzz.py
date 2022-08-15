from easy_sge.experiences_manager import ExperienceBase

if __name__ == "__main__":
    if ExperienceBase.is_in_SGE():  # Write your task
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
    else:  # Configure your task
        my_experience = ExperienceBase()
        my_experience.add_experience_key_values("n", list(range(1, 101)))

        my_experience.add_grid_parameter("-P", "devel")
        my_experience.add_grid_parameter("-cwd", "")
        my_experience.add_grid_parameter("-N", "fizzbuzz")

        my_experience.run(sync=True)
