import uuid

from copy import deepcopy


from .io import (read_board, write_board, read_notebook, write_notebook,
                 read_text_file, write_text_file,
                 get_board_notebook_and_text_filenames_in_tree)


def _updated_id(old_id, new_id_for_old_id):
    """Update ids.

    Parameters
    ----------
    old_id :
        Id to update.
    new_id_for_old_id :
        Dictionary giving new keys ids old ids.

    Returns
    -------
    new_id :
        The updated id.

    """
    new_id = old_id
    while new_id in new_id_for_old_id.keys():
        new_id = new_id_for_old_id[new_id]
    return new_id


def create_card_id():
    return str(uuid.uuid4())


def assign_new_card_ids_to_board(board, new_id_for_old_id, inplace=False):
    """Assign new ids to cards in board.

    Parameters
    ----------
    board :
        The board for which to assign new card ids.
    new_id_for_old_id :
        A dictionary for recording the mapping from old ids to new ids.
    inplace :
        Whether to assign ids in place.

    Returns
    -------
    board :
        The board with new ids.

    """
    if not inplace:
        board = deepcopy(board)

    for node in board['nodes']:
        if node['type'] == 'note':
            old_id = node["id"]
            new_id = str(uuid.uuid4())
            node["id"] = new_id

            new_id_for_old_id[old_id] = new_id

    for edge in board['edges']:
        edge["node_connections"] = [new_id_for_old_id.get(old_id, old_id)
                                    for old_id in edge["node_connections"]]

    return board


def replace_card_ids_in_notebook(notebook, new_id_for_old_id, inplace=False):
    """Replace card ids in notebook.

    Parameters
    ----------
    notebook :
        The notebook in which to replace card ids.
    new_id_for_old_id :
        The mapping from old ids to new ids.
    inplace :
        Whether to replace ids in place.

    Returns
    -------
    notebook :
        The notebook with the card ids replaced.

    """
    if not inplace:
        notebook = deepcopy(notebook)

    for cell in notebook["cells"]:
        if "connections" in cell:
            for connection in cell["connections"]:
                connection["id"] = _updated_id(connection["id"], new_id_for_old_id)

    return notebook


def replace_card_ids_in_text(lines, new_id_for_old_id, inplace=False):
    """Replace card ids in text.

    Parameters
    ----------
    lines :
        The text as list of lines in which to replace card ids.
    new_id_for_old_id :
        The mapping from olds ids to new ids.
    inplace :
        Whether to replace ids in place.

    Returns
    -------
    lines:
        The text as list of lines with the card ids replaced.

    """
    if not inplace:
        lines = deepcopy(lines)

    for line_number, line in enumerate(lines):
        if line[:16] == '# <halerium id="' or line[:17] == '# </halerium id="':
            line_parts = line.split('"')
            if len(line_parts) != 3:
                raise ValueError(f"Cannot interpret special comment line {line_number}: {line}")
            prefix, old_id, suffix = line_parts
            new_id = _updated_id(old_id, new_id_for_old_id)
            lines[line_number] = f'{prefix}"{new_id}"{suffix}'

    return lines


def assign_new_card_ids_to_board_file(board_file, new_board_file, new_id_for_old_id):
    """Assign new card ids to board file.
    
    Parameters
    ----------
    board_file :
        The file to read the board from.
    new_board_file :
        The file to write the board with the new ids to.
    new_id_for_old_id :
        The dictionary for recording the mapping from old ids to new ids.

    Returns
    -------

    """
    board = read_board(board_file)
    board = assign_new_card_ids_to_board(board, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_board(board, new_board_file)


def replace_card_ids_in_notebook_file(notebook_file, new_notebook_file, new_id_for_old_id):
    """Replace card ids in notebook file.

    Parameters
    ----------
    notebook_file :
        The file to read the notebook from.
    new_notebook_file :
        The file to write the notebook with replaced ids to.
    new_id_for_old_id :
        The mapping from old ids to new ids.

    Returns
    -------

    """
    notebook = read_notebook(notebook_file)
    notebook = replace_card_ids_in_notebook(notebook, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_notebook(notebook, new_notebook_file)


def replace_card_ids_in_text_file(text_file, new_text_file, new_id_for_old_id):
    """Replace card ids in text file.

    Parameters
    ----------
    text_file :
        The file to read the text from.
    new_text_file :
        The file to write the text with replaced ids to.
    new_id_for_old_id :
        The mapping from old ids to new ids.

    Returns
    -------

    """
    lines = read_text_file(text_file)
    lines = replace_card_ids_in_text(lines, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_text_file(lines, new_text_file)


def assign_new_card_ids_to_files(board_files, notebook_files, text_files,
                                 new_board_files=None, new_notebook_files=None, new_text_files=None):
    """Assign new card ids to file.

    Assign new ids to all cards in all boards in board files.
    Then replace all old card ids with these new card ids
    in the notebook and text files provided.
    If new board, notebook, or text files are provided, the results are written
    there. Otherwise, the ids are replaced in-place.

    Parameters
    ----------
    board_files :
        The list of board files.
    notebook_files :
        The list of notebook files.
    text_files :
        The list of text files.
    new_board_files :
        The list of files to write boards with new card ids to.
        If omitted, files written to are the same as read from.
    new_notebook_files :
        The list of files to write notebooks with new card ids to.
        If omitted, files written to are the same as read from.
    new_text_files :
        The list of files to write texts with new card ids to.
        If omitted, files written to are the same as read from.

    """
    new_board_files = new_board_files or board_files
    new_notebook_files = new_notebook_files or notebook_files
    new_text_files = new_text_files or text_files

    new_id_for_old_id = dict()

    for board_file, new_board_file in zip(board_files, new_board_files):
        assign_new_card_ids_to_board_file(board_file, new_board_file, new_id_for_old_id)

    for notebook_file, new_notebook_file in zip(notebook_files, new_notebook_files):
        replace_card_ids_in_notebook_file(notebook_file, new_notebook_file, new_id_for_old_id)

    for text_file, new_text_file in zip(text_files, new_text_files):
        replace_card_ids_in_text_file(text_file, new_text_file, new_id_for_old_id)


def assign_new_card_ids_to_tree(path, include_symlinks=False):
    """Assign new card ids to all files in directory tree.

    Assign new ids to all cards in all board files in a directory tree.
    Then replace all old card ids with these new card ids
    in all notebook and text files in the tree.
    The ids are replaced in-place.

    Parameters
    ----------
    path :
        The root of the directory tree.
    include_symlinks :
        Whether to include symbolic links.
        The default is `False`.

    Returns
    -------
    board_filenames :
        The list of board file names in tree.
    notebook_filenames :
        The list of notebook file names  in tree.
    text_filenames :
        The list of text file names in tree.

    """
    board_filenames, notebook_filenames, text_filenames = \
        get_board_notebook_and_text_filenames_in_tree(path, include_symlinks=include_symlinks)
    assign_new_card_ids_to_files(board_filenames, notebook_filenames, text_filenames)

    return board_filenames, notebook_filenames, text_filenames
