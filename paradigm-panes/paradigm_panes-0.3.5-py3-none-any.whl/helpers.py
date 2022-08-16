from typing import Dict

from .panes import Paradigm
from . import settings


def serialize_paradigm(paradigm: Paradigm) -> Dict[str, any]:
    """
    Serializes a Paradigm object as a dictionary

    :param paradigm: the paradigm to be serialized
    :return: dictionary representation
    """
    panes = []

    if paradigm is None:
        return {"panes": panes}

    for pane in (paradigm.panes or []):

        tr_rows = []
        for row in (pane.rows or []):
            if row.is_header:
                tr_rows.append({
                    "is_header": True,
                    "label": row.fst_tags,
                    "cells": []
                })
            else:
                cells = []
                for cell in (row.cells or []):
                    cell_data = {
                        "should_suppress_output": cell.should_suppress_output,
                        "is_label": cell.is_label,
                        "is_inflection": cell.is_inflection,
                        "is_missing": cell.is_missing,
                        "is_empty": cell.is_empty
                    }

                    if cell_data["is_label"]:
                        cell_data["label_for"] = cell.label_for
                        cell_data["label"] = cell.fst_tags

                        if type(cell_data["label_for"]) != str:  # if cell.label_for was never instantiated
                            cell_data["label_for"] = ""
                        if cell_data["label_for"] == "row":
                            cell_data["row_span"] = cell.row_span

                    elif cell_data["is_inflection"] and not cell_data["is_missing"]:
                        cell_data["inflection"] = cell.inflection

                    cells.append(cell_data)

                tr_rows.append({
                    "is_header": False,
                    "label": None,  # shouldn't be used.
                    "cells": cells
                })

        panes.append({"tr_rows": tr_rows})

    return {"panes": panes}
