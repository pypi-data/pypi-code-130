from typing import Annotated, Dict, List, Literal, Tuple, Union
import numpy as np
import pyproj
import rasterio
from rpc_file_readers import read_rpc_file

def apply_poly(poly: Annotated[List[float], 20], x: List[float], y: List[float], z: List[float]):
    """Evaluates a 3-variables polynom of degree 3 on a triplet of numbers.

    Parameters
    ----------
        poly: list of the 20 coefficients of the 3-variate degree 3 polynom,
            ordered following the RPC convention.
        x, y, z: triplet of floats. They may be numpy arrays of same length.

    Returns
    -------
        the value(s) of the polynom on the input point(s).
    """
    out = 0
    out += poly[0]
    out += poly[1]*y + poly[2]*x + poly[3]*z
    out += poly[4]*y*x + poly[5]*y*z +poly[6]*x*z
    out += poly[7]*y*y + poly[8]*x*x + poly[9]*z*z
    out += poly[10]*x*y*z
    out += poly[11]*y*y*y
    out += poly[12]*y*x*x + poly[13]*y*z*z + poly[14]*y*y*x
    out += poly[15]*x*x*x
    out += poly[16]*x*z*z + poly[17]*y*y*z + poly[18]*x*x*z
    out += poly[19]*z*z*z
    return out


def apply_rfm(num: Annotated[List[float], 20], den: Annotated[List[float], 20], x: List[float], y: List[float], z: List[float]):
    """Evaluates a Rational Function Model (rfm), on a triplet of numbers.

    Parameters
    ----------
        num: list of the 20 coefficients of the numerator
        den: list of the 20 coefficients of the denominator
            All these coefficients are ordered following the RPC convention.
        x, y, z: triplet of floats. They may be numpy arrays of same length.

    Returns
    -------
        the value(s) of the rfm on the input point(s).
    """
    return apply_poly(num, x, y, z) / apply_poly(den, x, y, z)

