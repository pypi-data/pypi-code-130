import json
import pathlib

from ipynb_strip_copy.search import Action, search_act


def prep_hw(file, suffix='_rub.ipynb', **kwargs):
    new_file_dict = {'_sol.ipynb': [('rubric', Action.RM_CELL),
                                    ('todo', Action.ERROR)],
                     '.ipynb': [('rubric', Action.RM_CELL),
                                ('solution', Action.RM_CELL),
                                ('todo', Action.ERROR)]}

    if not str(file).endswith(suffix):
        raise IOError(f'improper suffix ({suffix}) in file: {file}')

    return prep(file, new_file_dict, suffix=suffix, **kwargs)


def prep_notes(file, suffix='.ipynb', **kwargs):
    new_file_dict = {'_stud.ipynb': [('solution', Action.CLEAR_CELL),
                                     ('todo', Action.ERROR)],
                     '_ica.ipynb': [('in-class-activ', Action.RM_COMPLEMENT),
                                    ('solution', Action.CLEAR_CELL),
                                    ('todo', Action.ERROR)]}
    return prep(file, new_file_dict, suffix=suffix, **kwargs)


def prep(file, new_file_dict, suffix, verbose=True):
    if not str(file).endswith(suffix):
        raise IOError(f'improper suffix ({suffix}) in file: {file}')

    json_dict = json_from_ipynb(file)
    for new_file, target_act_list in new_file_dict.items():
        if verbose:
            print(f'building: {new_file}')
        _json_dict = search_act(json_dict, target_act_list, verbose=verbose)

        new_file = pathlib.Path(str(file).replace(suffix, new_file))

        with open(str(new_file), 'w') as f:
            json.dump(_json_dict, f)


def json_from_ipynb(file):
    file = pathlib.Path(file)

    with open(str(file), 'r') as f:
        return json.load(f)
