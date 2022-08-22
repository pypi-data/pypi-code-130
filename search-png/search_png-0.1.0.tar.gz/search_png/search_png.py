from PIL import Image
import threading
import os
import binascii
import logging
import math

"""
Scott Blackburn April 4, 2022
sblack777@hotmail.com
"""


class Counter(object):
    rectangle = []

    def __init__(self, rectangle2=None):
        if rectangle2 is None:
            rectangle2 = []
        self.lock = threading.Lock()
        self.rectangle = rectangle2

    def update_value(self, rectangle_found=None):
        """ append the value if not empty """
        logging.debug('Waiting for update value')
        if rectangle_found is None:
            rectangle_found = []
        self.lock.acquire()
        try:
            if len(rectangle_found) > 0:
                self.rectangle.append(rectangle_found)
            logging.debug('Acquired lock for update')
        finally:
            self.lock.release()

    def get_value(self):
        logging.debug('get_value function')
        x = []
        self.lock.acquire()
        logging.debug('get_value acquire lock')
        try:
            logging.debug('Acquired lock')
            x = self.rectangle
        finally:
            self.lock.release()
        return x


def cut_area(test_image, left, top, right, bottom, save_cut_image):
    """
    Cut a region from the image and save new image.  parameters input image,
    left coordinate, top coordinate, right and bottom coordinate and
    the image file to save to.
    """
    test_image = test_image.decode()
    save_cut_image = save_cut_image.decode()
    test = os.path.exists (test_image)
    if not test:
        msg = "ERROR: File " + test_image + " does not exist."
        AssertionError(msg)
        return False
    try:    
        original = Image.open(test_image)
    except BaseException as e:
        return "Error:" + str(e) + " trying to open file: " + test_image
    cut_region = original.crop((left, top, right, bottom))
    try:
        save_cut_image = os.path.abspath(save_cut_image)
        cut_region.save(save_cut_image)
        original.close()
    except BaseException as e:
        pass
    return True


def cut_area_with_list(test_image, cut_area_list, save_cut_image):
    """
    Cut a region from the image and save new image.  parameters input image,
    left coordinate, top coordinate, right and bottom coordinate and
    the image file to save to.
    """
    left = int(cut_area_list[0])
    top = int(cut_area_list[1])
    right = int(cut_area_list[2])
    bottom = int(cut_area_list[3])
    test = os.path.exists (test_image)
    if not test:
        msg = "ERROR: File " + test_image + " does not exist."
        AssertionError(msg)
        return False
    try:    
        original = Image.open(test_image)
    except BaseException as e:
        return "Error:" + str(e) + " trying to open file: " + test_image
    cut_region = original.crop((left, top, right, bottom))
    try:
        save_cut_image = os.path.abspath(save_cut_image)
        cut_region.save(save_cut_image)
        original.close()
    except BaseException as e:
        pass
    return True


def _searchfor_n_number_bitmap_image(tar_list, ti_height, ti_width, sf_height,
                                     sf_width, sf_list, start_row, end_row,
                                     C1, expected_number_images):
    """
    Use in threading - searches just the given rows ... if found will look in adjacent rows even beyond this.
    if the list is empty then found nothing.
    ti_height => target image height
    ti_width => target image width
    sf_height => search within image height
    sf_width => seach winthin image width.
    tar_list => the image we are searching inside.
    sf_list => the image we are searching for
    expected_number_images: is the number of bitmaps to search for.
    """
    list_found = []
    number_found = 0
    for y in range(start_row, end_row):
        if len(list_found) > 0 or number_found == expected_number_images:
            break
        start_x = 0
        for x in range(start_x, ti_width):
            if tar_list[y][x] == sf_list[0][0] and tar_list[y][x:x+sf_width] == sf_list[0]:  # found first row of the item
                for jj in range(1, sf_height):
                    if tar_list[y+jj][x] == sf_list[jj][0] and tar_list[y + jj][x:x + sf_width] == sf_list[jj]:
                        if jj == (sf_height - 1):
                            list_found.append([x, y, (x + sf_width), y + jj])
                            C1.update_value(list_found)
                            number_found = number_found + 1
                            start_x = x + sf_width
                            break
    return list_found


def find_n_number_bitmap_image(target_png, search_for_png, expected_number_images):
    """ Look for search for png inside of target png return the coordinates """
    im_target = Image.open(target_png)
    pix = im_target.load()
    pixels = list(im_target.getdata())
    ti_width, ti_height = im_target.size
    tar_list = [pixels[i * ti_width:(i + 1) * ti_width] for i in range(ti_height)]

    im_search = Image.open(search_for_png)
    pix = im_search.load()
    pixels = list(im_search.getdata())
    sf_width, sf_height = im_search.size
    sf_list = [pixels[i * sf_width:(i + 1) * sf_width] for i in range(sf_height)]

    # Break down the screen into separate rows.
    if ti_height < 32:
        if ti_height > 5:
            rows_per_thread = 5
        else:
            rows_per_thread = 1
    else:
        rows_per_thread = math.ceil(ti_height / 350)

    t = range(0, ti_height, rows_per_thread)
    tsize = len(t) - 1
    list_found = []
    threads = []
    C1 = Counter([])
    for i in range(0, tsize):
        start_row = t[i]
        end_row = t[i+1]
        th = threading.Thread(target=_searchfor_n_number_bitmap_image,
                              args=(tar_list, ti_height, ti_width, sf_height,
                                    sf_width, sf_list, start_row, end_row,
                                    C1, expected_number_images, ))
        threads.append(th)
        th.start()
    for j in threads:
        j.join()
    if len(C1.rectangle) > 0:
        if len(C1.rectangle[0]) > 0:
            if len(C1.rectangle[0][0]) > 0:
                list_found.append (C1.rectangle)  # return just the first one.

    new_list = []
    for x in list_found:
        for subitem in x:
            if type(subitem[0]) is list:
                for subsubitem in subitem:
                    if subsubitem not in new_list:
                        new_list.append(subsubitem)
                        print(subsubitem)
    return new_list


