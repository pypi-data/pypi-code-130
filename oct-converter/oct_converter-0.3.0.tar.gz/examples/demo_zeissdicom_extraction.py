from oct_converter.readers import ZEISSDICOM, Dicom

filepath = "/Users/mark/Downloads/03984 MANNERS James/12716/OPT Glaucoma OU Analysis-2/OP000000.dcm"
filepath = "/Users/mark/Downloads/03984 MANNERS James/12716/OPT ONH Angiography 4.5x4.5 mm-3/OP000000.dcm"
filepath = "/Users/mark/Downloads/03984 MANNERS James/12716/OPT Optic Disc Cube 200x200/OP000000.dcm"
filepath = "/Users/mark/Downloads/03984 MANNERS James/12716/OPT Macular Cube 512x128-2/OP000000.dcm"

img = ZEISSDICOM(filepath)
#img = Dicom(filepath)

oct_volume = (
    img.read_oct_volume()
)  # returns an OCT volume with additional metadata if available
oct_volume.peek()  # plots a montage of the volume
oct_volume.save("img_testing.avi")  # save volume