class RPCModel:
    def __init__(self, d: Dict[str, str], dict_format: Literal['rpcm', 'geotiff'] ="geotiff"):
        """
        Parameters
        ----------
            d -- dictionary read from a geotiff file with
                rasterio.open('/path/to/file.tiff', 'r').tags(ns='RPC'),
                or from the .__dict__ of an RPCModel object.
            dict_format -- format of the dictionary passed in `d`.
                Either "geotiff" if read from the tags of a geotiff file,
                or "rpcm" if read from the .__dict__ of an RPCModel object.
        """
        if dict_format == "geotiff":
            self.row_offset = float(d['LINE_OFF'])
            self.col_offset = float(d['SAMP_OFF'])
            self.lat_offset = float(d['LAT_OFF'])
            self.lon_offset = float(d['LONG_OFF'])
            self.alt_offset = float(d['HEIGHT_OFF'])

            self.row_scale = float(d['LINE_SCALE'])
            self.col_scale = float(d['SAMP_SCALE'])
            self.lat_scale = float(d['LAT_SCALE'])
            self.lon_scale = float(d['LONG_SCALE'])
            self.alt_scale = float(d['HEIGHT_SCALE'])

            self.row_num = list(map(float, d['LINE_NUM_COEFF'].split()))
            self.row_den = list(map(float, d['LINE_DEN_COEFF'].split()))
            self.col_num = list(map(float, d['SAMP_NUM_COEFF'].split()))
            self.col_den = list(map(float, d['SAMP_DEN_COEFF'].split()))

            if 'LON_NUM_COEFF' in d:
                self.lon_num = list(map(float, d['LON_NUM_COEFF'].split()))
                self.lon_den = list(map(float, d['LON_DEN_COEFF'].split()))
                self.lat_num = list(map(float, d['LAT_NUM_COEFF'].split()))
                self.lat_den = list(map(float, d['LAT_DEN_COEFF'].split()))

        elif dict_format == "rpcm":
            self.__dict__ = d

        else:
            raise ValueError(
                "dict_format '{}' not supported. "
                "Should be {{'geotiff','rpcm'}}".format(dict_format)
            )

    def projection(self, lon: Union[float, List[float]], lat: Union[float, List[float]], alt: Union[float, List[float]]) -> Tuple[Union[float, List[float]], Union[float, List[float]]]:
        """Convert geographic coordinates of 3D points into image coordinates.

        Parameters
        ----------
            lon -- longitude(s) of the input 3D point(s)
            lat -- latitude(s) of the input 3D point(s)
            alt -- altitude(s) of the input 3D point(s)

        Returns
        -------
            col -- horizontal image coordinate(s) (column index, ie x)
            row -- vertical image coordinate(s) (row index, ie y)
        """
        nlon = (np.asarray(lon) - self.lon_offset) / self.lon_scale
        nlat = (np.asarray(lat) - self.lat_offset) / self.lat_scale
        nalt = (np.asarray(alt) - self.alt_offset) / self.alt_scale

        col = apply_rfm(self.col_num, self.col_den, nlat, nlon, nalt)
        row = apply_rfm(self.row_num, self.row_den, nlat, nlon, nalt)

        col = col * self.col_scale + self.col_offset
        row = row * self.row_scale + self.row_offset

        return col, row

    def write_to_file(self, path: str) -> None:
        """Write RPC coefficients to a txt file in IKONOS txt format.

        Parameters
        ----------
            path (str): path to the output txt file
        """
        with open(path, 'w') as f:

            # scale and offset
            f.write('LINE_OFF: {:.12f} pixels\n'.format(self.row_offset))
            f.write('SAMP_OFF: {:.12f} pixels\n'.format(self.col_offset))
            f.write('LAT_OFF: {:.12f} degrees\n'.format(self.lat_offset))
            f.write('LONG_OFF: {:.12f} degrees\n'.format(self.lon_offset))
            f.write('HEIGHT_OFF: {:.12f} meters\n'.format(self.alt_offset))
            f.write('LINE_SCALE: {:.12f} pixels\n'.format(self.row_scale))
            f.write('SAMP_SCALE: {:.12f} pixels\n'.format(self.col_scale))
            f.write('LAT_SCALE: {:.12f} degrees\n'.format(self.lat_scale))
            f.write('LONG_SCALE: {:.12f} degrees\n'.format(self.lon_scale))
            f.write('HEIGHT_SCALE: {:.12f} meters\n'.format(self.alt_scale))

            # projection function coefficients
            for i in range(20):
                f.write('LINE_NUM_COEFF_{:d}: {:.12f}\n'.format(i+1, self.row_num[i]))
            for i in range(20):
                f.write('LINE_DEN_COEFF_{:d}: {:.12f}\n'.format(i+1, self.row_den[i]))
            for i in range(20):
                f.write('SAMP_NUM_COEFF_{:d}: {:.12f}\n'.format(i+1, self.col_num[i]))
            for i in range(20):
                f.write('SAMP_DEN_COEFF_{:d}: {:.12f}\n'.format(i+1, self.col_den[i]))


def rpc_from_geotiff(geotiff_path: str) -> RPCModel:
    """Read the RPC coefficients from a GeoTIFF file and return an RPCModel object.

    Parameters
    ----------
        geotiff_path -- path or url to a GeoTIFF file

    Returns
    -------
        instance of the rpc_model.RPCModel class
    """
    with rasterio.open(geotiff_path, 'r') as src:
        rpc_dict = src.tags(ns='RPC')
    return RPCModel(rpc_dict)


def rpc_from_rpc_file(rpc_file_path: str) -> RPCModel:
    """=Read the RPC coefficients from a sidecar XML or TXT file and return an RPCModel object.

    Parameters
    ----------
        rpc_file_path -- path to an XML or TXT RPC file

    Returns
    -------
        instance of the rpc_model.RPCModel class
    """
    return RPCModel(read_rpc_file(rpc_file_path))