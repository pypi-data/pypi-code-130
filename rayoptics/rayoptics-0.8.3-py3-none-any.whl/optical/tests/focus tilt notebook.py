#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%matplotlib inline
#get_ipython().run_line_magic('matplotlib', 'widget')


# In[2]:


isdark = True


# In[3]:


# initialization
from rayoptics.environment import *

from rayoptics.gui import dashboards

from matplotlib import gridspec
from matplotlib.colors import LogNorm, PowerNorm, Normalize
from mpl_toolkits.mplot3d import axes3d

import colorcet as cc

import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual


# In[4]:


root_pth = Path(rayoptics.__file__).resolve().parent


# # Create a new model

# In[5]:


opm = OpticalModel()
sm = opm.seq_model
osp = opm.optical_spec
pm = opm.parax_model


# ## Define first order aperture and field for system

# In[6]:


pupil_diameter = 100.
pupil_radius = pupil_diameter/2
osp.pupil = PupilSpec(osp, key=['object', 'pupil'], value=pupil_diameter)

# single field on-axis
osp.field_of_view = FieldSpec(osp, key=['object', 'angle'], flds=[0.0])

# wavelength for analysis: 550nm
osp.spectral_region = WvlSpec([(550.0, 1.0)], ref_wl=0)


# ### object at infinity, i.e. collimated input

# In[7]:


sm.gaps[0].thi = 1e+11


# In[8]:


#opm.add_mirror(lbl='M1', r=-500., t=-250.)
opm.add_mirror(lbl='M1', profile=Conic, r=-500., cc=-1., t=-250.)


# In[11]:


sm.list_model()


# In[9]:


opm.update_model()
fod = opm['analysis_results']['parax_data'].fod



# # Draw a lens picture

# In[10]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, is_dark=isdark,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# # List first order data

# In[ ]:


fod.list_first_order_data()


# In[ ]:


fld, wvl, foc = osp.lookup_fld_wvl_focus(0)


# ### create fan and grid objects for use by plot grid

# In[ ]:


ray_xfan = analyses.RayFan(opm, f=fld, wl=wvl, xyfan='x')
ray_yfan = analyses.RayFan(opm, f=fld, wl=wvl, xyfan='y')
ray_grid = analyses.RayGrid(opm, f=fld, wl=wvl)


# In[ ]:


ndim = 32
maxdim = 256
pupil_grid = analyses.RayGrid(opm, num_rays=ndim, f=fld, wl=wvl, foc=-0.0)


# ### Create lists of fans, data types, and plotting keyword arguments to drive 

# In[ ]:


xyabr_fan_list = [(ray_xfan, 'dx', dict(num_points=100)),
                  (ray_yfan, 'dy', dict(num_points=100, linestyle='--'))]


# In[ ]:


opd_fan_list = [(ray_yfan, 'opd', dict(linestyle='', linewidth=1, marker='D', markersize=3.5)),
                (ray_yfan, 'opd', dict(num_points=100, linewidth=2))]


# ### create focus dashboard

# In[ ]:


one_wave = opm.nm_to_sys_units(wvl)
# one wave of defocus
dfoc = one_wave/(fod.img_na**2/(2*fod.n_img))
qwrt_dfoc = abs(0.25*dfoc)

# one wave of tilt
_, _, ref_sphere_radius = fld.ref_sphere
shft = ref_sphere_radius*one_wave/fod.exp_radius


# In[ ]:


opd_scale = 1.0
ta_scale = .01


# In[ ]:


# create a figure with a wavefront map and transverse ray and opd ray fans
fig = plt.figure(FigureClass=AnalysisFigure, data_objs=[ray_grid, ray_xfan, ray_yfan],
                 figsize=[9, 5], tight_layout=True, is_dark=isdark)
gs = gridspec.GridSpec(nrows=8, ncols=13, figure=fig)

Wavefront(fig, gs[:8, :8], ray_grid, user_scale_value=opd_scale, do_contours=False, title='Wavefront Map')
RayFanPlot(fig, gs[:4, 9:], xyabr_fan_list, user_scale_value=ta_scale, scale_type='user',
           yaxis_ticks_position='right', title='Transverse Ray Aberration')
