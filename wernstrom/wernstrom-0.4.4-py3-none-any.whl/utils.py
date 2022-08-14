"""Provides helper methods for loading and parsing KITTI data."""

from collections import namedtuple
from squaternion import Quaternion
import numpy as np
from PIL import Image


# Per dataformat.txt
OxtsPacket = namedtuple('OxtsPacket',
                        'lat, lon, alt, ' +
                        'roll, pitch, yaw, ' +
                        'vn, ve, vf, vl, vu, ' +
                        'ax, ay, az, af, al, au, ' +
                        'wx, wy, wz, wf, wl, wu, ' +
                        'pos_accuracy, vel_accuracy, ' +
                        'navstat, numsats, ' +
                        'posmode, velmode, orimode')

IMU = namedtuple("IMU", "accels gyros euler quaternion")


# Bundle into an easy-to-access structure
OxtsData = namedtuple('OxtsData', 'packet, T_w_imu')


def subselect_files(files, indices):
    try:
        files = [files[i] for i in indices]
    except:
        pass
    return files


def rotx(t):
    """Rotation about the x-axis."""
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[1,  0,  0],
                     [0,  c, -s],
                     [0,  s,  c]])


def roty(t):
    """Rotation about the y-axis."""
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[c,  0,  s],
                     [0,  1,  0],
                     [-s, 0,  c]])


def rotz(t):
    """Rotation about the z-axis."""
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[c, -s,  0],
                     [s,  c,  0],
                     [0,  0,  1]])


def transform_from_rot_trans(R, t):
    """Transforation matrix from rotation matrix and translation vector."""
    R = R.reshape(3, 3)
    t = t.reshape(3, 1)
    return np.vstack((np.hstack([R, t]), [0, 0, 0, 1]))


def read_calib_file(filepath):
    """Read in a calibration file and parse into a dictionary."""
    data = {}

    with open(filepath, 'r') as f:
        for line in f.readlines():
            # print(line)
            try:
                line = line.replace("\n","")
                key, value = line.split(':', 1)
                # The only non-float values in these files are dates, which
                # we don't care about anyway
                try:
                    data[key] = np.array([float(x) for x in value.split()])
                except ValueError:
                    pass
            except:
                vals = line.split(" ")
                # print(vals)
                key = vals[0]
                data[key] = np.array([float(x) for x in vals[1:] if len(x) > 0])

    return data


def pose_from_oxts_packet(packet, scale):
    """Helper method to compute a SE(3) pose matrix from an OXTS packet.
    """
    er = 6378137.  # earth radius (approx.) in meters

    # Use a Mercator projection to get the translation vector
    tx = scale * packet.lon * np.pi * er / 180.
    ty = scale * er * \
        np.log(np.tan((90. + packet.lat) * np.pi / 360.))
    tz = packet.alt
    t = np.array([tx, ty, tz])

    # Use the Euler angles to get the rotation matrix
    Rx = rotx(packet.roll)
    Ry = roty(packet.pitch)
    Rz = rotz(packet.yaw)
    R = Rz.dot(Ry.dot(Rx))

    # Combine the translation and rotation into a homogeneous transform
    return R, t


