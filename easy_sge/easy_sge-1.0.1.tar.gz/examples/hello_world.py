from easy_sge.experiences_manager import ExperienceBase

if __name__ == "__main__":
    if ExperienceBase.is_in_SGE():  # Write your task
        parameters = ExperienceBase.load_only_current()
        first = parameters["first"]
        second = parameters["second"]
        print("{} {}".format(first, second))
    else:  # Configure your task
        my_experience = ExperienceBase()
        my_experience.add_experience_key_values("first", ["hello", "hi"])
        my_experience.add_experience_key_values("second", ["world", "idiap"])

        my_experience.add_grid_parameter("-P", "devel")
        my_experience.add_grid_parameter("-cwd", "")
        my_experience.add_grid_parameter("-N", "hello_world")

        my_experience.run(sync=True)
