import numpy as np
import os

from typing import BinaryIO
from numpy.typing import NDArray

from . import _native


class MP3:
    """
    Attributes:
        channels (int): Number of channels
        hz (int): Sampling frequency
        samples (numpy.ndarray[int16]): Audio samples of shape (CHANNELS, LEN).
    """
    samples: NDArray[np.int16]
    channels: int
    hz: int

    def __init__(
            self,
            *,
            path: str | bytes | os.PathLike | None = None,
            file: BinaryIO | None = None,
            data: bytes | None = None
    ) -> None:
        """
        Exactly one of the arguments must be given.

        Args:
            path (str | bytes | PathLike): path to the MP3 file.
            file (BinaryIO): file-like object to read MP3 from.
            data (bytes): MP3 data to decode.
        """
        args_given = (
            (path is not None) +
            (file is not None) +
            (data is not None)
        )
        if args_given > 1:
            raise TypeError(
                "Only one of input arguments can be given. Got {args_given}"
            )
        if not args_given:
            raise TypeError(
                "One of input arguments must be given. Got 0"
            )

        input = data
        if path is not None:
            with open(path, "rb") as fh:
                input = fh.read()
        elif file is not None:
            input = file.read()

        samples, channels, hz = _native.from_bytes(input)
        samples = samples.reshape(-1, channels).T
        self.samples = samples
        self.channels = channels
        self.hz = hz