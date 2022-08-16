import os
import logging
import pandas as pd

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=format)
logger = logging.getLogger(__name__)


def openfile(file_path):
    """
    Open the file
    :param - file_path
    :yield - line
    """
    with open(file_path, 'r') as f:
        for _, line in enumerate(f.readlines()):
            sp = line.strip().split(" ")
            yield f'{sp[0]},{" ".join(sp[1:])}\n'

def create_dataframe(path: str, save: bool = False) -> pd.DataFrame:
    """
    Convert the dataset to csv
    :param - path: path to the dataset
           - save: whether to save the dataframe
    :return - dataframe
    """
    files = ['wav.scp', 'utt2spk', 'text']
    files = [openfile(os.path.join(path, file)) for file in files]
    w, u, t = files
    logger.info('Converting to dataframe')
    x = pd.read_csv(genReader(w), sep=',', header=None, names=['utt', 'wav'])
    logger.info('wav.scp converted')
    y = pd.read_csv(genReader(u), sep=',', header=None, names=['utt', 'spk'])
    logger.info('utt2spk converted')
    z = pd.read_csv(genReader(t), sep=',', header=None, names=['utt', 'text'])
    logger.info('text converted')
    data = pd.merge(x, y, on='utt')
    data = pd.merge(data, z, on='utt')
    logger.info('Finished converting to dataframe')
    data = data.drop_duplicates()
    data['spk'] = data['spk'].str.split('-', 1, expand=True)[0]
    if save:
        data.to_csv('data.csv', index=False)
    return data

class genReader(object):
    """
    Helper class for geneator to be used with df.read_csv()
    """
    def __init__(self, generator):
        self.generator = generator

    def read(self, n=0):
        try:
            return next(self.generator)
        except StopIteration:
            return ""
