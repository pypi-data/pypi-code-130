import numpy as np
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from copy import copy, deepcopy
import numba

def get_corners(bbox, ret_center=False):
    '''
    bbox format: [x,y,z,l,w,h,yaw]
    coordinate frame:
    +z
    |
    |
    ----- +y
    \
     \
      +x

    Corner numbering::
         5------4
         |\     |\
         | \    | \
         6--\---7  \
          \  \   \  \
     l     \  1------0    h
      e     \ |    \ |    e
       n     \|     \|    i
        g     2------3    g
         t      width     h
          h               t

    First four corners are the ones facing front.
    The last four are the ones facing back.
    '''
    l, w, h = bbox[3:6]
    #                      front           back
    xs = l/2 * np.array([1, 1, 1, 1] + [-1,-1,-1,-1])
    ys = w/2 * np.array([1,-1,-1, 1] * 2)
    zs = h/2 * np.array([1, 1,-1,-1] * 2)
    pts = np.vstack([xs, ys, zs])       # (3, 8)

    center = bbox[:3]
    yaw = bbox[6]
    R = Rotation.from_euler('z', yaw).as_matrix()   # (3, 3)
    pts = (R @ pts).T + center
    if ret_center == True:
        return pts, center
    return pts

def get_visual_lines(bbox, color='r', width=1):
    from vispy.scene import visuals

    pts = get_corners(bbox)
    connect = np.array([
        [0, 1], [1, 2], [2, 3], [3, 0],  # front
        [4, 5], [5, 6], [6, 7], [7, 4],  # back
        [0, 4], [1, 5], [2, 6], [3, 7],  # side
        [0, 2], [1, 3], # front cross
    ])
    lines = visuals.Line(pos=pts, connect=connect, color=color, width=width,
                         antialias=True, method='gl')
    return lines

def get_visual_arrows(bbox, color='g', width=1):
    from vispy.scene import visuals
    center = bbox[:3]
    pts = get_corners(bbox)
    front_center = (pts[0] + pts[1]) / 2
    connect = np.array([
        [0, 1], [1, 2], [2, 3], [3, 0],  # front
        [4, 5], [5, 6], [6, 7], [7, 4],  # back
        [0, 4], [1, 5], [2, 6], [3, 7],  # side
        [0, 2], [1, 3], # front cross
    ])
    return visuals.Line.arrow.ArrowVisual(pos=pts, connect=connect, color=color, width=width, 
                        method='gl', antialias=True)

def points_in_bbox(bbox, points, only_mask=True):
    """
    Checks whether points are inside the box.
    adapted from: https://github.com/nutonomy/nuscenes-devkit/blob/05d05b3c994fb3c17b6643016d9f622a001c7275/python-sdk/nuscenes/utils/geometry_utils.py#L111

    Args:
        points: (n, 3)
    """
    corners = get_corners(bbox)
    
    p1 = corners[0]
    p_x = corners[4]
    p_y = corners[1]
    p_z = corners[3]

    i = p_x - p1
    j = p_y - p1
    k = p_z - p1

    points_c = points.copy()
    v = (points_c[:, :3] - p1).T # (3, n)

    iv = np.dot(i, v)
    jv = np.dot(j, v)
    kv = np.dot(k, v)

    mask_x = np.logical_and(0 <= iv, iv <= np.dot(i, i))
    mask_y = np.logical_and(0 <= jv, jv <= np.dot(j, j))
    mask_z = np.logical_and(0 <= kv, kv <= np.dot(k, k))
    mask = np.logical_and(np.logical_and(mask_x, mask_y), mask_z)

    if only_mask:
        return mask
    else:
        return points_c[mask]

@numba.njit
def downsample(points, voxel_size=0.05):
    sample_dict = dict()
    for i in range(points.shape[0]):
        point_coord = np.floor(points[i] / voxel_size)
        sample_dict[(int(point_coord[0]), int(point_coord[1]), int(point_coord[2]))] = True
    res = np.zeros((len(sample_dict), 3), dtype=np.float32)
    idx = 0
    for k, v in sample_dict.items():
        res[idx, 0] = k[0] * voxel_size + voxel_size / 2
        res[idx, 1] = k[1] * voxel_size + voxel_size / 2
        res[idx, 2] = k[2] * voxel_size + voxel_size / 2
        idx += 1
    return res

def pca(points):
    '''
    Args
    -----
        points: np.ndarray, shape (N, 3)
    Return
    ------
        mu, covariance, eigen_value, eigen_vector
    '''
    pts_num = points.shape[0]
    mu = np.mean(points, axis=0)
    normalized_points = points - mu
    covariance = (1/pts_num - 1) * normalized_points.T @ normalized_points
    eigen_vals, eigen_vec = np.linalg.eig(covariance)
    return mu, covariance, eigen_vals, eigen_vec