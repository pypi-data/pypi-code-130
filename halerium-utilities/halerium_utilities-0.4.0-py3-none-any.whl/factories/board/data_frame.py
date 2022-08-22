from halerium_utilities.board.board import create_card, add_card_to_board


def add_card_from_data_frame_info(board, title, data, description=None, card_properties=None):
    """Add card with info from data frame to board.

    Parameters
    ----------
    board :
        Board or file path or descriptor of the board file.
    title :
        The title of the card.
    data : pandas.DataFrame
        The dataframe.
    description : dict, optional
        A dictionary providing a description for columns.
    card_properties :
        A dictionary with properties to be added to the card.

    Returns
    -------
    node_id :
        The unique id of the card added.

    """
    description = description or dict()

    ops = list()
    ops += [{'attributes': {'header': '1'}, 'insert': 'Columns\n'}]
    ops += [{'attributes': {'list': 'bullet'},
             'insert': f'name: {name}, dtype: {dtype}, description: {description.get(name, "")} \n'}
            for name, dtype in data.dtypes.items()]

    card = create_card(title=title, content=ops, card_properties=card_properties)
    add_card_to_board(board=board, card=card)
    return card['id']


def add_card_from_data_frame(board, title, data, columns=None, card_properties=None):
    """Add card with data frame to board.

    Parameters
    ----------
    board :
        Board or file path or descriptor of the board file.
    title :
        The title of the card.
    data : pandas.DataFrame
        The dataframe.
    columns : optional
        The list of columns to select.
    card_properties :
        A dictionary with properties to be added to the card.

    Returns
    -------
    node_id :
        The unique id of the card added.

    """
    if columns is not None:
        data = data[data.columns.intersection(columns)]

    index_name = data.index.name or "index"

    rows = [
        f'"{index_name}": {r[0]} | ' +
        ', '.join(f'"{key}": {value}' for key, value in r[1].items()) +
        '\n'
        for r in data.iterrows()
    ]

    ops = list()
    ops += [{'attributes': {'header': '1'}, 'insert': 'Data\n'}]
    ops += [{'attributes': {'list': 'bullet'}, 'insert': row}
            for row in rows]

    card = create_card(title=title, content=ops, card_properties=card_properties)
    add_card_to_board(board=board, card=card)
    return card['id']
