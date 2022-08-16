import numpy as np
import rasterio
import srtm4
from typing import List, Tuple, Union
import warnings
from rpc_model import rpc_from_geotiff

warnings.filterwarnings("ignore",
    category=rasterio.errors.NotGeoreferencedWarning)

def projection(img_path: str, lon: Union[float, List[float]], lat: Union[float, List[float]], z: Union[float, List[float], None]=None, crop_path: Union[str, None]=None, svg_path: Union[str, None]=None,
               verbose=False) -> Tuple[Union[float, List[float]], Union[float, List[float]]]:
    """Conversion of geographic coordinates to image coordinates.

    Parameters
    ----------
        img_path -- path or url to a GeoTIFF image with RPC metadata
        lon -- longitude(s) of the input points
        lat -- latitude(s) of the input points
        z -- altitude(s) of the input points
        crop_path -- path or url to an image crop produced by rpcm.
            Projected image coordinates are computed wrt this crop.
        svg_path -- path to an svg file where to plot the projected image
            point(s)

    Returns
    -------
        x -- pixel coordinate(s) of the projected point(s)
        y -- pixel coordinate(s) of the projected point(s)
    """
    rpc = rpc_from_geotiff(img_path)
    if z is None:
        z = srtm4.srtm4(lon, lat)

    x, y = rpc.projection(lon, lat, z)

    if crop_path:  # load and apply crop transformation matrix
        with rasterio.open(crop_path, 'r') as src:
            tags = src.tags()

        C = list(map(float, tags['CROP_TRANSFORM'].split()))
        C = np.array(C).reshape(3, 3)
        h = np.row_stack((x, y, x**0))  # homogeneous coordinates
        x, y = np.dot(C, h).squeeze()[:2]

    if svg_path:  #TODO
        pass

    if verbose:
        for p in zip(np.atleast_1d(x), np.atleast_1d(y)):
            print('{:.4f} {:.4f}'.format(*p))

    return x, y
