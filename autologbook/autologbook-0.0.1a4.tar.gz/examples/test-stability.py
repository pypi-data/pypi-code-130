# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:17 2022

@author: elog-admin
"""
import random
import shutil
import time
from pathlib import Path
import argparse
import sys

def main_parser():
    """
    Define the main argument parser.

    Returns
    -------
    parser : ArgumentParser
        The main parser.
    """
    parser = argparse.ArgumentParser(description='''
                                 Test your autologbook generating fake analysis
                                 ''')
    parser.add_argument('-m', '--microscope', type=str, dest='microscope',
                        choices=('Quattro', 'Versa'), default='Quattro',
                        help='''
                        Set the microscope for which the fake analysis will
                        be generated.
                        ''')
    parser.add_argument('-d', '--delay-avg', type=float, dest='delay_mu',
                        default=5,help='''
                        The average delay in seconds between the generation of two
                        following events.
                        '''
                        )
    parser.add_argument('-s', '--delay-sigma', type=float, dest='delay_sigma',
                        default=1,help='''
                        The spread delay in seconds between the generation of two
                        following events.
                        '''
                        )
    parser.add_argument('-n', '--num-events', type=int, dest='number_events',
                        default=100,help='''
                        The total number of events to be generated.
                        '''
                        )
    return parser



def main(cli_args, prog):

    parser = main_parser()
    if prog:
        parser.prog = prog

    args = parser.parse_args(cli_args)
    
    microscope = args.microscope

    if microscope == 'Quattro':
        input_tifffile = Path('S:/software-dev/myquattro.tif')
        dest_folder = Path(
            'C:/Users/elog-admin/Documents/src/12456-RADCAS-Bulgheroni')
    elif microscope == 'Versa':
        input_tifffile = Path('S:/software-dev/myversa.tif')
        dest_folder = Path(
            'C:/Users/elog-admin/Documents/src/#12457-FIBVERSA-Bulgheroni')
        
    #dest_folder = Path('R:/A226/Results/2022/12456-RADCAS-Bulgheroni/')
    delay_mu = args.delay_mu
    delay_sigma = args.delay_sigma 


    #events = ('new_pic', 'remove_pic', 'mod_pic')
    #events = ('new_pic', 'remove_pic', 'mod_pic')
    events = ('new_pic', 'remove_pic', 'new_pic')
    samples = (Path('Graphite'), Path('Cemento'), Path('Carta'))

    for sample in samples:
        (dest_folder / sample).mkdir(exist_ok=True)

    number_events = args.number_events 
    for i in range(number_events):
        event = events[random.randint(0, len(events) - 1)]
        sample = samples[random.randint(0, len(samples) - 1)]
        if microscope == 'Quattro':
            dest_file = dest_folder / sample / \
                Path(f'{i:03}-{str(input_tifffile.name)}')
        elif microscope == 'Versa':
            dest_file = dest_folder / sample / \
                Path(f'{str(input_tifffile.stem)}_{i:03}{str(input_tifffile.suffix)}')
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
    main(sys.argv[1:], 'py test-stability.py')
