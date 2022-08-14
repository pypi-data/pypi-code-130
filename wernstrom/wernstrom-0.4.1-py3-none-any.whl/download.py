from subprocess import call

def get_data(what):
    """
    You can open a web browser at this url_base and get back an xml
    of all available files
    """
    URL_BASE = "https://s3.eu-central-1.amazonaws.com/avg-kitti/"
    data_avail = ['image_2', 'image_3', 'velodyne', 'calib', 'oxts', 'label_2', 'det_2_lsvm']
    if what in data_avail:
        zip_name = f"data_tracking_{what}.zip"
        url = URL_BASE + zip_name
        print(f"Getting: {url}")
        # call(['wget', url])
    else:
        print("ERROR: Can only get this data:")
        for x in data_avail:
            print(f"   {x}")
