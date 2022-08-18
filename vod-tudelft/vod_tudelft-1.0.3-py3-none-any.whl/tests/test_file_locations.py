import os

from vod import KittiLocations


def test_kitti_locations_calculated_locations():
    locations = KittiLocations("test")

    assert locations.camera_dir == os.path.join('test', 'lidar', 'training', 'image_2')
    assert locations.lidar_dir == os.path.join('test', 'lidar', 'training', 'velodyne')
    assert locations.lidar_calib_dir == os.path.join('test', 'lidar', 'training', 'calib')
    assert locations.radar_dir == os.path.join('test', 'radar', 'training', 'velodyne')
    assert locations.radar_calib_dir == os.path.join('test', 'radar', 'training', 'calib')
    assert locations.pose_dir == os.path.join('test', 'lidar', 'training', 'pose')
    assert locations.pose_calib_dir == os.path.join('test', 'lidar', 'training', 'calib')
    assert locations.label_dir == os.path.join('test', 'lidar', 'training', 'label_2')


def test_kitti_locations_optional_arguments():
    locations = KittiLocations("")

    assert locations.output_dir is None
    assert locations.frame_set_path is None
    assert locations.pred_dir is None


def test_kitti_locations_given_optional_arguments():
    locations = KittiLocations(root_dir="",
                                   output_dir="output_dir",
                                   frame_set_path="frame_path",
                                   pred_dir="pred_dir")

    assert locations.output_dir == "output_dir"
    assert locations.frame_set_path == "frame_path"
    assert locations.pred_dir == "pred_dir"
