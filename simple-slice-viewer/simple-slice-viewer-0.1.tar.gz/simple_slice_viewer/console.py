#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:35:34 2020

@author: marcel
"""

from simple_slice_viewer.controller import display
import SimpleITK as sitk
import argparse



def _load(im):
    if isinstance(im, str):
        im = sitk.ReadImage(im)
    return im

def run_from_cmd():
    args = cmdparser().parse_args()
    image = _load(args.image)
    fusion = _load(args.fusion)
    
    display(image=image, fusion=fusion)
    
    
def cmdparser():
    
    parser = argparse.ArgumentParser(description='SimpleITK slice browser')
    
    parser.add_argument('image', type=str, nargs='?',
                    help='Image file', default=None)
    
    parser.add_argument('--fusion', type=str, nargs='?',
                    help='Fusion image file',
                    default=None)
    
   
    
    return parser
    


  

    