def load_oxts_packets_and_poses(oxts_files):
    """
    Generator to read OXTS ground truth data.

    Poses are given in an East-North-Up coordinate system
    whose origin is the first GPS position.

    - lat:     latitude of the oxts-unit (deg)
    - lon:     longitude of the oxts-unit (deg)
    - alt:     altitude of the oxts-unit (m)
    - roll:    roll angle (rad),  0 = level, positive = left side up (-pi..pi)
    - pitch:   pitch angle (rad), 0 = level, positive = front down (-pi/2..pi/2)
    - yaw:     heading (rad),     0 = east,  positive = counter clockwise (-pi..pi)
    - vn:      velocity towards north (m/s)
    - ve:      velocity towards east (m/s)
    - vf:      forward velocity, i.e. parallel to earth-surface (m/s)
    - vl:      leftward velocity, i.e. parallel to earth-surface (m/s)
    - vu:      upward velocity, i.e. perpendicular to earth-surface (m/s)
    - ax:      acceleration in x, i.e. in direction of vehicle front (m/s^2)
    - ay:      acceleration in y, i.e. in direction of vehicle left (m/s^2)
    - az:      acceleration in z, i.e. in direction of vehicle top (m/s^2)
    - af:      forward acceleration (m/s^2)
    - al:      leftward acceleration (m/s^2)
    - au:      upward acceleration (m/s^2)
    - wx:      angular rate around x (rad/s)
    - wy:      angular rate around y (rad/s)
    - wz:      angular rate around z (rad/s)
    - wf:      angular rate around forward axis (rad/s)
    - wl:      angular rate around leftward axis (rad/s)
    - wu:      angular rate around upward axis (rad/s)
    - posacc:  velocity accuracy (north/east in m)
    - velacc:  velocity accuracy (north/east in m/s)
    - navstat: navigation status
    - numsats: number of satellites tracked by primary GPS receiver
    - posmode: position mode of primary GPS receiver
    - velmode: velocity mode of primary GPS receiver
    - orimode: orientation mode of primary GPS receiver
    """
    # Scale for Mercator projection (from first lat value)
    scale = None
    # Origin of the global coordinate system (first GPS position)
    origin = None

    oxts = []
    imu = []

    for filename in oxts_files:
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.split()
                # Last five entries are flags and counts
                line[:-5] = [float(x) for x in line[:-5]]
                line[-5:] = [int(float(x)) for x in line[-5:]]

                packet = OxtsPacket(*line)
                sen = IMU(
                    [packet.ax, packet.ay, packet.az],
                    [packet.wx, packet.wy, packet.wz],
                    [packet.roll, packet.pitch, packet.yaw],
                    Quaternion.from_euler(packet.roll, packet.pitch, packet.yaw, degrees=False)
                )
                imu.append(sen)

                if scale is None:
                    scale = np.cos(packet.lat * np.pi / 180.)

                R, t = pose_from_oxts_packet(packet, scale)

                if origin is None:
                    origin = t

                T_w_imu = transform_from_rot_trans(R, t - origin)

                oxts.append(OxtsData(packet, T_w_imu))

    timestamps = np.arange(0, len(imu)*0.1, 0.1)

    return oxts, imu, timestamps

"""
https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
1 (1-bit pixels, black and white, stored with one pixel per byte)

L (8-bit pixels, black and white)

P (8-bit pixels, mapped to any other mode using a color palette)

RGB (3x8-bit pixels, true color)

RGBA (4x8-bit pixels, true color with transparency mask)

CMYK (4x8-bit pixels, color separation)

YCbCr (3x8-bit pixels, color video format)

Note that this refers to the JPEG, and not the ITU-R BT.2020, standard

LAB (3x8-bit pixels, the L*a*b color space)

HSV (3x8-bit pixels, Hue, Saturation, Value color space)

I (32-bit signed integer pixels)

F (32-bit floating point pixels

LA (L with alpha)

PA (P with alpha)

RGBX (true color with padding)

RGBa (true color with premultiplied alpha)

La (L with premultiplied alpha)

I;16 (16-bit unsigned integer pixels)

I;16L (16-bit little endian unsigned integer pixels)

I;16B (16-bit big endian unsigned integer pixels)

I;16N (16-bit native endian unsigned integer pixels)

BGR;15 (15-bit reversed true colour)

BGR;16 (16-bit reversed true colour)

BGR;24 (24-bit reversed true colour)

BGR;32 (32-bit reversed true colour)
"""
def load_image(file, mode):
    """Load an image from file."""
    im = Image.open(file).convert(mode)
    return np.array(im)


def yield_images(imfiles, mode):
    """Generator to read image files."""
    for file in imfiles:
        yield load_image(file, mode)


# def load_velo_scan(file):
#     """Load and parse a velodyne binary file."""
#     scan = np.fromfile(file, dtype=np.float32)
#     return scan.reshape((-1, 4))
#
#
# def yield_velo_scans(velo_files):
#     """Generator to parse velodyne binary files into arrays."""
#     for file in velo_files:
#         yield load_velo_scan(file)
