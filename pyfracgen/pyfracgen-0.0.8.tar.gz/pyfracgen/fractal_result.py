import pickle


class fractal_result:

    def __init__(self, arr, width, height, dpi):

        self.image_array = arr
        self.width_inches = width
        self.height_inches = height
        self.dpi = dpi

    def save(self, name='save'):

        res = [self.image_array, self.width_inches, self.height_inches, self.dpi]
        with open(name, 'wb') as f:
            pickle.dump(res, f)


def open_fractal_result(file):

    with open(file, 'rb') as f:
        res = pickle.load(f)
        
    return fractal_result(*res)
