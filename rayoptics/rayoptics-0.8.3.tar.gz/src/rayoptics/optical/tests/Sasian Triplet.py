#!/usr/bin/env python
# coding: utf-8
.. currentmodule:: rayoptics.optical

###############
Triplet example
###############

This triplet design, used in Jose Sasian's `Lens Design OPTI 517 <https://wp.optics.arizona.edu/jsasian/courses/opti-517/>`_ course at the Univ. of Arizona, is attributed to Geiser.
# In[1]:


#get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


isdark = False

Setup the rayoptics environment
-------------------------------

The ``environment.py`` module imports many useful classes and functions. All the symbols defined in the module are intended to be imported into a rayoptics interactive session.
# In[3]:


from rayoptics.environment import *

Create a new model
------------------

Create a new :class:`~opticalmodel.OpticalModel` instance and set up some convenient aliases to important constituents of the model.
# In[4]:


opm = OpticalModel()
sm  = opm.seq_model
osp = opm.optical_spec
pm = opm.parax_model


# ### Define first order aperture and field for system
# 
# The pupil and field specifications can be specified in a variety of ways. The `key` keyword argument takes a list of 2 strings. The first string indicates whether the specification is in object or image space. The second one indicates which parameter is the defining specification.

# The PupilSpec can be defined in object or image space. The defining parameters can be `pupil`, `f/#` or `NA`, where `pupil` is the pupil diameter.

# In[5]:


osp.pupil = PupilSpec(osp, key=['object', 'pupil'], value=12.5)


# The FieldSpec can be defined in object or image space. The defining parameters can be `height` or `angle`, where `angle` is given in degrees.

# In[6]:


#osp.field_of_view = FieldSpec(osp, key=['object', 'angle'], flds=[0., 20.0])
osp.field_of_view = FieldSpec(osp, key=['object', 'angle'], value=20.0, flds=[0., 0.707, 1.], is_relative=True)


# The WvlSpec defines the wavelengths and weights to use when evaluating the model. The wavelength values can be given in either nanometers or a spectral line designation.

# In[7]:


osp.spectral_region = WvlSpec([('F', 0.5), (587.5618, 1.0), ('C', 0.5)], ref_wl=1)


# ### Define interface and gap data for the sequential model

# In[8]:


opm.radius_mode = True

sm.gaps[0].thi=1e10

sm.add_surface([23.713, 4.831, 'N-LAK9', 'Schott'])
sm.add_surface([7331.288, 5.86])
sm.add_surface([-24.456, .975, 'N-SF5,Schott'])
sm.set_stop()
sm.add_surface([21.896, 4.822])
sm.add_surface([86.759, 3.127, 'N-LAK9', 'Schott'])
sm.add_surface([-20.4942, 41.2365])


# ### Update the model

# In[9]:


opm.update_model()


# ## Draw a lens picture

# In[10]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, is_dark=isdark).plot()


# In[11]:


opm.ele_model.list_elements()

Draw a |ybar| diagram
---------------------
# In[12]:


yybar_plt = plt.figure(FigureClass=InteractiveDiagram, opt_model=opm, dgm_type='ht',
                       do_draw_axes=True, do_draw_frame=True, is_dark=isdark).plot()


# ## Plot the transverse ray aberrations

# In[13]:


abr_plt = plt.figure(FigureClass=RayFanFigure, opt_model=opm, data_type='Ray', scale_type=Fit.All_Same, is_dark=isdark).plot()


# ## Plot the wavefront aberration

# In[14]:


wav_plt = plt.figure(FigureClass=RayFanFigure, opt_model=opm, data_type='OPD', scale_type=Fit.All_Same, is_dark=isdark).plot()


# ## List the optical specifications

# In[15]:


pm.first_order_data()


# ## List the paraxial model

# In[16]:


pm.list_lens()


# ## Third Order Seidel aberrations
# 
# ### Computation and tabular display

# In[17]:


to_pkg = compute_third_order(opm)
to_pkg


# ### Bar chart for surface by surface third order aberrations

# In[18]:


fig, ax = plt.subplots()
ax.set_xlabel('Surface')
ax.set_ylabel('third order aberration')
ax.set_title('Surface by surface third order aberrations')
to_pkg.plot.bar(ax=ax, rot=0)
ax.grid(True)
fig.tight_layout()


# ### convert aberration sums to transverse measure

# In[19]:


ax_ray, pr_ray, fod = osp.parax_data
n_last = pm.sys[-1][mc.indx]
u_last = ax_ray[-1][mc.slp]
to.seidel_to_transverse_aberration(to_pkg.loc['sum',:], n_last, u_last)


# ### convert sums to wavefront measure

# In[20]:


central_wv = opm.nm_to_sys_units(sm.central_wavelength())
to.seidel_to_wavefront(to_pkg.loc['sum',:], central_wv).T


# ### compute Petzval, sagittal and tangential field curvature

# In[21]:


to.seidel_to_field_curv(to_pkg.loc['sum',:], n_last, fod.opt_inv)


# ## Save the model

# In[22]:


opm.save_model('Sasian Triplet')

