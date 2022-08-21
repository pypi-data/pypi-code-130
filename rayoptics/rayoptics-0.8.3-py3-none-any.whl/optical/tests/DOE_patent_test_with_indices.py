#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


isdark = True


# In[43]:


# initialization
import csv
import itertools
from rayoptics.environment import *
from rayoptics.oprops import doe
from rayoptics.util.misc_math import normalize
from numpy.linalg import norm
from math import copysign


# In[4]:


def ray_debug(ray):
    print('            Y             Z            M             N           srf M         srf N         sin I          Len')
    for i, r in enumerate(ray):
        cos_I = np.dot(r.d, r.nrml)
        sin_I = np.sqrt(1 - cos_I**2)
        print(f'{i:2d}: {r.p[1]:12.6f}  {r.p[2]:12.6f}  {r.d[1]:12.8f}  {r.d[2]:12.8f}  {r.nrml[1]:12.8f}  {r.nrml[2]:12.8f}  {sin_I:12.8f}  {r.dst:12.6f}')


# In[5]:


def refocus(opm):
    osp = opm.optical_spec
    sm = opm.seq_model

    fld, wvl, foc = osp.lookup_fld_wvl_focus(0)

    df_ray, ray_op, wvl = trace_base(opm, [0., 1.], fld, wvl)
    df_ray = [RaySeg(*rs) for rs in df_ray]

    defocus = -df_ray[-1].p[1]/(df_ray[-2].d[1]/df_ray[-2].d[2])
    sm.gaps[-1].thi += defocus
    opm.update_model()


# In[6]:


prescription = []
with open(Path('.') / 'DOE_patent.csv', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    for row in csv_reader:
        prescription.append(row)


# In[7]:


prescription


# ## build model from csv input data

# In[8]:


opm = OpticalModel()
sm = opm.seq_model
sm.do_apertures = False
osp = opm.optical_spec
pm = opm.parax_model


# In[9]:


osp.pupil = PupilSpec(osp, key=['image', 'f/#'], value=5.77)
osp.field_of_view = FieldSpec(osp, key=['image', 'height'], value=43.2/2, flds=[0., .707, 1.], is_relative=True)
osp.spectral_region = WvlSpec([('F', 0.5), ('d', 1.0), ('C', 0.5)], ref_wl=1)


# In[10]:


opm.radius_mode = True

sm.gaps[0].thi=1e12

for p in prescription:
    p[4] /= 2
    sm.add_surface(p)

sm.stop_surface = 11

orig_bf = sm.gaps[-1].thi

phase_element = doe.DiffractiveElement(coefficients=[-2.57E-05, -2.04E-11], phase_fct=doe.radial_phase_fct, ref_wl=587.6, order=1)
s5 = sm.ifcs[5]
s5.phase_element = phase_element
phase_element.listobj()


# In[11]:


sm.gaps[1].medium = create_glass('J-LASFH6,Hikari')
sm.gaps[2].medium = create_glass('J-FK5,Hikari')
sm.gaps[4].medium = create_glass('J-BK7A,Hikari')
sm.gaps[6].medium = create_glass('J-LAF2,Hikari')
sm.gaps[7].medium = create_glass('J-SFH4,Hikari')
sm.gaps[9].medium = create_glass('J-SFH5,Hikari')
sm.gaps[12].medium = create_glass('J-F2,Hikari')
sm.gaps[14].medium = create_glass('J-SFH1,Hikari')
sm.gaps[16].medium = create_glass('J-SK4,Hikari')
sm.gaps[18].medium = create_glass('J-FKH1,Hikari')
sm.gaps[19].medium = create_glass('J-LASKH2,Hikari')
sm.gaps[21].medium = create_glass('J-F16,Hikari')
sm.gaps[22].medium = create_glass('J-LASKH2,Hikari')
sm.gaps[24].medium = create_glass('J-SFH4,Hikari')
sm.gaps[25].medium = create_glass('J-F8,Hikari')
sm.gaps[27].medium = create_glass('J-FKH2,Hikari')
sm.gaps[29].medium = create_glass('J-LASKH2,Hikari')


# In[12]:


opm.update_model()

### trace the axial marginal ray to calculate defocus amount
# In[13]:


refocus(opm)


# In[14]:


sm.list_model()


# In[17]:


s5.phase_element.debug_output = True


# ### trace ray incident at a 10 mm height on surface 5

# In[18]:


fi = 0
wl = osp.spectral_region.reference_wvl
fld, wvl, foc = osp.lookup_fld_wvl_focus(fi, wl)


# In[19]:


pupil = [0., 0.5887113]
ray, ray_op, wvl = trace_base(opm, pupil, fld, wvl)
ray = [RaySeg(*rs) for rs in ray]

#opm.save_model(Path('.') / 'US2021_0026133_Ex_2_Real_Glasses.roa')
# In[20]:


ray_debug(ray)


# In[21]:




s5.phase_element.debug_output = False


# ## calculate transverse aberrations
# 
# There are ED elements in this lens. Chromatic aberration analysis based on only index and dispersion model refractive effects in ED glasses poorly, as seen in the plots.

# In[50]:


def reverse_path(seq_model, wl=None, start=None, stop=None, step=-1):
    """ returns an iterable path tuple for a range in the sequential model

    Args:
        wl: wavelength in nm for path, defaults to central wavelength
        start: start of range
        stop: first value beyond the end of the range
        step: increment or stride of range

    Returns:
        (**ifcs, gaps, lcl_tfrms, rndx, z_dir**)
    """
    def compute_local_transforms(seq_model, step=-1):
        """ Return forward surface coordinates (r.T, t) for each interface. """
        from rayoptics.elem import transform as trns
        tfrms = []
        path = itertools.zip_longest(seq_model.ifcs[::step], seq_model.gaps[::step])
        b4_ifc, b4_gap = before = next(path)
        while before is not None:
            try:
                ifc, gap = after = next(path)
            except StopIteration:
                tfrms.append((np.identity(3), np.array([0., 0., 0.])))
                break
            else:
                zdist = step*b4_gap.thi
                r, t = trns.forward_transform(b4_ifc, zdist, ifc)
                rt = r.transpose()
                tfrms.append((rt, t))
                before, b4_ifc, b4_gap = after, ifc, gap

        return tfrms
    if wl is None:
        wl = seq_model.central_wavelength()

    if step < 0:
        if start is not None:
            gap_start = start - 1
            rndx_start = start - 1
        else:
            gap_start = start
            rndx_start = -2
    else:
        gap_start = start

    tfrms = compute_local_transforms(seq_model, step=step)
    wl_idx = seq_model.index_for_wavelength(wl)
    rndx = [n[wl_idx] for n in seq_model.rndx[rndx_start:stop:step]]
    z_dir = [-z_dir for z_dir in seq_model.z_dir[start:stop:step]]
    path = itertools.zip_longest(seq_model.ifcs[start:stop:step],
                                 seq_model.gaps[gap_start:stop:step],
                                 tfrms,
                                 rndx,
                                 z_dir)
    return path

# In[51]:


rvrs_path = reverse_path(sm, step=-1)


# In[52]:


sm.list_model(path=rvrs_path)


# In[55]:


rev_ray = rt.trace_raw(reverse_path(sm), ray[-1].p, -ray[-1].d, wvl)


# In[57]:


ray[-1].p, -ray[-1].d, wvl


# In[59]:


rev_ray = [RaySeg(*rs) for rs in rev_ray[0]]


# In[40]:


list_ray(rev_ray)


# In[56]:


list_ray(ray)


# In[ ]:





# In[ ]:
    

