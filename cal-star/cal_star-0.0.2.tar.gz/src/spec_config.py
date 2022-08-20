# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 10:33:40 2022

@author: Liang Yu

This code is used for setting the spce_cal parameters.
by Yu Liang 
yuliang@shao.ac.cn
"""

import numpy as np
import pandas as pd
import os
import astropy.io.fits as fits
from scipy.integrate import simps
import extinction
import pdb

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata = os.path.join(path, r'refdata/')

class spec_map(object):

    r"""
    get spectrum template using the input parameters

    .. todo::
        enable to add emission lines


    Args:
        isource (dict, including 3 keys):
            name:
                the spectrum filename
            redshift:
                the redshift applied to the template
            ebv:
                the extinction applied to the template

    Attributes:

        wave (`numpy.ndarray`, unit in Angstrom):
            the wavelength of the spectrum, redshift applied.
        flux (`numpy.ndarray`, unit in erg/s/cm^2/A)
            the flux of the spectrum, redshift and extinction considered.

    """

    def __init__(self, starlist, star):

        starlist = starlist
        star = star   
        if starlist in ['Hamuy1992',
                        'oke1990',
                        'Massey1998',
                        'gemini',
                        'ctiocal',
                        'spec50cal']:            
            template_filename = os.path.join(refdata, '1d_radec', starlist,'*.xlsx')
            
            cat = pd.read_csv(template_filename)
            print(cat)
            ra = cat.iat[i,1]
            dec = cat.iat[i,2]   
        else:
            raise ValueError("starlist or star name wrong. ")
        self.ra = ra
        self.dec = dec
        self.cat = cat
        
#    def sp_plot(template_wave,template_flux):
#            template_wave = cat[0]      # unit should be in Angstrom
#            template_flux = cat[1]      # unit should be in erg/s/cm^2/A

    def radec2plot(self):  # t2d: time to display ra map
        display(self.ra.hour,self.ra.minute,self.ra.second,self.ra.microsecond)
        ram =  self.ra.hour + self.ra.minute / 60 + self.ra.second/3600
        deg = int(self.dec[0:3])
        arcm = int(self.dec[4:6])
        arcs = int(self.dec[7:10])
        decm =  deg + arcm / 60 + arcs/3600
        plt.plot(ram,decm,'r*')
    return ram,decm

    def shown_listinfor(self):
        starlist = self.starlist
        star = self.star   
        if starlist in ['Hamuy1992',
                        'oke1990',
                        'Massey1998',
                        'gemini',
                        'ctiocal',
                        'spec50cal']:            
            template_filename = os.path.join(refdata, '1d_radec', starlist,'*.xlsx')
            
            cat = pd.read_csv(template_filename)
            print(cat)
        else:
            raise ValueError("starlist or star name wrong. ")
 
        return cat