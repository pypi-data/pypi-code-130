#!/usr/bin/env python
# coding: utf-8

# In[2]:


# initialization
from rayoptics.environment import *

import anytree
from rayoptics.elem import parttree
import itertools
from rayoptics.raytr.trace import apply_paraxial_vignetting


# In[3]:


import transforms3d as t3d


# In[4]:


beta180 = np.array([0, np.deg2rad(180), 0])
rot_around_y = t3d.euler.euler2mat(*beta180); rot_around_y


# In[5]:


alpha180 = np.array([np.deg2rad(180), 0, 0])
rot_around_x = t3d.euler.euler2mat(*alpha180); rot_around_x


# In[6]:


rot_around_x = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
rot_around_y = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])


# In[7]:


root_pth = Path(rayoptics.__file__).resolve().parent


# In[48]:


opm = open_model(root_pth/"models/Sasian Triplet floating stop.roa")
sm = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']
ss = opm['specsheet']


# In[49]:


sm.list_model()


# In[50]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[51]:


pm.first_order_data()


# In[52]:


pt.list_model()


# In[53]:


em.list_model()


# In[54]:


for e in em.elements:
    print(f"{e.label}:  {e.tfrm}")


# In[55]:


e1 = pt.obj_by_name('E1')
e2 = pt.obj_by_name('E2')
e3 = pt.obj_by_name('E3')


# In[56]:


str(e1), str(e2), str(e3)


# In[57]:


opm.flip(e3)


# In[58]:


apply_paraxial_vignetting(opm)

opm.update_model()
# In[59]:


sm.list_model()


# In[60]:


layout_plt0 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False, do_draw_ray_fans=True,
                        refresh_gui=None).plot()
#layout_plt0.update_data()
#layout_plt0.plot()


# In[61]:


for e in em.elements:
    print(f"{e.label}:  {e.tfrm}")


# In[62]:


fld, wvl, foc = osp.lookup_fld_wvl_focus(0)


# In[63]:


ray_r2_f0 = trace_base(opm, [0, 1], fld, wvl)


# In[64]:


list_ray(ray_r2_f0)


# In[65]:


for i, rs in enumerate(ray_r2_f0[0]):
    rs = RaySeg(*rs)
    print(f"{i}: {rs.nrml}")


# In[66]:


opm.flip(e3)


# In[67]:


sm.list_model()


# In[68]:


apply_paraxial_vignetting(opm)


# In[69]:


layout_plt1 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False, do_draw_ray_fans=True,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[70]:


e1.tfrm, e2.tfrm, e3.tfrm


# In[71]:


idx1 = 3
idx2 = 6


# In[72]:


opm.flip(idx1, idx2)


# In[73]:


sm.list_model()


# In[74]:


layout_plt2 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[ ]:





# In[75]:


opm.flip(e2)


# In[76]:


sm.list_model()


# In[77]:


layout_plt3 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[78]:


e2.is_flipped


# In[79]:


ray_r2_f0_a = trace_base(opm, [0, 1], fld, wvl)


# In[80]:


list_ray(ray_r2_f0_a)


# In[81]:


sm.list_model()


# In[82]:


opm.flip(e2)
opm.flip(3,6)


# In[83]:


layout_plt4 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[84]:


fld, wvl, foc = osp.lookup_fld_wvl_focus(0)


# In[85]:


ray_r2_f0 = trace_base(opm, [0, 1], fld, wvl)


# In[86]:


list_ray(ray_r2_f0)


# In[87]:


for i, rs in enumerate(ray_r2_f0[0]):
    rs = RaySeg(*rs)
    print(f"{i}: {rs.nrml}")


# In[88]:


pt.list_tree_full()


# In[89]:


opm.flip(0, 7)


# In[ ]:




