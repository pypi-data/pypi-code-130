
from ..file.io import read_notebook, write_notebook


def is_notebook(obj):
    return isinstance(obj, dict) and ("cells" in obj)


def create_card_cell_link(card_id, notebook, cell_index):
    """Add link between a Halerium board card and notebook cell.

    Parameters
    ----------
    card_id :
        The id of the card.
    notebook:
        The notebook or file path or descriptor of the notebook to add a card to.
    cell_index:
        The index of the cell in the notebook to link.

    Returns
    -------

    """
    link = {
        'id': card_id,
        'startLine': 1,
        'endLine': 1,
    }
    is_notebook_file = False
    if not is_notebook(notebook):
        is_notebook_file = True
        notebook_file = notebook
        notebook = read_notebook(notebook_file)

    notebook['cells'][cell_index]['connections'].append(link)

    if is_notebook_file:
        write_notebook(notebook, notebook_file)

