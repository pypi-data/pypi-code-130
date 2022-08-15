from pprint import pprint

from easy_sge.experiences_manager import ExperienceBase

if __name__ == "__main__":
    if ExperienceBase.is_in_SGE():  # Write your task
        parameters = ExperienceBase.load_only_current()
        model_a = parameters["model_a"]
        model_b = parameters["model_b"]
        output_size = parameters["output_size"]
        pprint(parameters)
    else:  # Configure your task
        my_experience = ExperienceBase()
        my_experience.add_experience_namespace_key_values(
            "model_a", "learning_rate", [0.01, 0.02]
        )
        my_experience.add_experience_namespace_key_values(
            "model_a", "nb_leafs", [10, 50]
        )

        my_experience.add_experience_namespace_key_values(
            "model_b", "size", [500, 1000, 2000]
        )
        my_experience.add_experience_key_values("output_size", [1, 2])

        my_experience.add_grid_parameter("-P", "devel")
        my_experience.add_grid_parameter("-cwd", "")
        my_experience.add_grid_parameter("-N", "hello_sub_params")

        my_experience.run(sync=True)
