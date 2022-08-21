#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().run_line_magic('matplotlib', 'widget')
#%matplotlib inline


# In[2]:


# use standard rayoptics environment
from rayoptics.environment import *


# In[3]:


import rayoptics.seq.twoconicmirrors as tcm

def apply_conics(opt_model, fct, parax_model):
    cc_m1, cc_m2 = fct(parax_model)
    opt_model.seq_model.ifcs[1].profile.cc = cc_m1
    opt_model.seq_model.ifcs[2].profile.cc = cc_m2
    opt_model.update_model()


# In[13]:


root_pth = Path(rayoptics.__file__).resolve().parent


# In[14]:


app = AppManager(None)


# # Create a new model

# In[15]:


opm = app.model = OpticalModel()

sm  = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']


# ## Define first order aperture and field for system

# In[16]:


osp.pupil = PupilSpec(osp, key=['image', 'f/#'], value=10.)
osp.field_of_view = FieldSpec(osp, key=['image', 'height'], flds=[0., 0.5])


# ## Define interface and gap data for the sequential model

# In[17]:


sm.gaps[0].thi=1e10


# In[18]:


opm.add_mirror(label='M1', profile=Conic, c=-0.01, t=-33.)
opm.add_mirror(label='M2', profile=Conic, c=-0.01, t=50.)


# In[19]:

# ## Update the model

# In[ ]:


opm.update_model()


# In[ ]:

print('update model')
sm.list_model()
em.list_model()
opm.list_part_tree()


# In[ ]:


opm.part_tree.root_node.children[1]


# In[ ]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False).plot()
