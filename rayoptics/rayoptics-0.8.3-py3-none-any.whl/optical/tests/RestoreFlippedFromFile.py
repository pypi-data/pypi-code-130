#!/usr/bin/env python
# coding: utf-8

# In[2]:


# initialization
from rayoptics.environment import *
import anytree
from rayoptics.elem import parttree


# In[3]:


def list_vertices(opm, idxe1, idxe2, idxs1, idxs2):
    for e in opm['em'].elements[idxe1:idxe2]:
        print(f"{e.label:4s}({e.reference_idx()}): {e.tfrm[1]}  is_flipped = {e.is_flipped}")
    sm = opm['sm']
    labels = sm.surface_label_list()
    print("sm.gbl_tfrms")
    for i, tfrm in enumerate(sm.gbl_tfrms[idxs1:idxs2], start=idxs1):
        print(f"{labels[i]:4s}: {tfrm[1]}")


# In[4]:


root_pth = Path(rayoptics.__file__).resolve().parent


# In[59]:


opm_restored = open_model(root_pth/'optical/tests/Two Imported Doublets Flipped.roa')


# In[60]:


opm_restored['sm'].list_model()


# In[61]:


opm_restored['pt'].list_model()


# In[62]:


opm_restored['em'].list_model()


# In[63]:


opm_restored['em'].list_elements()


# In[65]:


list_vertices(opm_restored, 2, 6, 1, 9)


# In[66]:


ce1 = opm_restored['pt'].obj_by_name('CE1')
ce2 = opm_restored['pt'].obj_by_name('CE2')   # em.elements[4]


# In[67]:


print(f"{ce1.label}: is_flipped: {ce1.is_flipped}")


# In[68]:


print(f"{ce2.label}: is_flipped: {ce2.is_flipped}")


# In[69]:


layout_plt2 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm_restored,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[70]:


opm_restored['pt'].list_tree_full()


# In[ ]:





# In[ ]:




