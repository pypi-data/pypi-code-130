import os
import SimpleITK as sitk
import nibabel as nib
from typing import Tuple
import numpy as np


def resample_volume(volume_path: str,
                    new_spacing: list,
                    out_path: str,
                    interpolator: int = sitk.sitkLinear) -> Tuple[sitk.Image, nib.Nifti1Image, np.ndarray]:
    """This function resamples the input volume to a specified voxel spacing
    Args:
        volume_path (str): input volume path
        new_spacing (list): desired voxel spacing that we want
        out_path (str): path where we temporarily save the resampled output volume
        interpolator (int): interpolator that we want to use (e.g. 1= NearNeigh., 2=linear, ...)
    Returns:
        resampled_volume_sitk_obj: resampled volume as sitk object
        resampled_volume_nii_obj: resampled volume as nib object
        resampled_volume_nii: resampled volume as numpy array
    """
    volume = sitk.ReadImage(volume_path)  # read volume
    original_size = volume.GetSize()  # extract size
    original_spacing = volume.GetSpacing()  # extract spacing
    new_size = [int(round(osz * ospc / nspc)) for osz, ospc, nspc in zip(original_size, original_spacing, new_spacing)]
    resampled_volume_sitk_obj = sitk.Resample(volume, new_size, sitk.Transform(), interpolator,
                                              volume.GetOrigin(), new_spacing, volume.GetDirection(), 0,
                                              volume.GetPixelID())
    sitk.WriteImage(resampled_volume_sitk_obj, out_path)  # write sitk volume object to disk
    resampled_volume_nii_obj = nib.load(out_path)  # type: nib.Nifti1Image # load volume as nibabel object
    resampled_volume_nii = np.asanyarray(resampled_volume_nii_obj.dataobj)  # type: np.ndarray # convert from nibabel object to np.array
    os.remove(out_path)  # remove volume from disk to save space

    return resampled_volume_sitk_obj, resampled_volume_nii_obj, resampled_volume_nii


def remove_zeros_ijk_from_volume(input_volume: np.ndarray) -> np.ndarray:
    """This function removes all the rows, columns and slices of the input volume that only contain zero values.
    Args:
        input_volume: volume from which we want to remove zeros
    Returns:
        cropped_volume: cropped volume (i.e. input volume with zeros removed)
    """

    def remove_zeros_one_coordinate(input_volume_: np.ndarray, range_spatial_dim: int, spatial_dim: int):
        idxs_nonzero_slices = []  # will the contain the indexes of all the slices that have nonzero values
        for idx in range(range_spatial_dim):  # loop over coordinate
            if spatial_dim == 0:
                one_slice = input_volume_[idx, :, :]
            elif spatial_dim == 1:
                one_slice = input_volume_[:, idx, :]
            elif spatial_dim == 2:
                one_slice = input_volume_[:, :, idx]
            else:
                raise ValueError("spatial_dim can only be 0, 1, or 2. Got {} instead".format(spatial_dim))

            if np.count_nonzero(one_slice) > 0:  # if the slice has some nonzero values
                idxs_nonzero_slices.append(idx)  # save slice index

        # retain only indexes with nonzero values from the two input volumes
        if spatial_dim == 0:
            cropped_volume_ = input_volume_[idxs_nonzero_slices, :, :]
        elif spatial_dim == 1:
            cropped_volume_ = input_volume_[:, idxs_nonzero_slices, :]
        elif spatial_dim == 2:
            cropped_volume_ = input_volume_[:, :, idxs_nonzero_slices]
        else:
            raise ValueError("spatial_dim can only be 0, 1, or 2. Got {} instead".format(spatial_dim))

        return cropped_volume_

    assert len(input_volume.shape) == 3, "The input volume must be 3D"

    # i coordinate
    cropped_volume = remove_zeros_one_coordinate(input_volume, input_volume.shape[0], spatial_dim=0)
    # j coordinate
    cropped_volume = remove_zeros_one_coordinate(cropped_volume, input_volume.shape[1], spatial_dim=1)
    # k coordinate
    cropped_volume = remove_zeros_one_coordinate(cropped_volume, input_volume.shape[2], spatial_dim=2)

    return cropped_volume


