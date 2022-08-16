from oct_converter.readers import E2E
from construct import Array, Int8un, Int16un, Int32sn, Int32un, PaddedString, Struct

filepaths = [
            {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT001.E2E",
                'start': 36897},
             {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
                'start': 29565},
            {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/new-e2e-11-06-2022/TIN0901T.E2E",
                'start': 29756},
             {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/new-e2e-11-06-2022/TIN0902T.E2E",
            'start':644526}
]
# filepaths = [
#              {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 29565},
#     {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 2411365},
# {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 4793222},
# {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 9572863},
# {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 10607977},
# {'path':"/Users/mark/Library/CloudStorage/Dropbox/Work/Projects/OCT-Converter/my_example_volumes/e2e-vassily/PatientIDTIN0007-ADAMIDIS/DIMIT002.E2E",
#                 'start': 11643268}
#
# ]
import pandas as pd
headers_list= []
for skip in range(2,3):
    for f in filepaths:
        filepath = f['path']
        start = f['start']
        with open(filepath, "rb") as f:
            f.seek(start+skip)
            raw = f.read(32 * 35)
            header_structure = Struct(
                # "magic1" / Int32un,
                # "version" / PaddedString(10,'ascii'),
                "unknown" / Array(35, Int32un),
            )
            header = header_structure.parse(raw)
            for idx in range(len(header['unknown'])):
                print(f'{idx} {header["unknown"][idx]}')
            headers_list.append(header['unknown'])
df = pd.DataFrame(headers_list)
df2=df-df.iloc[0]
with open(tin1, "rb") as f:
    f.seek(29756+skip)

    raw = f.read(32*35)
    header_structure = Struct(
        #"magic1" / Int32un,
        #"version" / PaddedString(10,'ascii'),
        "unknown" / Array(35, Int32un),
    )
    header2 = header_structure.parse(raw)
# print(header2)
    with open(tin2, "rb") as f:
        f.seek(644526+skip)

        raw = f.read(32*35)
        header_structure = Struct(
            #"magic1" / Int32un,
            #"version" / PaddedString(10,'ascii'),
            "unknown" / Array(35, Int32un),
        )
        header3 = header_structure.parse(raw)
        #print(header3)
    print('\n\nSKIP:',skip)
    for idx in range(len(header2['unknown'])):
        print(header3['unknown'][idx]-header2['unknown'][idx])

for skip in range(0,4):
    with open(dimit, "rb") as f:
        f.seek(36897+skip)

        raw = f.read(32*35)
        header_structure = Struct(
            #"magic1" / Int32un,
            #"version" / PaddedString(10,'ascii'),
            "unknown" / Array(35, Int32un),
        )
        header2 = header_structure.parse(raw)
       # print(header2)
    with open(dimit2, "rb") as f:
        f.seek(29565+skip)

        raw = f.read(32*35)
        header_structure = Struct(
            #"magic1" / Int32un,
            #"version" / PaddedString(10,'ascii'),
            "unknown" / Array(35, Int32un),
        )
        header3 = header_structure.parse(raw)
        #print(header3)
    print('\n\nSKIP:',skip)
    for idx in range(len(header2['unknown'])):
        print(header3['unknown'][idx]-header2['unknown'][idx])
print('debug')
    # apply a skip of 0-3 bytes

    # f.read(skip)
    # while f:
    #     volume = np.frombuffer(
    #         f.read(4), dtype=np.uint32
    #     )
    #     # if volume[0] ==1087080448:
    #     #     print('debug') # found with a skip of 1 byte
    #     if np.isclose(volume[0], 1368403200,atol=86400):
    #         print(skip,volume[0],'TIN0902T')
    #     if np.isclose(volume[0], 1348444800,atol=86400):
    #         print(skip,volume[0],'TIN0007')
    #
    #
    #
    #     #if volume ==
file = E2E(filepath)
oct_volumes = (
    file.read_oct_volume()
)  # returns a list of all OCT volumes with additional metadata if available
# for volume in oct_volumes:
#     volume.peek()  # plots a montage of the volume
#     volume.save("{}_{}.png".format(volume.volume_id, volume.laterality))
#
# fundus_images = (
#     file.read_fundus_image()
# )  # returns a list of all fundus images with additional metadata if available
# for image in fundus_images:
#     image.save("{}+{}.png".format(image.image_id, image.laterality))
