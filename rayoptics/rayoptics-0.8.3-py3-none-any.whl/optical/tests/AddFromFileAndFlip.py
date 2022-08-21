#!/usr/bin/env python
# coding: utf-8

# In[2]:


# initialization
from rayoptics.environment import *
import anytree
from rayoptics.elem import parttree


# In[3]:


root_pth = Path(rayoptics.__file__).resolve().parent


# In[4]:


app = AppManager(None)
opm = app.model = OpticalModel()
sm = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']


# In[5]:


sm.gaps[0].thi = 1e10


# In[6]:


sm.list_model()


# In[7]:


osp.pupil.key, osp.pupil.value


# In[9]:


osp.pupil.value=22
opm.update_model()


# In[10]:


opm.add_from_file(root_pth/"codev/tests/CODV_32327.seq", t=10.)


# In[11]:


pt.list_tree_full()


# In[13]:


layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[14]:


sm.list_model()


# In[15]:


em.list_model()


# In[16]:


pt.list_tree()


# In[17]:


opm.save_model('Imported Doublet')


# In[ ]:





# In[18]:


opm.add_from_file(root_pth/"codev/tests/CODV_49664.seq", t=17.8)


# In[19]:


sm.list_model()


# In[20]:


listobj(sm.ifcs[7].profile)


# In[21]:


osp.field_of_view.key, osp.field_of_view.max_field()


# In[22]:


opm.update_model()


# In[23]:


pt.list_model()


# In[24]:


pm.first_order_data()


# In[25]:


pm.list_model()


# In[26]:


layout_plt0 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[27]:


em.list_model()


# In[28]:


pt.list_model()


# In[29]:


pt.list_tree()


# In[30]:


sm.list_model()


# In[31]:


for p in em.elements:
    print(f"{p.label}:\n{p.tfrm}")


# In[32]:


opm.save_model('Two Imported Doublets')


# In[33]:


opm_restored = open_model('Two Imported Doublets.roa')


# In[34]:


layout_plt1 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm_restored,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[35]:


opm_restored['pt'].list_tree_full()


# In[ ]:





# In[36]:


sm.list_model()


# In[37]:


for p in em.elements:
    print(f"{p.label}:\n{p.tfrm}")


# In[38]:


layout_plt1 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[39]:


sm.lcl_tfrms


# In[40]:


sm.gbl_tfrms


# In[41]:


pt.list_tree_full()


# In[42]:


opm.rebuild_from_seq()


# In[43]:


layout_plt2 = plt.figure(FigureClass=InteractiveLayout, opt_model=opm,
                        do_draw_rays=True, do_paraxial_layout=False).plot()


# In[44]:


pt.list_tree_full()


# In[45]:


sm.list_model()


# In[46]:


for p in em.elements:
    print(f"{p.label}:\n{p.tfrm}")


# ## Restore the just saved model to check roundtrip

# In[47]:


app = AppManager(None)
opm = app.model = OpticalModel()
sm = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']


# In[48]:


sm.gaps[0].thi = 1e10


# In[49]:


sm.list_model()


# In[50]:


osp.pupil.key, osp.pupil.value


# In[51]:


osp.pupil.value=22
#opm.update_model()


# In[52]:


opm.add_from_file('Imported Doublet.roa', t=10.)


# In[53]:


opm.update_model()


# In[54]:


opm['pt'].list_tree_full()


# In[55]:


pt.list_tree_full()


# In[56]:


opm2 = open_model('Imported Doublet.roa')


# In[57]:


opm2['pt'].list_tree_full()


# In[ ]:





# In[ ]:




