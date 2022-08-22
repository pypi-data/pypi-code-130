import os
from PIL import Image

def split_image(img_path, folder_path):
    """
    Split an image into smaller images.

    Parameters
    ----------
    img_path : str
        Path to the image to be split.
    folder_path : str
        Path to the folder where the images will be saved.
    """

    im = Image.open(img_path)
    pix = im.load()

    width, height = im.size

    visited = [[False for _ in range(height)] for _ in range(width)]
    sets = []

    for row in range(height):
        for col in range(width):
            if not visited[col][row] and pix[col, row] != (0, 0, 0, 0):
                visited[col][row] = True

                set = {(col, row)}
                queue = [(col, row)]

                while queue:
                    col, row = queue.pop(0)
                    for nrow, ncol in [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)]:
                        if 0 <= nrow < im.size[1] and 0 <= ncol < im.size[0] and not visited[ncol][nrow] and pix[ncol, nrow] != (0, 0, 0, 0):
                            visited[ncol][nrow] = True
                            set.add((ncol, nrow))
                            queue.append((ncol, nrow))

                sets.append(set)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for id, set in enumerate(sets):
        x_values = [x[0] for x in set]
        y_values = [x[1] for x in set]

        box = (min(x_values), min(y_values), max(x_values) + 1, max(y_values) + 1)
        outp = im.crop(box)
        outp.save(f"{folder_path}/{id}.png")