def _searchfor_bitmap_image(tar_list, ti_height, ti_width, sf_height, sf_width, sf_list, start_row, end_row, C1 ):
    """
    Use in threading - searches just the given rows ... if found will look in adjacent rows even beyond this.
    if the list is empty then found nothing.
    """
    list_found = []
    for y in range(start_row, end_row):
        if len(list_found) > 0:
            break
        for x in range(0, ti_width):
            if tar_list[y][x] == sf_list[0][0] and tar_list[y][x:x+sf_width] == sf_list[0]:
                for jj in range (1, sf_height):
                    if tar_list[y+jj][x] == sf_list[jj][0] and tar_list[y + jj][x:x + sf_width] == sf_list[jj]:
                        if jj == (sf_height - 1):
                            list_found.append([x, y, (x + sf_width - 1), y + jj])
                            break
                    else:
                        break                    
    C1.update_value(list_found)
    return list_found


def find_bitmap_image(target_png, search_for_png):
    """ Look for search for png inside of target png return the coordinates """
    im_target = Image.open(target_png)
    pix = im_target.load()
    pixels = list(im_target.getdata())
    ti_width, ti_height = im_target.size
    tar_list = [pixels[i * ti_width:(i + 1) * ti_width] for i in range(ti_height)]

    im_search = Image.open(search_for_png)
    pix = im_search.load()
    pixels = list(im_search.getdata())
    sf_width, sf_height = im_search.size
    sf_list = [pixels[i * sf_width:(i + 1) * sf_width] for i in range(sf_height)]

    # Break down the screen into separate rows.
    if ti_height < 32:
        if ti_height > 5:
            rows_per_thread = 5
        else:
            rows_per_thread = 1
    else:
        rows_per_thread = math.ceil(ti_height / 20)

    t = range(0, ti_height, rows_per_thread)
    tsize = len(t) - 1
    list_found = []
    threads = []
    C1 = Counter([])
    for i in range(0, tsize):
        start_row = t[i]
        end_row = t[i+1]
        #_searchfor_bitmap_image(tar_list, ti_height, ti_width, sf_height, sf_width,
        #                                 sf_list, 0, 1463, C1,)
        th = threading.Thread(target=_searchfor_bitmap_image, args=(tar_list, ti_height, ti_width, sf_height, sf_width,
                                                                    sf_list, start_row, end_row, C1,))
        threads.append(th)
        th.start()
    for j in threads:
        j.join()
    if len(C1.rectangle) > 0:
        if len(C1.rectangle[0]) > 0:
            if len(C1.rectangle[0][0]) > 0:
                list_found = C1.rectangle[0][0]  # return just the first one.
    return list_found


def crc32_compare_image_files(filename_baseline, filename_actual):
    """ Provide the complete path to both filenames - actual and baseline. """
    # Check if the files exist.
    if not os.path.exists(filename_baseline):
        msg = "ERROR: File " + filename_actual + " does not exist."
        AssertionError(msg)
    if not os.path.exists(filename_actual):
        msg = "ERROR: File " + filename_actual + " does not exist."
        AssertionError(msg)
    try:
        base = open(filename_baseline, 'rb').read()
        base = (binascii.crc32(base) & 0xFFFFFFFF)
        actual = open(filename_actual, 'rb').read()
        actual = (binascii.crc32(actual) & 0xFFFFFFFF)
        if base == actual:
            return True
        else:
            return False
    except BaseException as e:
        AssertionError(str(e))
        return False


def get_height_and_width (image_filename):
    """ Get the height and width of an image. """
    # Check if the file exists.
    if not os.path.exists(image_filename):
        msg = "ERROR: File " + image_filename + " does not exist."
        AssertionError(msg)
    try:
        im = Image.open(image_filename)
        return [im.size[0], im.size[1], im.format, im.format_description, im.mode]
    except BaseException as e:
        return list(str(e))


def get_center_rectangle(rectangle):
    """ input rectangle return list with center coordinate """
    if len(rectangle) != 4:
        print("Error must have 4 elements to have a rectangle. Should be in list such as: [left, top, right, bottom]")
        return [0, 0]
    else:
        tr_x, tr_y, bl_x, bl_y = rectangle
        tr_x = int(tr_x)
        tr_y = int(tr_y)
        bl_x = int(bl_x)
        bl_y = int(bl_y)
        x = int((bl_x + tr_x) / 2)
        y = int((tr_y + bl_y) / 2)
        return [x, y]
