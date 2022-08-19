""" Module w.r.t. data transformation."""

import base64 as b64

import pandas as pd
import pyarrow as pa


def msg_to_pandas_dataframe(message: bytes, encoding: str = "utf-8") -> pd.DataFrame:
    """This function takes a Azure servicebus message transform it into a
    pandas dataframe.

    Args:
        message (bytes): The body of a Azure Service Bus message in bytes.
        encoding (str, optional): Encoding of the message. Defaults to "utf-8".

    Returns:
        pd.DataFrame: A pandas dataframe with the decoded data.
    """
    message_body = message.decode(encoding)
    parquet_file = b64.b64decode(message_body)
    buf = pa.py_buffer(parquet_file)

    return pd.read_parquet(buf)
