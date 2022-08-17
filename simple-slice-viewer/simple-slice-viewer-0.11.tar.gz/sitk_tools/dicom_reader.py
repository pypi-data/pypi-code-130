import SimpleITK as sitk
import pydicom
import os
import numpy as np
import sitk_tools

SUV_SCALE_FACTOR = 'SUVScaleFactor'

def sort_files_by_slice_position(files):
    
    reader = sitk.ImageFileReader()
    
    origins = []
    for file in files:    
        reader.SetFileName(file)
        reader.ReadImageInformation()
        origins += [reader.GetOrigin()]
        
    direction = reader.GetDirection()
    
    
    slice_dir = np.asarray(direction[-3:])
    
    distances =  []
    for index, origin in enumerate(origins):
        distance_slice_dir = sum([i*j for i, j in zip(slice_dir, origin)])
        distances += [distance_slice_dir]
    
    order = [i for (v, i) in sorted((v, i) for (i, v) in enumerate(distances))]
    files = [files[i] for i in order]
    return files, order
    


def get_series_instance_uids(files):
    folders = set()
    for file in files:
        folders.add(os.path.split(file)[0])

    reader = sitk.ImageSeriesReader()

    ids = []
    reader.SetGlobalWarningDisplay(False)
    for folder in folders:
        if folder == '':
            folder = '.'
        ids += list(reader.GetGDCMSeriesIDs(folder))

    reader.SetGlobalWarningDisplay(True)

    return ids

def get_tag_from_file(file, tag, reader=None):
    tag = tagname_to_sitk_tag(tag)
    
    if reader is None:
        reader = sitk.ImageFileReader()
    
    if isinstance(file, (list, tuple)):
        return [get_tag_from_file(fi, tag, reader=reader) for fi in file]
    
    reader.SetFileName(file)
    reader.ReadImageInformation()
    value = reader.GetMetaData(tag)
    
    try:
        value = float(value)
    except ValueError:
        pass
    
    return value

def tagname_to_sitk_tag(tagname):
    if len(tagname) == 9 and tagname[4] == '|':
        return tagname
    
    tagnumber=pydicom.datadict.tag_for_keyword(tagname)
    tag = pydicom.tag.Tag(tagnumber)
    
    group = str(hex(tag.group)).split('0x')[1]
    element = str(hex(tag.element)).split('0x')[1]
    
    group = group.rjust(4, '0')
    element = element.rjust(4, '0')
    
    sitk_tag = group + '|' + element
    return sitk_tag

def validate_series_instance_uid(files):
    series_instance_uids = get_series_instance_uids(files)
    
    if len(series_instance_uids) == 0:
        raise IOError('No dicom files found!')
    elif len(series_instance_uids) > 1:
        raise IOError('Multiple Dicom Series Found!')
        

def read_folder(folder, SUV=False, frame_tag=None, recursive=False):
    reader = sitk.ImageSeriesReader()
    files  = reader.GetGDCMSeriesFileNames(folder, recursive=recursive)
    return read_files(files, SUV=SUV)


def read_frames_from_folder(folder, SUV=False, frame_tag=None, recursive=False):
    reader = sitk.ImageSeriesReader()
    files  = reader.GetGDCMSeriesFileNames(folder, recursive=recursive)
    return read_frames_from_files(files, SUV=SUV, frame_tag=frame_tag)
        
def read_frames_from_files(files, SUV=None, frame_tagname=None):
    if frame_tagname is None:
        return read_files(files, SUV=SUV)
    
    sitk_tag = tagname_to_sitk_tag(frame_tagname)
    tag_values = get_tag_from_file(files, sitk_tag)
    
    split = {}
    for file, tag_value in zip(files, tag_values):
        if tag_value not in split.keys():
            split[tag_value] = []
        split[tag_value] += [file]
        
    frames = {}
    for tag_value, fns in split.items():
        frames[tag_value] = read_files(fns, SUV=SUV)

    return frames


def read_files(files, SUV=False):
    validate_series_instance_uid(files)
    
    reader = sitk.ImageSeriesReader()

    files, _ = sort_files_by_slice_position(files)
    
    reader.SetFileNames(files)
    image = reader.Execute()
    
    modality = get_tag_from_file(files[0], '0008|0060')
    if SUV and modality in ('PT', 'NM'):
       header = pydicom.read_file(files[0], stop_before_pixels=True)       
       suv_factor = sitk_tools.suv.suv_scale_factor(header)
       image *= suv_factor

    return image



def read_file(file, SUV=False):
    reader = sitk.ImageFileReader()
    reader.SetFileName(file)
    image = reader.Execute()

    modality = get_tag_from_file(file, '0008|0060')
    if SUV and modality in ('PT', 'NM'):
       header = pydicom.read_file(file, stop_before_pixels=True)       
       suv_factor = sitk_tools.suv.suv_scale_factor(header)
       image *= suv_factor
    

    return image
    






    


