import numpy as np
import os

from array import array
from typing import BinaryIO, Iterable
from numpy.typing import NDArray

from . import _native

Buffer = bytearray | array | memoryview | bytes | NDArray


class DecoderError(Exception): pass


class StreamDecoderUninitialised(DecoderError): pass


class StreamDecoder:
    """Streaming mp3 decoder.
    
    High level usage:

    data = some_bytes_iterator  # i.e. data from http response
    for raw_samples_block in stream_decoder.stream(data):
        # raw_samples_block is a NumPy array of int16 shaped (CHAN, SOME_LEN)
        do_something_with(raw_sample_block)

        # channel and hz attributes are not available before first data
        channels = stream_decoder.channels
        sampling_rate = stream_decoder.hz
    
    Alternatively if you have a file-like object opened for binary reading:

    with open(file_path, "rb") as file_handle
    for raw_samples_block in stream_decoder.stream_from_file(file_handle):
        # do something with the decoded samples

    Low level usage:
    stream_decoder = StreamDecoder()
    decoded_samples = stream_decoder.decode(mp3_bytes)
    more_decoded_samples = stream_decoder.decode(more_mp3_bytes)
    final_samples = stream_decoder.flush()

    # Optionally, to reuse the decoder later:
    stream_decoder.reset()
    """

    _decoder: _native.StreamDecoder

    def __init__(self) -> None:
        self._decoder = _native.StreamDecoder()

    @property
    def channels(self) -> int:
        """Number of channels.

        Only available after first frame has been decoded.
        """
        if self._decoder.channels is None:
            raise StreamDecoderUninitialised(
                "Channels and samling rate are only available after the first "
                "frame has been decoded"
            )
        return self._decoder.channels

    @property
    def hz(self) -> int:
        """Sampling rate.

        Only available after first frame has been decoded.
        """
        if self._decoder.hz is None:
            raise StreamDecoderUninitialised(
                "Channels and samling rate are only available after the first "
                "frame has been decoded"
            )
        return self._decoder.hz

    def decode(self, input: Buffer) -> NDArray[np.int16] | None:
        """Decode the next block.

        Args:
            input (bytes-like): mp3 binary data

        Returns:
            Audio samples of shape (CHANNELS, LEN) or None if no data has been
            decoded from the block.
        """
        samples = self._decoder.decode(input)
        if samples.size == 0:
            return None
        return samples.reshape(-1, self._decoder.channels).T

    def flush(self) -> NDArray[np.int16] | None:
        """Decode the leftovers from the internal buffer.

        Returns:
            Audio samples of shape (CHANNELS, LEN) or None if no data has been
            decoded.

        Note that after a call to flush() you cannot call decode() anymore,
        until reset() is call, to indicate an explicit cleanup.
        """
        samples = self._decoder.flush()
        if samples.size == 0:
            return None
        return samples.reshape(-1, self._decoder.channels).T

    def reset(self) -> None:
        """Prepare decoder for a new stream.

        Resets all internal state forgetting all previously undecoded data.
        """
        self._decoder.reset()

    def stream(self, input: Iterable[Buffer]) -> Iterable[NDArray[np.int16]]:
        """Iterates over input and yield decoded samples.
        
        Args:
            input (Iterable[bytes-like]: input stream of mp3 data)

        Wraps an iterator/iterable. Returns an iterator, yielding samples as
        they are decoded. After the first block of samples is yielded the
        number of channels and sampling rate become available as normal in
        channel and hz attributes of the decoder.
        """
        for block in input:
            samples = self.decode(block)
            if samples is None:
                continue
            yield samples
        samples = self.flush()
        if samples is None:
            return
        yield samples

    def stream_from_file(
        self,
        file: BinaryIO,
        blocksize: int = 65536,
    ) -> Iterable[NDArray[np.int16]]:
        """Reads a file in blocks, yielding decoded samples.

        Args:
            file (BinaryIO): a file opened for binary reading
            blocksize (int): read block size

        Returns an iterator, yielding samples as they are decoded. After the
        first block of samples is yielded the number of channels and sampling
        rate become available as normal in channel and hz attributes of the
        decoder.
        """
        def fileiter():
            while True:
                block = file.read(blocksize)
                if not block:
                    return
                yield block
        return self.stream(fileiter())


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

        decoder = _native.StreamDecoder()
        samples = np.concatenate([decoder.decode(input), decoder.flush()])
        if samples.size == 0:
            raise DecoderError("No data decoded")
        samples = samples.reshape(-1, decoder.channels).T
        self.samples = samples
        self.channels = decoder.channels
        self.hz = decoder.hz