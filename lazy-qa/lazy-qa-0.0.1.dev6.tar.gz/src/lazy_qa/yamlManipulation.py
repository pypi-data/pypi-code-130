import yaml

# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate YAML                                                   #
# ---------------------------------------------------------------------------------------------------------------------#

# ------------------------------------------------- YAML Functions ----------------------------------------------------#


def read_yml_file(file_path):
    with open(file_path) as file:
        data = yaml.full_load(file)
        file.close()
        return data


def select_the_keys_from_yml(yml_path, parent_reference):
    environments = read_yml_file(yml_path)
    params = set()
    if parent_reference == "environment":
        for key in environments.keys():
            params.update(environments)
            return sorted(params)
    else:
        for key in environments.keys():
            params.update(environments[key])
            return sorted(params)
