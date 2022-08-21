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


# In[4]:


root_pth = Path(rayoptics.__file__).resolve().parent


# # Create a new model

# In[5]:


opm = OpticalModel()
sm = opm.seq_model
osp = opm.optical_spec
pm = opm.parax_model
em = opm.ele_model
pt = opm.part_tree


# ## Define first order aperture and field for system

# In[6]:


pupil_diameter = 12.5
pupil_radius = pupil_diameter/2
osp.pupil = PupilSpec(osp, key=['object', 'pupil'], value=pupil_diameter)

# single field on-axis
osp.field_of_view = FieldSpec(osp, key=['object', 'angle'],
                              value=20.0, flds=[0., 0.707, 1.],
                              is_relative=True)

# wavelength for analysis: visual
osp.spectral_region = WvlSpec([('F', 0.5), ('d', 1.0), ('C', 0.5)], ref_wl=1)


# ### object at infinity, i.e. collimated input

# In[7]:
    
opm.radius_mode = True

sm.gaps[0].thi = 1e+11

sm.add_surface([23.713, 4.831, 'N-LAK9', 'Schott'])
sm.add_surface([7331.288, 5.86])
sm.add_surface([-24.456, .975, 'N-SF5,Schott'])
sm.set_stop()
sm.add_surface([21.896, 4.822])
sm.add_surface([86.759, 3.127, 'N-LAK9', 'Schott'])
sm.add_surface([-20.4942, 41.2365])


# In[11]:


sm.list_model()


# In[9]:


opm.update_model()
fod = osp.parax_data.fod


# # Draw a lens picture

# In[10]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, is_dark=isdark,
                        do_draw_rays=True, do_paraxial_layout=False).plot()

yybar_plt = plt.figure(FigureClass=InteractiveDiagram, opt_model=opm, dgm_type='ht',
                       refresh_gui=None, is_dark=isdark).plot()
# # List first order data

# In[ ]:


fod.list_first_order_data()


# In[ ]:


fld, wvl, foc = osp.lookup_fld_wvl_focus(0)


# ### create fan and grid objects for use by plot grid

# In[ ]:


ray_xfan = analyses.RayFan(opm, f=fld, wl=wvl, xyfan='x')
ray_yfan = analyses.RayFan(opm, f=fld, wl=wvl, xyfan='y')
