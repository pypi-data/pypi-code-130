import io

import pandas as pd

from datawhys_dashboard.api import portal_create


def create_dashboard(
    df: pd.DataFrame,
    outcome: str = None,
    name: str = None,
    description: str = None,
    **kwargs,
):
    """
    Create a dashboard from a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to create dashboard from.

    outcome : str, optional
        Which column to use as the outcome for the solve (sometimes referred to as a
        target feature). If None, then the first column is selected

    name : str, optional
        Name of the dashboard. This cannot be changed once the dashboard is created. If None,
        then the name is set using the outcome.

    description : str, optional
        Description of the dashboard. If None, then the description is indicates that the
        dashboard was created using the datawhys_dashboard package.

    kwargs: any
        Remaining kwargs are sent so api.portal_create
    """
    if outcome is None:
        outcome = df.columns[0]

    if name is None:
        name = f"SDK Dashboard | {outcome}"

    if description is None:
        description = "Automatically generated from DataWhys Dashboard SDK"

    # place outcome column first
    df = df[[outcome] + [col for col in df.columns if col != outcome]]

    # convert to CSV string and then to BytesIO
    csv_str = df.to_csv(index=False)
    data = io.BytesIO(csv_str.encode("utf-8"))

    return portal_create(data, name, description=description, **kwargs)
