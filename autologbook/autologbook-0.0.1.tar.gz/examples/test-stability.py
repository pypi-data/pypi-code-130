# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:17 2022

@author: elog-admin
"""
import random
import shutil
import time
from pathlib import Path


def main():

    input_tifffile = Path('S:/software-dev/myquattro.tif')
    #dest_folder = Path('R:/A226/Results/2022/12456-RADCAS-Bulgheroni/')
    dest_folder = Path(
        'C:/Users/elog-admin/Documents/src/12456-RADCAS-Bulgheroni')
    delay_mu = 5
    delay_sigma = 1.

    #events = ('new_pic', 'remove_pic', 'mod_pic')
    #events = ('new_pic', 'remove_pic', 'mod_pic')
    events = ('new_pic', 'remove_pic', 'new_pic')
    samples = (Path('Graphite'), Path('Cemento'), Path('Carta'))

    for sample in samples:
        (dest_folder / sample).mkdir(exist_ok=True)

    number_attempts = 100
    for i in range(number_attempts):
        event = events[random.randint(0, len(events) - 1)]
        sample = samples[random.randint(0, len(samples) - 1)]
        dest_file = dest_folder / sample / \
            Path(f'{i:03}-{str(input_tifffile.name)}')
        delay = random.gauss(delay_mu, delay_sigma)
        while delay <= 0:
            delay = random.gauss(delay_mu, delay_sigma)
        time.sleep(delay)
        if event == 'new_pic':
            print(
                f'Iteration {i:03} of type {event} on {sample} file {dest_file.name} with {delay:.3f} sec delay')
            shutil.copy(str(input_tifffile), str(dest_file))
        elif event == 'remove_pic':
            for file in (dest_folder / sample).glob('*tif*'):
                file.unlink()
                print(
                    f'Iteration {i:03} of type {event} on {sample} file {file.name} with {delay:.3f} sec delay')
                break
        elif event == 'mod_pic':
            for file in (dest_folder / sample).glob('*tif*'):
                file.touch()
                print(
                    f'Iteration {i:03} of type {event} on {sample} file {file.name} with {delay:.3f} sec delay')
                break


if __name__ == '__main__':
    main()
