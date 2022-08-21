#!/usr/bin/env python
# coding: utf-8

# In[2]:


# initialization
from rayoptics.environment import *
import anytree
from rayoptics.elem import parttree
import itertools
from rayoptics.raytr.trace import apply_paraxial_vignetting

import pprint
import json
# In[3]:


def flip(opt_model, *args, **kwargs):
    sm = opt_model['seq_model']
    em = opt_model['ele_model']
    pt = opt_model['part_tree']
    if isinstance(args[0], int):
        idx1 = args[0]
        idx2 = args[1]
    elif isinstance(args[0], elements.Part):
        e = args[0]
        e.flip()
        idx_list = [sm.ifcs.index(ifc) for ifc in e.interface_list()]
        sm.flip(idx_list[0], idx_list[-1])
        parttree.sync_part_tree_on_update(em, sm, pt.root_node)


# In[4]:


def list_vertices(opm, *args):
    if len(args) == 4:
        idxe1, idxe2, idxs1, idxs2 = args
    else:
        idxe1, idxe2, idxs1, idxs2 = 4, 11, 2, 8
    for e in opm['em'].elements[idxe1:idxe2]:
        print(f"{e.label:4s}({e.reference_idx()}): {e.tfrm[1]}  is_flipped = {e.is_flipped}")
    sm = opm['sm']
    labels = sm.surface_label_list()
    print("sm.gbl_tfrms")
    for i, tfrm in enumerate(sm.gbl_tfrms[idxs1:idxs2], start=idxs1):
        print(f"{labels[i]:4s}: {tfrm[1]}")


# In[5]:


import transforms3d as t3d


# In[6]:


beta180 = np.array([0, np.deg2rad(180), 0])
rot_around_y = t3d.euler.euler2mat(*beta180); rot_around_y


# In[7]:


alpha180 = np.array([np.deg2rad(180), 0, 0])
rot_around_x = t3d.euler.euler2mat(*alpha180); rot_around_x


# In[8]:


rot_around_x = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
rot_around_y = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])


# In[9]:


root_pth = Path(rayoptics.__file__).resolve().parent


# In[10]:


opm = open_model(root_pth/"codev/tests/folded_lenses.seq")
sm = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']
ss = opm['specsheet']


# In[11]:


sm.list_sg()


# In[12]:


pt.list_model()


# In[13]:


list_vertices(opm)


# In[14]:


layout_plt0 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()


# ## Flip a range of sequential model interfaces
# 
# input range for sequence to be flipped

# In[15]:


idx1, idx2 = 3, 6


# In[16]:


opm.flip(idx1, idx2)


# In[17]:


pt.list_tree_full()


# In[18]:


layout_plt1 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False, do_draw_ray_fans=False,
                        refresh_gui=None).plot()


# In[19]:


list_vertices(opm)


# In[20]:


opm.flip(idx1, idx2)


# In[21]:


idx1, idx2


# In[22]:


sm.list_model()


# In[23]:


list_vertices(opm)


# In[24]:


layout_plt2 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[25]:


e4=pt.obj_by_name('E4')


# In[26]:


opm.flip(e4)


# In[27]:


layout_plt3 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[28]:


opm.flip(e4)


# In[29]:


layout_plt4 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[30]:


e2=pt.obj_by_name('E2')


# In[31]:


opm.flip(e2)


# In[32]:


layout_plt5 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[33]:


opm.flip(e2)


# In[34]:


layout_plt6 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[35]:


opm.add_assembly_from_seq(3, 6, label='ASM1')
opm.add_assembly_from_seq(8, 11, label='ASM2')
opm.update_model()


# In[36]:


sm.list_model()
em.list_model()
em.elements


# In[37]:


list_vertices(opm, 4, 12, 2, 8)


# In[38]:


asm1=pt.obj_by_name('ASM1')


# In[39]:


opm.flip(asm1)


# In[40]:


list_vertices(opm, 4, 12, 2, 8)


# In[41]:


layout_plt7 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[42]:


opm.flip(asm1)


# In[43]:


list_vertices(opm, 4, 12, 2, 8)


# In[44]:


layout_plt8 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[45]:


list_vertices(opm, 11, 19, 7, 13)


# In[46]:


asm2=pt.obj_by_name('ASM2')


# In[47]:


opm.flip(asm2)


# In[48]:


list_vertices(opm, 11, 19, 7, 13)


# In[49]:


layout_plt9 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
#layout_plt.update_data()
#layout_plt.plot()


# In[50]:


opm.flip(asm2)


# In[51]:


list_vertices(opm, 11, 19, 7, 13)


# In[52]:


layout_plt10 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False,
                        refresh_gui=None).plot()
