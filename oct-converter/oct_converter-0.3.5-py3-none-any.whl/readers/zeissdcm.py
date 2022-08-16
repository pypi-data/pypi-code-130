from pathlib import Path
import math
import numpy as np

from oct_converter.image_types import OCTVolumeWithMetaData


class ZEISSDICOM(object):
    """Class for extracting data from Zeiss's .dcm file format.

    Attributes:
        filepath (str): Path to .img file for reading.
    """

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(self.filepath)

    def read_oct_volume(self, interlaced=False):
        """Reads OCT data.

        """
        import pydicom
        from pydicom.encaps import generate_pixel_data_frame
        from pydicom.uid import JPEG2000Lossless

        ds = pydicom.dcmread(self.filepath)
        meta = ds.file_meta
        a=np.array(ds[0x0407, 0x10a0][0][0x0407, 0x1005][0][0x0407, 0x1006].value,dtype=np.uint16)
        b = np.volume = np.frombuffer(
            a.read(105526), dtype=np.uint8
        )
        # if meta.TransferSyntaxUID != JPEG2000Lossless:
        #     raise ValueError(
        #         "Only DICOM datasets with a 'Transfer Syntax UID' of JPEG 2000 "
        #         "(Lossless) are supported"
        #     )

        if not ds.Manufacturer.startswith("Carl Zeiss Meditec"):
            raise ValueError("Only CZM DICOM datasets are supported")

        if "PixelData" not in ds:
            raise ValueError("No 'Pixel Data' found in the DICOM dataset")

        # Iterate through the frames, unscramble and write to file
        if "NumberOfFrames" in ds:
            # Workaround horrible non-conformance in datasets :(
            if isinstance(ds.NumberOfFrames, str):
                nr_frames = ds.NumberOfFrames.split('\0')[0]
            else:
                nr_frames = ds.NumberOfFrames

            frames = generate_pixel_data_frame(ds.PixelData, int(nr_frames))
            for idx, frame in enumerate(frames):
                with open(f"{p.stem}_{idx:>03}.jp2", "wb") as f:
                    f.write(self.unscramble_czm(frame))
        else:
            # CZM is non-conformant for single frames :(
            with open(f"{p.stem}.jp2", "wb") as f:
                f.write(self.unscramble_czm(ds.PixelData))

    def unscramble_czm(self, frame: bytes) -> bytearray:
        """Return an unscrambled image frame.

        Parameters
        ----------
        frame : bytes
            The scrambled CZM JPEG 2000 data frame as found in the DICOM dataset.

        Returns
        -------
        bytearray
            The unscrambled JPEG 2000 data.
        """
        # Fix the 0x5A XORing
        frame = bytearray(frame)
        for ii in range(0, len(frame), 7):
            frame[ii] = frame[ii] ^ 0x5A

        # Offset to the start of the JP2 header - empirically determined
        jp2_offset = math.floor(len(frame) / 5 * 3)

        # Double check that our empirically determined jp2_offset is correct
        offset = frame.find(b"\x00\x00\x00\x0C")
        if offset == -1:
            raise ValueError("No JP2 header found in the scrambled pixel data")

        if jp2_offset != offset:
            print(
                f"JP2 header found at offset {offset} rather than the expected "
                f"{jp2_offset}"
            )
            jp2_offset = offset

        d = bytearray()
        d.extend(frame[jp2_offset:jp2_offset + 253])
        d.extend(frame[993:1016])
        d.extend(frame[276:763])
        d.extend(frame[23:276])
        d.extend(frame[1016:jp2_offset])
        d.extend(frame[:23])
        d.extend(frame[763:993])
        d.extend(frame[jp2_offset + 253:])

        assert len(d) == len(frame)

        return d
