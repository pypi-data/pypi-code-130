#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 12:47:09 2021

@author: Mike
"""

isdark = False
from rayoptics.environment import *
from rayoptics.elem.elements import Element
from rayoptics.raytr.trace import apply_paraxial_vignetting

# JP2019-152887 Example 3 (Nikon AF-S Nikkor 400mm f/2.8 E FL ED VR)
# Obtained via https://www.photonstophotos.net/GeneralTopics/Lenses/OpticalBench/OpticalBenchHub.htm

opm = OpticalModel()
sm  = opm.seq_model
osp = opm.optical_spec
pm = opm.parax_model
osp.pupil = PupilSpec(osp, key=['image', 'f/#'], value=2.89)
osp.field_of_view = FieldSpec(osp, key=['object', 'angle'], flds=[0., 3.14])
osp.spectral_region = WvlSpec([(486.1327, 0.5), (587.5618, 1.0), (656.2725, 0.5)], ref_wl=1)
opm.system_spec.title = 'JP2019-152887 Example 3 (Nikon AF-S Nikkor 400mm f/2.8 E FL ED VR)'
opm.system_spec.dimensions = 'MM'
opm.radius_mode = True
sm.gaps[0].thi=1e10
sm.add_surface([1200.37,5,1.5168,63.88])
sm.ifcs[sm.cur_surface].max_aperture = 69.61
sm.add_surface([1199.79,1])
sm.ifcs[sm.cur_surface].max_aperture = 69.61
sm.add_surface([207.079,17.5,1.43384,95.26])
sm.ifcs[sm.cur_surface].max_aperture = 68.61
sm.add_surface([-1127.53,44.9])
sm.ifcs[sm.cur_surface].max_aperture = 68.61
sm.add_surface([175.97,18,1.43384,95.26])
sm.ifcs[sm.cur_surface].max_aperture = 57.61
sm.add_surface([-397.271,3.07])
sm.ifcs[sm.cur_surface].max_aperture = 57.61
sm.add_surface([-360.24,6,1.61266,44.46])
sm.ifcs[sm.cur_surface].max_aperture = 55.36
sm.add_surface([353.184,90])
sm.ifcs[sm.cur_surface].max_aperture = 55.36
sm.add_surface([66.4844,4,1.795,45.32])
sm.ifcs[sm.cur_surface].max_aperture = 34.61
sm.add_surface([45.9182,15,1.49782,82.54])
sm.ifcs[sm.cur_surface].max_aperture = 31.61
sm.add_surface([1114.11,18.503])
sm.ifcs[sm.cur_surface].max_aperture = 31.61
sm.add_surface([2992.55,2.5,1.755,52.34])
sm.ifcs[sm.cur_surface].max_aperture = 24.11
sm.add_surface([118.04,3.35])
sm.ifcs[sm.cur_surface].max_aperture = 23.36
sm.add_surface([-241.694,3.5,1.84668,23.83])
sm.ifcs[sm.cur_surface].max_aperture = 23.36
sm.add_surface([-86.4136,2.4,1.53996,59.52])
sm.ifcs[sm.cur_surface].max_aperture = 23.36
sm.add_surface([64.2643,38.179])
sm.ifcs[sm.cur_surface].max_aperture = 23.36
sm.add_surface([0,1.5])
sm.set_stop()
sm.ifcs[sm.cur_surface].max_aperture = 18.979
sm.add_surface([90.0336,7.6,1.48749,70.43])
sm.ifcs[sm.cur_surface].max_aperture = 19.36
sm.add_surface([-63.8039,1.2])
sm.ifcs[sm.cur_surface].max_aperture = 19.36
sm.add_surface([-65.9768,1.9,1.84668,23.83])
sm.ifcs[sm.cur_surface].max_aperture = 18.36
sm.add_surface([-114.876,5])
sm.ifcs[sm.cur_surface].max_aperture = 18.36
sm.add_surface([300.359,3.5,1.84668,23.83])
sm.ifcs[sm.cur_surface].max_aperture = 18.36
sm.add_surface([-128.056,1.9,1.59319,67.94])
sm.ifcs[sm.cur_surface].max_aperture = 18.36
sm.add_surface([53.9004,3.1])
sm.ifcs[sm.cur_surface].max_aperture = 18.36
sm.add_surface([-347.542,1.9,1.755,52.33])
sm.ifcs[sm.cur_surface].max_aperture = 17.36
sm.add_surface([94.5337,4.19])
sm.ifcs[sm.cur_surface].max_aperture = 17.36
sm.add_surface([118.353,3.5,1.7725,49.68])
sm.ifcs[sm.cur_surface].max_aperture = 16.86
sm.add_surface([-384.382,0.1])
sm.ifcs[sm.cur_surface].max_aperture = 16.86
sm.add_surface([67.4622,4.5,1.64,60.14])
sm.ifcs[sm.cur_surface].max_aperture = 17.11
sm.add_surface([-340.421,1.9,1.84668,23.83])
sm.ifcs[sm.cur_surface].max_aperture = 17.11
sm.add_surface([246.642,6.5])
sm.ifcs[sm.cur_surface].max_aperture = 17.11
sm.add_surface([0,1.5,1.5168,63.88])
sm.ifcs[sm.cur_surface].max_aperture = 17.86
sm.add_surface([0,74.22])
sm.ifcs[sm.cur_surface].max_aperture = 17.86
#sm.list_surfaces()
#sm.list_gaps()
sm.do_apertures = False
opm.update_model()
apply_paraxial_vignetting(opm)
layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, do_draw_rays=True, do_paraxial_layout=False,
                        is_dark=isdark).plot()
sm.list_model()
# List the optical specifications
pm.first_order_data()
# List the paraxial model
pm.list_lens()
# Plot the transverse ray aberrations
abr_plt = plt.figure(FigureClass=RayFanFigure, opt_model=opm,
          data_type='Ray', scale_type=Fit.All_Same, is_dark=isdark).plot()
# Plot the wavefront aberration
wav_plt = plt.figure(FigureClass=RayFanFigure, opt_model=opm,
          data_type='OPD', scale_type=Fit.All_Same, is_dark=isdark).plot()
# Plot spot diagrams
spot_plt = plt.figure(FigureClass=SpotDiagramFigure, opt_model=opm,
                      scale_type=Fit.User_Scale, user_scale_value=0.1, is_dark=isdark).plot()