def get_axes_orientations_with_nibabel(input_nifti_volume: nib.Nifti1Image) -> tuple:
    """This function returns the axes orientations as a tuple
    Args:
        input_nifti_volume: the input volume for which we want the axes orientations
    Returns:
        orientations: the axes orientations
    """
    aff_mat = input_nifti_volume.affine  # type: np.ndarray # extract affine matrix
    orientations = nib.aff2axcodes(aff_mat)

    return orientations


def get_nibabel_header(input_nifti_volume: nib.Nifti1Image,
                       print_header: bool = False) -> nib.nifti1.Nifti1Header:
    """This function returns the header of the nifti image/volume
    Args:
        input_nifti_volume: the input volume for which we want the header
        print_header: whether to print the header or not; defaults to False
    Returns:
        header (nib.nifti1.Nifti1Header): the axes orientations
    """
    header = input_nifti_volume.header
    if print_header:
        print(header)

    return header


def read_dcm_series(dcm_dir: str) -> sitk.Image:
    """This function reads a dicom series with SimpleITK
    Args:
        dcm_dir: directory where dicom files are stored
    Returns:
        volume_sitk: volume loaded as sitk.Image
    """
    reader = sitk.ImageSeriesReader()  # create reader
    dicom_names = reader.GetGDCMSeriesFileNames(dcm_dir)  # read dicom series
    reader.SetFileNames(dicom_names)

    volume_sitk = reader.Execute()  # extract sitk.Image

    return volume_sitk


def get_sitk_volume_info(path_to_nii_or_dcm: str, print_info: bool = False) -> dict:
    """This function prints basic info of the input volume
    Args:
        path_to_nii_or_dcm: path to volume that we want to explore
        print_info: whether to print the volume info or no; defaults to False
    Returns:
        volume_info: it contains all the main volume information
    """
    if os.path.isdir(path_to_nii_or_dcm):  # if path_to_nii_or_dcm is a directory
        volume_sitk = read_dcm_series(path_to_nii_or_dcm)
    else:  # if instead path_to_nii_or_dcm is a file
        volume_sitk = sitk.ReadImage(path_to_nii_or_dcm)  # read as sitk Image

    volume_info = {"dimensions": volume_sitk.GetDimension(),
                   "size": volume_sitk.GetSize(),
                   "origin": volume_sitk.GetOrigin(),
                   "spacing": volume_sitk.GetSpacing(),
                   "direction": volume_sitk.GetDirection(),
                   "nb_components_per_pixel": volume_sitk.GetNumberOfComponentsPerPixel(),
                   "pixel_type": volume_sitk.GetPixelID(),
                   "pixel_id_type_as_string": volume_sitk.GetPixelIDTypeAsString(),
                   "pixel_id_value": volume_sitk.GetPixelIDValue()
                   }

    if print_info:
        print("Dimensions: {}".format(volume_sitk.GetDimension()))
        print("Size: {}".format(volume_sitk.GetSize()))
        print("Origin: {}".format(volume_sitk.GetOrigin()))
        print("Spacing: {}".format(volume_sitk.GetSpacing()))
        print("Direction cosine matrix: {}".format(volume_sitk.GetDirection()))
        print("Nb. components per pixel {}".format(volume_sitk.GetNumberOfComponentsPerPixel()))
        print("Pixel type: {}".format(volume_sitk.GetPixelID()))
        print("Pixel ID type as string: {}".format(volume_sitk.GetPixelIDTypeAsString()))
        print("Pixel ID value: {}".format(volume_sitk.GetPixelIDValue()))

    return volume_info
