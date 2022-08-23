# -*- coding: utf-8 -*-

import pandas as pd


def load_indexs_system(fpath):
    df = pd.read_excel(fpath)
    return df


if __name__ == '__main__':
    import time

    strt_tm = time.time()


    print('used time: {}s.'.format(round(time.time()-strt_tm, 6)))
