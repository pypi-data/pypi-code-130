import numpy as np
import plyfile
from typing import List, Tuple

def read_3d_point_cloud_from_ply(ply_file_path: str) -> Tuple[np.ndarray, List[str]]:
    """Read a 3D point cloud from a ply file and return a numpy array.

    Parameters
    ----------
        ply_file_path -- path to a .ply file

    Returns
    -------
        Tuple(NDArray, comments)
        -- array: numpy array with the list of 3D points, one point per line
        -- comments: list of strings with the ply header comments
    """
    plydata = plyfile.PlyData.read(ply_file_path)
    d = np.asarray(plydata["vertex"].data)
    array = np.column_stack([d[p.name] for p in plydata["vertex"].properties])
    return array, plydata.comments