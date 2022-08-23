import copy
from enum import Enum


class Action(Enum):
    ERROR = 0
    RM_CELL = 1
    RM_COMPLEMENT = 2
    CLEAR_CELL = 3


empty_code_cell = {'cell_type': 'code',
                   'execution_count': None,
                   'metadata': {},
                   'outputs': [],
                   'source': []}
empty_markdown_cell = {'cell_type': 'markdown',
                       'metadata': {},
                       'source': []}


def search_cell(json_dict, str_target, case_sensitive=False):
    """ searches all cells for a string target

    Args:
        json_dict (dict): dictionary of ipynb file
        str_target (str): string to search for

    Returns:
        cell_list (list): list of idx of cells containing str_target
    """
    if not case_sensitive:
        str_target = str_target.lower()

    cell_list = list()
    for cell_idx, cell in enumerate(json_dict['cells']):
        s = ''.join(cell['source'])

        if not case_sensitive:
            s = s.lower()

        if str_target in s:
            cell_list.append(cell_idx)
    return cell_list


def search_act(json_dict, target_act_list, verbose=False):
    """ returns copy of json_dict. actions taken on all cells with target

    Args:
        json_dict (dict): dictionary of ipynb file
        target_act_list (list): list of tuples.  each tuple is a target string
            and an action (see ACTION_RM_CELL, ACTION_ERROR)
        verbose (bool): toggle command line output

    Returns:
        json_dict (dict): dictionary of ipynb file, actions taken on cells
            where target found
    """
    # leave original intact
    json_dict = copy.copy(json_dict)

    for str_target, action in target_act_list:
        # search cells for target string
        cell_list = search_cell(json_dict, str_target)
        if verbose:
            str_action = str(action).split('.')[1]
            print(
                f'{str_action}: {len(cell_list)} instances of "{str_target}"')

        if action == Action.RM_COMPLEMENT:
            # swap cell_list for complement
            num_cell = len(json_dict['cells'])
            cell_list = list(set(range(num_cell)) - set(cell_list))

            # swap action
            action = action.RM_CELL

        # actions on later index (so deletions don't change other idx)
        for cell_idx in reversed(cell_list):
            if action == Action.ERROR:
                s_error = f'{str_target} found in cell {cell_idx}'
                raise AttributeError(s_error)
            elif action == Action.RM_CELL:
                # delete cell
                del json_dict['cells'][cell_idx]
            elif action == Action.CLEAR_CELL:
                # replaces cell with an empty cell (of same type)
                cell_type = json_dict['cells'][cell_idx]['cell_type']
                if cell_type == 'code':
                    json_dict['cells'][cell_idx] = empty_code_cell
                elif cell_type == 'markdown':
                    json_dict['cells'][cell_idx] = empty_markdown_cell
                else:
                    raise AttributeError(
                        f'unrecognized cell type: {cell_type}')
            else:
                raise AttributeError(f'action not recognized: {action}')

    return json_dict