RayFanPlot(fig, gs[4:8, 9:], opd_fan_list, user_scale_value=opd_scale, scale_type='user',
           yaxis_ticks_position='right', title='Wavefront Aberration')
fig.refresh()

# create a figure with transverse ray and opd ray fans 
fig2 = plt.figure(FigureClass=AnalysisFigure, data_objs=[ray_xfan, ray_yfan],
                 figsize=[9, 5], is_dark=isdark)
gs2 = gridspec.GridSpec(nrows=1, ncols=2, figure=fig2)

RayFanPlot(fig2, gs2[0, 0], xyabr_fan_list, user_scale_value=ta_scale, scale_type='user',
           title='Transverse Ray Aberration')
RayFanPlot(fig2, gs2[0, 1], opd_fan_list, user_scale_value=opd_scale, scale_type='user',
           yaxis_ticks_position='right', title='Wavefront Aberration')
fig2.plot()

# create sliders for controlling defocus and image offset
defocus, x_shift, y_shift = dashboards.create_focus_dashboard([fig, fig2],
                                                   [ray_grid, ray_xfan, ray_yfan],
                                                   osp.defocus.focus_shift, abs(dfoc), shft, on_axis_pt=[0, 0])
display(widgets.HBox([defocus, y_shift]))


# In[ ]:


fig_psf = plt.figure(FigureClass=AnalysisFigure, data_objs=[pupil_grid],
                     figsize=[6, 6], is_dark=isdark)
gs_psf = gridspec.GridSpec(nrows=2, ncols=2, figure=fig_psf)

wfr = Wavefront(fig_psf, gs_psf[:, :1], pupil_grid, user_scale_value=None, do_contours=False,
                title='Wavefront Map', cmap="BrBG_r")

psf = DiffractionPSF(fig_psf, gs_psf[:, -1:], pupil_grid, maxdim, cmap=cc.m_fire,
                     yaxis_ticks_position='left', title='PSF', norm=PowerNorm(gamma=0.5, vmin=1e-4))

fig_psf.plot()


# In[ ]:


from numpy.fft import fftshift, fft2


# In[ ]:


ndim = 64
maxdim = 4096
pupil_grid = analyses.RayGrid(opm, num_rays=ndim, f=fld, wl=wvl, foc=-0.0)


# In[ ]:


psf_dim = analyses.psf_sampling(maxdim, ndim)
n_airy = psf_dim[2]
psf_dim


# In[ ]:


opd = pupil_grid.grid[2]


# In[ ]:


AP = analyses.calc_psf(opd, ndim, maxdim)


# In[ ]:


figg = plt.figure()
plt.imshow(AP, origin='lower', norm=LogNorm(vmin=5e-4), cmap=cc.m_fire)
plt.colorbar()
plt.show()


# In[ ]:


delta_x, delta_xp = analyses.calc_psf_scaling(pupil_grid, ndim, maxdim)


# In[ ]:


maxdim_by_2 = maxdim//2
W = np.zeros([maxdim, maxdim])
nd2 = ndim//2


# In[ ]:


image_scale = maxdim_by_2 * delta_xp
xi = np.linspace(-image_scale, image_scale, maxdim)
yi = np.linspace(-image_scale, image_scale, maxdim)
#xi = np.linspace(-image_scale, image_scale, nd)
#yi = np.linspace(-image_scale, image_scale, nd)
[XI, YI] = np.meshgrid(xi, yi)


# In[ ]:


fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(XI, YI, AP)


# In[ ]:


delta_x, delta_xp, image_scale


# In[ ]:


maxdim/n_airy, maxdim/ndim


# In[ ]:


psf_dim


# In[ ]:




W[maxdim_by_2-(nd2-1):maxdim_by_2+(nd2+1), maxdim_by_2-(nd2-1):maxdim_by_2+(nd2+1)] = np.nan_to_num(opd)
phase = np.exp(1j*2*np.pi*W)
for i in range(len(phase)):
    for j in range(len(phase)):
        if phase[i][j] == 1:
            phase[i][j] = 0
AP = abs(fftshift(fft2(fftshift(phase))))**2
AP_max = np.nanmax(AP); AP_max
AP = AP/AP_max
AP_sub = AP[maxdim_by_2-(ndim-1):maxdim_by_2+(ndim+1), maxdim_by_2-(ndim-1):maxdim_by_2+(ndim+1)]