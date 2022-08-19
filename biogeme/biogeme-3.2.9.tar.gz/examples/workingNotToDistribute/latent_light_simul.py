#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.distributions as dist
import biogeme.results as res
import biogeme.messaging as msg
from biogeme.expressions import (
    Beta,
    Variable,
    Elem,
    bioNormalCdf,
    MonteCarlo,
    bioDraws,
)

logger = msg.bioMessage()
logger.setDebug()

# In[2]:


# Read the data
df = pd.read_csv('data_bio.txt', sep='\t')
database = db.Database('data', df)


# In[3]:


# The following statement allows you to use the names of the variable
# as Python variable.
#globals().update(database.variables)
n_enq = Variable('n_enq')
SEED1 = Variable('SEED1')
territoire = Variable('territoire')
VILLE = Variable('VILLE')
Aa1 = Variable('Aa1')
Aa1bis = Variable('Aa1bis')
Aa2 = Variable('Aa2')
Aa3 = Variable('Aa3')
Aa5 = Variable('Aa5')
Aa8 = Variable('Aa8')
Aa9 = Variable('Aa9')
Aa11 = Variable('Aa11')
Ab2 = Variable('Ab2')
Ab5 = Variable('Ab5')
Ac1 = Variable('Ac1')
Frontalier = Variable('Frontalier')
Ac13_relat = Variable('Ac13_relat')
Ac13_relat_agr = Variable('Ac13_relat_agr')
Ac16_agr = Variable('Ac16_agr')
ProfessionREP = Variable('ProfessionREP')
ProfessionREP1 = Variable('ProfessionREP1')
CSP_m = Variable('CSP_m')
CSP_p = Variable('CSP_p')
Francais = Variable('Francais')
Neerlandais = Variable('Neerlandais')
Espagnol = Variable('Espagnol')
Basque = Variable('Basque')
Aj1 = Variable('Aj1')
Aj5 = Variable('Aj5')
Aj14 = Variable('Aj14')
Db1 = Variable('Db1')
Db2 = Variable('Db2')
Db3 = Variable('Db3')
Db4 = Variable('Db4')
Db5 = Variable('Db5')
Cf11 = Variable('Cf11')
Cf12 = Variable('Cf12')
Cf13 = Variable('Cf13')
Cf14 = Variable('Cf14')
Cf15 = Variable('Cf15')
Cf16 = Variable('Cf16')
Cf21 = Variable('Cf21')
Cf22 = Variable('Cf22')
Cf23 = Variable('Cf23')
Cf24 = Variable('Cf24')
Cf25 = Variable('Cf25')
Cf26 = Variable('Cf26')
courses_rea = Variable('courses_rea')
shopping_rea = Variable('shopping_rea')
restauration_rea = Variable('restauration_rea')
culture_rea = Variable('culture_rea')
sport_rea = Variable('sport_rea')
courses_freq = Variable('courses_freq')
shopping_freq = Variable('shopping_freq')
restauration_freq = Variable('restauration_freq')
culture_freq = Variable('culture_freq')
sport_freq = Variable('sport_freq')
CSP = Variable('CSP')
mob_soc = Variable('mob_soc')
muni = Variable('muni')
migr_type = Variable('migr_type')
Q219 = Variable('Q219')
GI19 = Variable('GI19')
NBPERS19 = Variable('NBPERS19')
Distance_x = Variable('Distance_x')
Distance_y = Variable('Distance_y')
Distance = Variable('Distance')



# In[4]:


# Variables exclusion
exclude = (
    (courses_freq == -99)
    + (shopping_freq == -99)
    + (restauration_freq == -99)
    + (culture_freq == -99)
    + (sport_freq == -99)
    + (Aa11 == -99)
    + ((territoire == 2 + territoire == 4 + territoire == 6) * (Q219 == -99))
    + ((territoire == 4) * (Distance == -99))
) > 0
database.remove(exclude)


# In[5]:


# Random variables
latent = bioDraws('latent', 'NORMAL')


# In[6]:


# Definition of new variables
bsp = database.DefineVariable('bsp', (territoire == 1))
bfr = database.DefineVariable('bfr', (territoire == 2))
gch = database.DefineVariable('gch', (territoire == 3))
gfr = database.DefineVariable('gfr', (territoire == 4))
lbe = database.DefineVariable('lbe', (territoire == 5))
lfr = database.DefineVariable('lfr', (territoire == 6))

woman = database.DefineVariable('woman', (Aa2 == 2))

age = database.DefineVariable('age', (2020 - Aa3) / 10)

hh_fam = database.DefineVariable('hh_fam', (Aa5 == 2) + (Aa5 == 3))
hh_cpl = database.DefineVariable('hh_cpl', (Aa5 == 1))
hh_mono = database.DefineVariable('hh_mono', (Aa5 == 4))
hh_sgl = database.DefineVariable('hh_sgl', ((Aa5 == 5) + (Aa5 == 6)))
hh_na = database.DefineVariable('hh_na', (Aa5 == 7))

born_nat = database.DefineVariable('born_nat', (migr_type == 2))
born_xb = database.DefineVariable('born_xb', (migr_type == 3))
born_int = database.DefineVariable('born_int', (migr_type == 4))
born_here = database.DefineVariable('born_here', (migr_type == 1))

pass_xb = database.DefineVariable('pass_xb', (Aa11 > 2) * (Aa11 < 7))

years_xb = database.DefineVariable('years_xb', Ab5 / 100)

job = database.DefineVariable('job', (Ac1 < 3))
job_less = database.DefineVariable('job_less', (Ac1 > 2) * (Ac1 < 5))
job_ret = database.DefineVariable('job_ret', (Ac1 == 5))
job_stud = database.DefineVariable('job_stud', (Ac1 == 6))
job_oth = database.DefineVariable('job_oth', (Ac1 == 7))

work_xb = database.DefineVariable('work_xb', Frontalier == 1)

educ_lvl = database.DefineVariable('educ_lvl', Ac16_agr)
educ_na = database.DefineVariable('educ_na', (Ac16_agr == 8))
# educ_no = DefineVariable('educ_no', (Ac16_agr == 1), database)
# educ_obl = DefineVariable('educ_obl', (Ac16_agr == 2), database)
# educ_pro = DefineVariable('educ_pro', (Ac16_agr == 3), database)
# educ_bac = DefineVariable('educ_bac', (Ac16_agr == 4), database)
# educ_lic = DefineVariable('educ_lic', (Ac16_agr == 5), database)
# educ_mas = DefineVariable('educ_mas', (Ac16_agr == 6) + (Ac16_agr == 7), database)

spk_fr = database.DefineVariable('spk_fr', (Francais == 1))
spk_nl = database.DefineVariable('spk_nl', (Neerlandais == 1))
spk_sp = database.DefineVariable('spk_sp', (Espagnol == 1))
spk_bs = database.DefineVariable('spk_bs', (Basque == 1))
spk_xb = database.DefineVariable(
    'spk_xb',
    (bsp * spk_fr)
    + (bfr * spk_sp)
    + (lbe * (SEED1 < 200000) * spk_fr)
    + (lfr * spk_nl),
)

# inc_cat1 = DefineVariable('inc_cat1', (Ac13_relat == 1), database)
# inc_cat2 = DefineVariable('inc_cat2', (Ac13_relat == 2), database)
# inc_cat3 = DefineVariable('inc_cat3', (Ac13_relat == 3), database)
# inc_cat4 = DefineVariable('inc_cat4', (Ac13_relat == 4), database)
inc_agr = database.DefineVariable('inc_agr', Ac13_relat_agr)
inc_cat1_agr = database.DefineVariable('inc_cat1_agr', (Ac13_relat_agr == 1))
inc_cat2_agr = database.DefineVariable('inc_cat2_agr', (Ac13_relat_agr == 2))
inc_cat3_agr = database.DefineVariable('inc_cat3_agr', (Ac13_relat_agr == 3))
inc_cat4_agr = database.DefineVariable('inc_cat4_agr', (Ac13_relat_agr == 4))
inc_na = database.DefineVariable('inc_na', (Ac13_relat == 5))

csp_agr = database.DefineVariable('csp_agr', (CSP == 1))
csp_com = database.DefineVariable('csp_com', (CSP == 2))
csp_oth = database.DefineVariable('csp_oth', (CSP == 3))
csp_sup = database.DefineVariable('csp_sup', (CSP == 4))
csp_emp = database.DefineVariable('csp_emp', (CSP == 5))
csp_wrk = database.DefineVariable('csp_wrk', (CSP == 6))
csp_int = database.DefineVariable('csp_int', (CSP == 7))

soc_xb = database.DefineVariable('soc_xb', (Aj14 == 2))

mobsoc_asc = database.DefineVariable('mobsoc_asc', (mob_soc == 1))
mobsoc_na = database.DefineVariable('mobsoc_na', (mob_soc == 2))
mobsoc_desc = database.DefineVariable('mobsoc_desc', (mob_soc == 3))
mobsoc_stab = database.DefineVariable('mobsoc_stab', (mob_soc == 4))

children = database.DefineVariable('children', Aa8 > 0)
med_educ = database.DefineVariable(
    'med_educ', (Ac16_agr == 3) + (Ac16_agr == 4)
)
sup_educ = database.DefineVariable(
    'sup_educ', (Ac16_agr == 5) + (Ac16_agr == 6) + (Ac16_agr == 7)
)
xb_job = database.DefineVariable('xb_job', (1 - (Aa9 == 2)) * (Aj5 == 2))
owner = database.DefineVariable('owner', (Ab2 == 1))
xb_dwell = database.DefineVariable('xb_dwell', (1 - (Aa9 == 2)) * (Aj1 == 2))
# groc = DefineVariable('groc', activite == 1, database)
# shop = DefineVariable('shop', activite == 2, database)
# resto = DefineVariable('resto', activite == 3, database)
# cult = DefineVariable('cult', activite == 4, database)
# act = DefineVariable('act', activite == 5, database)

med_inc = database.DefineVariable('med_income (muni)', Q219 / 10000)
gini = database.DefineVariable('gini (muni)', GI19 / 10)
gini_na = database.DefineVariable('gini_na (muni)', (GI19 == -99))
nb_hab = database.DefineVariable('nb_habitants (muni)', NBPERS19 / 100000)
distance = database.DefineVariable('distance_border (muni)', Distance / 1000)

freq_g = database.DefineVariable(
    'freq_groceries',
    ((courses_rea == 2) * 8) + ((courses_rea == 1) * courses_freq),
)
freq_s = database.DefineVariable(
    'freq_shopping',
    ((shopping_rea == 2) * 8) + ((shopping_rea == 1) * shopping_freq),
)
freq_r = database.DefineVariable(
    'freq_resto',
    ((restauration_rea == 2) * 8)
    + ((restauration_rea == 1) * restauration_freq),
)
freq_c = database.DefineVariable(
    'freq_culture',
    ((culture_rea == 2) * 8) + ((culture_rea == 1) * culture_freq),
)
freq_a = database.DefineVariable(
    'freq_active',
    ((sport_rea == 2) * 8) + ((sport_rea == 1) * sport_freq),
)


# In[7]:


# LV parameters
intercept = Beta('lv_b0_intercept', 0, None, None, 0)

lv_woman = Beta('lv_b1_woman', 0, None, None, 0)

lv_age = Beta('lv_b4_age', 0, None, None, 0)

lv_educ = Beta('lv_b5_educ', 0, None, None, 0)

lv_born_xb = Beta('lv_b21_born_nghbcntry', 0, None, None, 0)
lv_born_int = Beta('lv_b22_born_othercntry', 0, None, None, 0)
lv_born_here = Beta('lv_b23_born_xbregion', 0, None, None, 0)

lv_bsp = Beta('lv_b31_bsp_spain', 0, None, None, 0)
lv_bfr = Beta('lv_b32_bsp_france', 0, None, None, 0)
lv_gch = Beta('lv_b33_gva_swiss', 0, None, None, 0)
lv_gfr = Beta('lv_b34_gva_france', 0, None, None, 0)
lv_lbe = Beta('lv_b35_lil_belgium', 0, None, None, 0)

# lv_inc_cat2 = Beta('lv_b61_inc_cat2_agr', 0, None, None, 0)
# lv_inc_cat3 = Beta('lv_b62_inc_cat3_agr', 0, None, None, 0)
# lv_inc_cat4 = Beta('lv_b63_inc_cat4_agr', 0, None, None, 0)
lv_inc = Beta('lv_b6_inc_agr', 0, None, None, 0)
lv_inc_na = Beta('lv_b64_inc_na', 0, None, None, 0)

lv_spk_xb = Beta('lv_b7_speak_neighbors', 0, None, None, 0)

lv_work_xb = Beta('lv_b8_xb_worker', 0, None, None, 0)

# lv_years_xb = Beta('lv_b9_number_years', 0, None, None, 0)

lv_csp_agr = Beta('lv_b91_csp_agriculture', 0, None, None, 0)
lv_csp_com = Beta('lv_b92_csp_commerce', 0, None, None, 0)
lv_csp_oth = Beta('lv_b93_csp_other', 0, None, None, 0)
lv_csp_sup = Beta('lv_b94_csp_manager', 0, None, None, 0)
lv_csp_emp = Beta('lv_b95_csp_employee', 0, None, None, 0)
lv_csp_wrk = Beta('lv_b96_csp_workers', 0, None, None, 0)
lv_csp_int = Beta('lv_b97_csp_intermediate', 0, None, None, 0)

lv_soc_xb = Beta('lv_c1_xb_habits', 0, None, None, 0)

lv_mobsoc_asc = Beta('lv_c21_socialmob_upward', 0, None, None, 0)
lv_mobsoc_desc = Beta('lv_c22_socialmob_downward', 0, None, None, 0)
lv_mobsoc_na = Beta('lv_c23_socialmob_na', 0, None, None, 0)

# lv_job = Beta('lv_c31_have_job', 0, None, None, 0)
# lv_job_less = Beta('lv_c32_jobless', 0, None, None, 0)
# lv_job_stud = Beta('lv_c32_student', 0, None, None, 0)
# lv_job_oth = Beta('lv_c33_other', 0, None, None, 0)

lv_gini = Beta('lv_gini', 0, None, None, 0)
lv_gini_na = Beta('lv_gini_na', 0, None, None, 0)

lv_gini_inc = Beta('lv_gini_inc', 0, None, None, 0)

lv_latent = Beta('lv_sigma', 1, None, None, 0)


# In[8]:


### Latent variable: structural equation
xb_support = (
    intercept
    + lv_woman * woman
    + lv_born_xb * born_xb
    + lv_born_int * born_int
    + lv_born_here * born_here
    + lv_bsp * bsp
    + lv_bfr * bfr
    + lv_gch * gch
    + lv_gfr * gfr
    + lv_lbe * lbe
    + lv_educ  # lv_job * job + lv_job_less * job_less + lv_job_stud * job_stud + lv_job_oth * job_oth + \
    * educ_lvl
    + lv_latent * latent
)


# In[9]:


### Measurement equations
INTER_DB1 = Beta('lv_ic1_transport', 0, None, None, 1)
INTER_DB2 = Beta('lv_ic2_school', 0, None, None, 0)
INTER_DB3 = Beta('lv_ic3_culture', 0, None, None, 0)
INTER_DB4 = Beta('lv_ic4_residential', 0, None, None, 0)
INTER_DB5 = Beta('lv_ic5_work', 0, None, None, 0)


# In[10]:


### Measurement equations
DB1 = Beta('lv_ib1_transport', 1, None, None, 1)
DB2 = Beta('lv_ib2_school', 1, None, None, 0)
DB3 = Beta('lv_ib3_culture', 1, None, None, 0)
DB4 = Beta('lv_ib4_residential', 1, None, None, 0)
DB5 = Beta('lv_ib5_work', 1, None, None, 0)


# In[11]:


### Measurement equations
MODEL_DB1 = INTER_DB1 + DB1 * xb_support
MODEL_DB2 = INTER_DB2 + DB2 * xb_support
MODEL_DB3 = INTER_DB3 + DB3 * xb_support
MODEL_DB4 = INTER_DB4 + DB4 * xb_support
MODEL_DB5 = INTER_DB5 + DB5 * xb_support


# In[12]:


### Measurement equations
SIGMA_DB1 = Beta('lv_is1_transport', 1, 1.0e-5, None, 1)
SIGMA_DB2 = Beta('lv_is2_school', 1, 1.0e-5, None, 0)
SIGMA_DB3 = Beta('lv_is3_culture', 1, 1.0e-5, None, 0)
SIGMA_DB4 = Beta('lv_is4_residential', 1, 1.0e-5, None, 0)
SIGMA_DB5 = Beta('lv_is5_work', 1, 1.0e-5, None, 0)


# In[13]:


### Measurement equations
chi_1 = Beta('lv_p1', 0.1, 1.0e-5, None, 0)
chi_2 = Beta('lv_p2', 0.2, 1.0e-5, None, 0)
nu_1 = -chi_1 - chi_2
nu_2 = -chi_1
nu_3 = chi_1
nu_4 = chi_1 + chi_2


# In[14]:


### Measurement equations
DB1_nu_1 = (nu_1 - MODEL_DB1) / SIGMA_DB1
DB1_nu_2 = (nu_2 - MODEL_DB1) / SIGMA_DB1
DB1_nu_3 = (nu_3 - MODEL_DB1) / SIGMA_DB1
DB1_nu_4 = (nu_4 - MODEL_DB1) / SIGMA_DB1
IndDB1 = {
    1: bioNormalCdf(DB1_nu_1),
    2: bioNormalCdf(DB1_nu_2) - bioNormalCdf(DB1_nu_1),
    3: bioNormalCdf(DB1_nu_3) - bioNormalCdf(DB1_nu_2),
    4: bioNormalCdf(DB1_nu_4) - bioNormalCdf(DB1_nu_3),
    5: 1 - bioNormalCdf(DB1_nu_4),
    -99: 1.0,
}

P_DB1 = Elem(IndDB1, Db1)


# In[15]:


### Measurement equations
DB2_nu_1 = (nu_1 - MODEL_DB2) / SIGMA_DB2
DB2_nu_2 = (nu_2 - MODEL_DB2) / SIGMA_DB2
DB2_nu_3 = (nu_3 - MODEL_DB2) / SIGMA_DB2
DB2_nu_4 = (nu_4 - MODEL_DB2) / SIGMA_DB2
IndDB2 = {
    1: bioNormalCdf(DB2_nu_1),
    2: bioNormalCdf(DB2_nu_2) - bioNormalCdf(DB2_nu_1),
    3: bioNormalCdf(DB2_nu_3) - bioNormalCdf(DB2_nu_2),
    4: bioNormalCdf(DB2_nu_4) - bioNormalCdf(DB2_nu_3),
    5: 1 - bioNormalCdf(DB2_nu_4),
    -99: 1.0,
}

P_DB2 = Elem(IndDB2, Db2)


# In[16]:


### Measurement equations
DB3_nu_1 = (nu_1 - MODEL_DB3) / SIGMA_DB3
DB3_nu_2 = (nu_2 - MODEL_DB3) / SIGMA_DB3
DB3_nu_3 = (nu_3 - MODEL_DB3) / SIGMA_DB3
DB3_nu_4 = (nu_4 - MODEL_DB3) / SIGMA_DB3
IndDB3 = {
    1: bioNormalCdf(DB3_nu_1),
    2: bioNormalCdf(DB3_nu_2) - bioNormalCdf(DB3_nu_1),
    3: bioNormalCdf(DB3_nu_3) - bioNormalCdf(DB3_nu_2),
    4: bioNormalCdf(DB3_nu_4) - bioNormalCdf(DB3_nu_3),
    5: 1 - bioNormalCdf(DB3_nu_4),
    -99: 1.0,
}

P_DB3 = Elem(IndDB3, Db3)


# In[17]:


### Measurement equations
DB4_nu_1 = (nu_1 - MODEL_DB4) / SIGMA_DB4
DB4_nu_2 = (nu_2 - MODEL_DB4) / SIGMA_DB4
DB4_nu_3 = (nu_3 - MODEL_DB4) / SIGMA_DB4
DB4_nu_4 = (nu_4 - MODEL_DB4) / SIGMA_DB4
IndDB4 = {
    1: bioNormalCdf(DB4_nu_1),
    2: bioNormalCdf(DB4_nu_2) - bioNormalCdf(DB4_nu_1),
    3: bioNormalCdf(DB4_nu_3) - bioNormalCdf(DB4_nu_2),
    4: bioNormalCdf(DB4_nu_4) - bioNormalCdf(DB4_nu_3),
    5: 1 - bioNormalCdf(DB4_nu_4),
    -99: 1.0,
}

P_DB4 = Elem(IndDB4, Db4)


# In[18]:


### Measurement equations
DB5_nu_1 = (nu_1 - MODEL_DB5) / SIGMA_DB5
DB5_nu_2 = (nu_2 - MODEL_DB5) / SIGMA_DB5
DB5_nu_3 = (nu_3 - MODEL_DB5) / SIGMA_DB5
DB5_nu_4 = (nu_4 - MODEL_DB5) / SIGMA_DB5
IndDB5 = {
    1: bioNormalCdf(DB5_nu_1),
    2: bioNormalCdf(DB5_nu_2) - bioNormalCdf(DB5_nu_1),
    3: bioNormalCdf(DB5_nu_3) - bioNormalCdf(DB5_nu_2),
    4: bioNormalCdf(DB5_nu_4) - bioNormalCdf(DB5_nu_3),
    5: 1 - bioNormalCdf(DB5_nu_4),
    -99: 1.0,
}

P_DB5 = Elem(IndDB5, Db5)


# In[19]:


# Parameters to be estimated
CST_g = Beta('A_CONSTANT_groceries', 0, None, None, 0)
CST_s = Beta('A_CONSTANT_shopping', 0, None, None, 0)
CST_r = Beta('A_CONSTANT_resto', 0, None, None, 0)
CST_c = Beta('A_CONSTANT_culture', 0, None, None, 0)
CST_a = Beta('A_CONSTANT_active', 0, None, None, 0)

WOMAN_g = Beta('B10_WOMAN_groceries', 0, None, None, 0)
WOMAN_s = Beta('B10_WOMAN_shopping', 0, None, None, 0)
WOMAN_r = Beta('B10_WOMAN_resto', 0, None, None, 0)
WOMAN_c = Beta('B10_WOMAN_culture', 0, None, None, 0)
WOMAN_a = Beta('B10_WOMAN_active', 0, None, None, 0)

AGE = Beta('B20_AGE', 0, None, None, 0)

# Effets du ménage très vagues, à réessayer une fois le modèle stabilisé.
# HH_FAM_g = Beta('B31_HOUSEHOLD_FAMILY_groceries', 0, None, None, 0)
# HH_CPL_g = Beta('B30_HOUSEHOLD_COUPLE_groceries', 0, None, None, 1)
# HH_SGL_g = Beta('B32_HOUSEHOLD_SINGLE_groceries', 0, None, None, 0)
# HH_MONO_g = Beta('B33_HOUSEHOLD_MONOPARENTAL_groceries', 0, None, None, 0)
# HH_FAM_s = Beta('B31_HOUSEHOLD_FAMILY_shopping', 0, None, None, 0)
# HH_CPL_s = Beta('B30_HOUSEHOLD_COUPLE_shopping', 0, None, None, 1)
# HH_SGL_s = Beta('B32_HOUSEHOLD_SINGLE_shopping', 0, None, None, 0)
# HH_MONO_s = Beta('B33_HOUSEHOLD_MONOPARENTAL_shopping', 0, None, None, 0)
# HH_FAM_r = Beta('B31_HOUSEHOLD_FAMILY_resto', 0, None, None, 0)
# HH_CPL_r = Beta('B30_HOUSEHOLD_COUPLE_resto', 0, None, None, 1)
# HH_SGL_r = Beta('B32_HOUSEHOLD_SINGLE_resto', 0, None, None, 0)
# HH_MONO_r = Beta('B33_HOUSEHOLD_MONOPARENTAL_resto', 0, None, None, 0)
# HH_FAM_c = Beta('B31_HOUSEHOLD_FAMILY_culture', 0, None, None, 0)
# HH_CPL_c = Beta('B30_HOUSEHOLD_COUPLE_culture', 0, None, None, 1)
# HH_SGL_c = Beta('B32_HOUSEHOLD_SINGLE_culture', 0, None, None, 0)
# HH_MONO_c = Beta('B33_HOUSEHOLD_MONOPARENTAL_culture', 0, None, None, 0)
# HH_FAM_a = Beta('B31_HOUSEHOLD_FAMILY_active', 0, None, None, 0)
# HH_CPL_a = Beta('B30_HOUSEHOLD_COUPLE_active', 0, None, None, 1)
# HH_SGL_a = Beta('B32_HOUSEHOLD_SINGLE_active', 0, None, None, 0)
# HH_MONO_a = Beta('B33_HOUSEHOLD_MONOPARENTAL_active', 0, None, None, 0)
# HH_NA = Beta('B33_HOUSEHOLD_NA', 0, None, None, 0)

BORN_XB = Beta('B41_BORN_NGHBCNTRY', 0, None, None, 0)
BORN_INT = Beta('B42_BORN_OTHERCNTRY', 0, None, None, 0)
BORN_HERE = Beta('B43_BORN_XBREGION', 0, None, None, 0)

PASS_XB_g = Beta('B51_PASSEPORT_NGHBCNTRY_groceries', 0, None, None, 0)
PASS_XB_s = Beta('B51_PASSEPORT_NGHBCNTRY_shopping', 0, None, None, 0)
PASS_XB_r = Beta('B51_PASSEPORT_NGHBCNTRY_resto', 0, None, None, 0)
PASS_XB_c = Beta('B51_PASSEPORT_NGHBCNTRY_culture', 0, None, None, 0)
PASS_XB_a = Beta('B51_PASSEPORT_NGHBCNTRY_active', 0, None, None, 0)

NB_YRS_g = Beta('B60_NUMBER_YEARS_groceries', 0, None, None, 0)
NB_YRS_s = Beta('B60_NUMBER_YEARS_shopping', 0, None, None, 0)
NB_YRS_r = Beta('B60_NUMBER_YEARS_resto', 0, None, None, 0)
NB_YRS_c = Beta('B60_NUMBER_YEARS_culture', 0, None, None, 0)
NB_YRS_a = Beta('B60_NUMBER_YEARS_active', 0, None, None, 0)

# Possibilité de réessayer par activité une fois le modèle arrêté.
JOB = Beta('B71_HAVE_JOB', 0, None, None, 0)
JOB_LESS = Beta('B72_JOBLESS', 0, None, None, 0)
JOB_STUD = Beta('B73_STUDENT', 0, None, None, 0)
# JOB_g = Beta('B71_HAVE_JOB_groceries', 0, None, None, 0)
# JOB_LESS_g = Beta('B71_JOBLESS_groceries', 0, None, None, 0)
# JOB_STUD_g = Beta('B71_STUDENT_groceries', 0, None, None, 0)
# JOB_s = Beta('B71_HAVE_JOB_shopping', 0, None, None, 0)
# JOB_LESS_s = Beta('B71_JOBLESS_shopping', 0, None, None, 0)
# JOB_STUD_s = Beta('B71_STUDENT_shopping', 0, None, None, 0)
# JOB_r = Beta('B71_HAVE_JOB_resto', 0, None, None, 0)
# JOB_LESS_r = Beta('B71_JOBLESS_resto', 0, None, None, 0)
# JOB_STUD_r = Beta('B71_STUDENT_resto', 0, None, None, 0)
# JOB_c = Beta('B71_HAVE_JOB_culture', 0, None, None, 0)
# JOB_LESS_c = Beta('B71_JOBLESS_culture', 0, None, None, 0)
# JOB_STUD_c = Beta('B71_STUDENT_culture', 0, None, None, 0)
# JOB_a = Beta('B71_HAVE_JOB_active', 0, None, None, 0)
# JOB_LESS_a = Beta('B71_JOBLESS_active', 0, None, None, 0)
# JOB_STUD_a = Beta('B71_STUDENT_active', 0, None, None, 0)
JOB_OTH = Beta('B71_OTHER', 0, None, None, 0)

# Aussi tester, pour les retraités, l'effet d'être un.e ancien.ne frontalier.e
WORK_XB_g = Beta('B81_XB_WORKER_groceries', 0, None, None, 0)
WORK_XB_s = Beta('B81_XB_WORKER_shopping', 0, None, None, 0)
WORK_XB_r = Beta('B81_XB_WORKER_resto', 0, None, None, 0)
WORK_XB_c = Beta('B81_XB_WORKER_culture', 0, None, None, 0)
WORK_XB_a = Beta('B81_XB_WORKER_active', 0, None, None, 0)

# EDUC_NA = Beta('B91_LEVEL_EDUCATION_NA', 0, None, None, 0)
# EDUC_LVL_g = Beta('B90_LEVEL_EDUCATION_groceries', 0, None, None, 0)
# EDUC_LVL_s = Beta('B90_LEVEL_EDUCATION_shopping', 0, None, None, 0)
# EDUC_LVL_r = Beta('B90_LEVEL_EDUCATION_resto', 0, None, None, 0)
# EDUC_LVL_c = Beta('B90_LEVEL_EDUCATION_culture', 0, None, None, 0)
# EDUC_LVL_a = Beta('B90_LEVEL_EDUCATION_active', 0, None, None, 0)

SPK_XB_g = Beta('C01_SPEAK_NEIGHBORS_groceries', 0, None, None, 0)
SPK_XB_s = Beta('C01_SPEAK_NEIGHBORS_shopping', 0, None, None, 0)
SPK_XB_r = Beta('C01_SPEAK_NEIGHBORS_resto', 0, None, None, 0)
SPK_XB_c = Beta('C01_SPEAK_NEIGHBORS_culture', 0, None, None, 0)
SPK_XB_a = Beta('C01_SPEAK_NEIGHBORS_active', 0, None, None, 0)

SPK_BS_g = Beta('C02_SPEAK_BASQUE_g', 0, None, None, 0)
SPK_BS_s = Beta('C02_SPEAK_BASQUE_s', 0, None, None, 0)
SPK_BS_r = Beta('C02_SPEAK_BASQUE_r', 0, None, None, 0)
SPK_BS_c = Beta('C02_SPEAK_BASQUE_c', 0, None, None, 0)
SPK_BS_a = Beta('C02_SPEAK_BASQUE_a', 0, None, None, 0)

# Possibilité de généraliser le terme une fois le modèle arrêté ; tester une interaction avec les terrains ?
# INC_CAT1 = Beta('C11_INC_CAT1', 0, None, None, 0)
# INC_CAT2 = Beta('C12_INC_CAT2', 0, None, None, 0)
# INC_CAT3 = Beta('C13_INC_CAT3', 0, None, None, 0)
# INC_CAT4 = Beta('C14_INC_CAT4', 0, None, None, 0)
INC_NA = Beta('C15_INC_NA', 0, None, None, 0)
# INC_CAT1_AGR = Beta('C11_INC_CAT1_AGR', 0, None, None, 0)
# INC_CAT2_AGR = Beta('C12_INC_CAT2_AGR', 0, None, None, 0)
# INC_CAT3_AGR = Beta('C13_INC_CAT3_AGR', 0, None, None, 0)
# INC_CAT4_AGR = Beta('C14_INC_CAT4_AGR', 0, None, None, 0)
INC_AGR_g = Beta('C10_INCOME_groceries', 0, None, None, 0)
INC_AGR_s = Beta('C10_INCOME_shopping', 0, None, None, 0)
INC_AGR_r = Beta('C10_INCOME_resto', 0, None, None, 0)
INC_AGR_c = Beta('C10_INCOME_culture', 0, None, None, 0)
INC_AGR_a = Beta('C10_INCOME_active', 0, None, None, 0)

# CSP_AGR_gs = Beta('C21_CSP_AGRICULTURE_gs', 0, None, None, 0)
# CSP_COM_gs = Beta('C22_CSP_COMMERCE_gs', 0, None, None, 0)
# CSP_OTH = Beta('C23_CSP_OTHER', 0, None, None, 0)
# CSP_SUP_gs = Beta('C24_CSP_MANAGER_gs', 0, None, None, 0)
# CSP_EMP_gs = Beta('C25_CSP_EMPLOYEE_gs', 0, None, None, 0)
# CSP_WRK_gs = Beta('C26_CSP_WORKERS_gs', 0, None, None, 0)
# CSP_AGR_rca = Beta('C21_CSP_AGRICULTURE_rca', 0, None, None, 0)
# CSP_COM_rca = Beta('C22_CSP_COMMERCE_rca', 0, None, None, 0)
# CSP_SUP_rca = Beta('C24_CSP_MANAGER_rca', 0, None, None, 0)
# CSP_EMP_rca = Beta('C25_CSP_EMPLOYEE_rca', 0, None, None, 0)
# CSP_WRK_rca = Beta('C26_CSP_WORKERS_rca', 0, None, None, 0)
# CSP_INT = Beta('C27_CSP_INTERMEDIATE', 0, None, None, 0)

BSP = Beta('C21_BSQ_SPAIN', 0, None, None, 0)
BFR = Beta('C22_BSQ_FRANCE', 0, None, None, 0)
GCH = Beta('C23_GVA_SWISS', 0, None, None, 0)
GFR = Beta('C24_GVA_FRANCE', 0, None, None, 0)
LBE = Beta('C25_LIL_BELGIUM', 0, None, None, 0)

GINI_g = Beta('C30_GINI_groceries (MUNI)', 0, None, None, 0)
GINI_s = Beta('C30_GINI_shopping (MUNI)', 0, None, None, 0)
GINI_r = Beta('C30_GINI_resto (MUNI)', 0, None, None, 0)
GINI_c = Beta('C30_GINI_culture (MUNI)', 0, None, None, 0)

GINI_NA = Beta('C31_GINI_NA (MUNI)', 0, None, None, 0)

GINI_INC_g = Beta('C35_GINI_x_INC_groceries (MUNI)', 0, None, None, 0)
GINI_INC_s = Beta('C35_GINI_x_INC_shopping (MUNI)', 0, None, None, 0)
GINI_INC_r = Beta('C35_GINI_x_INC_resto (MUNI)', 0, None, None, 0)
GINI_INC_c = Beta('C35_GINI_x_INC_culture (MUNI)', 0, None, None, 0)

DISTANCE_g = Beta('C40_DISTANCE_BORDER_groceries (MUNI)', 0, None, None, 0)
DISTANCE_s = Beta('C40_DISTANCE_BORDER_shopping (MUNI)', 0, None, None, 0)
DISTANCE_r = Beta('C40_DISTANCE_BORDER_resto (MUNI)', 0, None, None, 0)
DISTANCE_c = Beta('C40_DISTANCE_BORDER_culture (MUNI)', 0, None, None, 0)
DISTANCE_a = Beta('C40_DISTANCE_BORDER_active (MUNI)', 0, None, None, 0)

# XB_SUPPORT = Beta('C40_XB_SUPPORT (LV)', 1, None, None, 0)
XB_SUPPORT_g = Beta('C40_XB_SUPPORT_groceries (LV)', 1, None, None, 0)
XB_SUPPORT_s = Beta('C40_XB_SUPPORT_shopping (LV)', 1, None, None, 0)
XB_SUPPORT_r = Beta('C40_XB_SUPPORT_resto (LV)', 1, None, None, 0)
XB_SUPPORT_c = Beta('C40_XB_SUPPORT_culture (LV)', 1, None, None, 0)
XB_SUPPORT_a = Beta('C40_XB_SUPPORT_active (LV)', 1, None, None, 0)

LBE_INT_r = Beta('C55_LIL_BELGIUM_INT_resto (LV)', 0.1, None, None, 0)
LBE_INT_c = Beta('C55_LIL_BELGIUM_INT_culture (LV)', 0.1, None, None, 0)
BFR_INT_s = Beta('C52_BSQ_FRANCE_INT_shopping (LV)', 0.1, None, None, 0)
BSP_INT_g = Beta('C51_BSQ_SPAIN_INT_groceries (LV)', 0.1, None, None, 0)
GCH_INT_a = Beta('C53_GVA_SWISS_INT_active (LV)', 0.1, None, None, 0)


# In[20]:


# Parameters for the ordered logit.
tau_1 = Beta('tau_1', 0, None, 0, 1)
tau_delta_2 = Beta('tau_delta_2', 0.5, 0, None, 0)
tau_delta_3 = Beta('tau_delta_3', 0.5, 0, None, 0)
tau_delta_4 = Beta('tau_delta_4', 0.5, 0, None, 0)
tau_delta_5 = Beta('tau_delta_5', 0.5, 0, None, 0)
tau_delta_6 = Beta('tau_delta_6', 0.5, 0, None, 0)

delta_1 = tau_1
delta_2 = tau_1 + tau_delta_2
delta_3 = tau_1 + tau_delta_2 + tau_delta_3
delta_4 = tau_1 + tau_delta_2 + tau_delta_3 + tau_delta_4
delta_5 = tau_1 + tau_delta_2 + tau_delta_3 + tau_delta_4 + tau_delta_5
delta_6 = (
    tau_1 + tau_delta_2 + tau_delta_3 + tau_delta_4 + tau_delta_5 + tau_delta_6
)


# In[21]:


# Utility
U_g = (
    CST_g
    + BORN_HERE * born_here
    + BORN_XB * born_xb
    + BORN_INT * born_int
    + JOB * job
    + JOB_LESS * job_less
    + JOB_STUD * job_stud
    + JOB_OTH * job_oth
    + job * WORK_XB_g * work_xb
    + BSP * bsp
    + BFR * bfr
    + LBE * lbe
    + GCH * gch
    + GFR * gfr
    + XB_SUPPORT_g * xb_support
)  # + BSP_INT_g * bsp * xb_support)

U_s = (
    CST_s
    + WOMAN_s * woman
    + AGE * age
    + BORN_HERE * born_here
    + BORN_XB * born_xb
    + BORN_INT * born_int
    + JOB * job
    + JOB_LESS * job_less
    + JOB_STUD * job_stud
    + JOB_OTH * job_oth
    + BSP * bsp
    + BFR * bfr
    + LBE * lbe
    + GCH * gch
    + GFR * gfr
    + XB_SUPPORT_s * xb_support
)  # + BFR_INT_s * bfr * xb_support)

U_r = (
    CST_r
    + WOMAN_r * woman
    + BORN_HERE * born_here
    + BORN_XB * born_xb
    + BORN_INT * born_int
    + JOB * job
    + JOB_LESS * job_less
    + JOB_STUD * job_stud
    + JOB_OTH * job_oth
    + job * WORK_XB_r * work_xb
    + BSP * bsp
    + BFR * bfr
    + LBE * lbe
    + GCH * gch
    + GFR * gfr
    + XB_SUPPORT_r * xb_support
)  # + LBE_INT_r * lbe * xb_support)

U_c = (
    CST_c
    + WOMAN_c * woman
    + BORN_HERE * born_here
    + BORN_XB * born_xb
    + BORN_INT * born_int
    + JOB * job
    + JOB_LESS * job_less
    + JOB_STUD * job_stud
    + JOB_OTH * job_oth
    + job * WORK_XB_c * work_xb
    + BSP * bsp
    + BFR * bfr
    + LBE * lbe
    + GCH * gch
    + GFR * gfr
    + XB_SUPPORT_c * xb_support
)  # + LBE_INT_c * lbe * xb_support)

U_a = (
    CST_a
    + WOMAN_a * woman
    + BORN_HERE * born_here
    + BORN_XB * born_xb
    + BORN_INT * born_int
    + JOB * job
    + JOB_LESS * job_less
    + JOB_STUD * job_stud
    + JOB_OTH * job_oth
    + job * WORK_XB_a * work_xb
    + BSP * bsp
    + BFR * bfr
    + LBE * lbe
    + GCH * gch
    + GFR * gfr
    + XB_SUPPORT_a * xb_support
)  # + GCH_INT_a * gch * xb_support)


# In[22]:


# Associate each discrete indicator with an interval.

ChoiceProba_g = {
    1: 1 - dist.logisticcdf(U_g - delta_1),
    2: dist.logisticcdf(U_g - delta_1) - dist.logisticcdf(U_g - delta_2),
    3: dist.logisticcdf(U_g - delta_2) - dist.logisticcdf(U_g - delta_3),
    4: dist.logisticcdf(U_g - delta_3) - dist.logisticcdf(U_g - delta_4),
    5: dist.logisticcdf(U_g - delta_4) - dist.logisticcdf(U_g - delta_5),
    6: dist.logisticcdf(U_g - delta_5) - dist.logisticcdf(U_g - delta_6),
    7: dist.logisticcdf(U_g - delta_6),
    8: 1.0,
}

# P_g = Elem(ChoiceProba_g, freq_g)

ChoiceProba_s = {
    1: 1 - dist.logisticcdf(U_s - delta_1),
    2: dist.logisticcdf(U_s - delta_1) - dist.logisticcdf(U_s - delta_2),
    3: dist.logisticcdf(U_s - delta_2) - dist.logisticcdf(U_s - delta_3),
    4: dist.logisticcdf(U_s - delta_3) - dist.logisticcdf(U_s - delta_4),
    5: dist.logisticcdf(U_s - delta_4) - dist.logisticcdf(U_s - delta_5),
    6: dist.logisticcdf(U_s - delta_5) - dist.logisticcdf(U_s - delta_6),
    7: dist.logisticcdf(U_s - delta_6),
    8: 1.0,
}

# P_s = Elem(ChoiceProba_s, freq_s)

ChoiceProba_r = {
    1: 1 - dist.logisticcdf(U_r - delta_1),
    2: dist.logisticcdf(U_r - delta_1) - dist.logisticcdf(U_r - delta_2),
    3: dist.logisticcdf(U_r - delta_2) - dist.logisticcdf(U_r - delta_3),
    4: dist.logisticcdf(U_r - delta_3) - dist.logisticcdf(U_r - delta_4),
    5: dist.logisticcdf(U_r - delta_4) - dist.logisticcdf(U_r - delta_5),
    6: dist.logisticcdf(U_r - delta_5) - dist.logisticcdf(U_r - delta_6),
    7: dist.logisticcdf(U_r - delta_6),
    8: 1.0,
}

# P_r = Elem(ChoiceProba_r, freq_r)

ChoiceProba_c = {
    1: 1 - dist.logisticcdf(U_c - delta_1),
    2: dist.logisticcdf(U_c - delta_1) - dist.logisticcdf(U_c - delta_2),
    3: dist.logisticcdf(U_c - delta_2) - dist.logisticcdf(U_c - delta_3),
    4: dist.logisticcdf(U_c - delta_3) - dist.logisticcdf(U_c - delta_4),
    5: dist.logisticcdf(U_c - delta_4) - dist.logisticcdf(U_c - delta_5),
    6: dist.logisticcdf(U_c - delta_5) - dist.logisticcdf(U_c - delta_6),
    7: dist.logisticcdf(U_c - delta_6),
    8: 1.0,
}

# P_c = Elem(ChoiceProba_c, freq_c)

ChoiceProba_a = {
    1: 1 - dist.logisticcdf(U_a - delta_1),
    2: dist.logisticcdf(U_a - delta_1) - dist.logisticcdf(U_a - delta_2),
    3: dist.logisticcdf(U_a - delta_2) - dist.logisticcdf(U_a - delta_3),
    4: dist.logisticcdf(U_a - delta_3) - dist.logisticcdf(U_a - delta_4),
    5: dist.logisticcdf(U_a - delta_4) - dist.logisticcdf(U_a - delta_5),
    6: dist.logisticcdf(U_a - delta_5) - dist.logisticcdf(U_a - delta_6),
    7: dist.logisticcdf(U_a - delta_6),
    8: 1.0,
}

# P_a = Elem(ChoiceProba_a, freq_a)


# In[23]:


# The choice model is a logit, with availability conditions
#prob_g1 = MonteCarlo(Elem(ChoiceProba_g, 1))
prob_g1 = MonteCarlo(U_g)
print(f'%%%%%%% {prob_g1} %%%%%%%%%%%%%%%')

# prob_g2 = Elem(ChoiceProba_g, 2)
# prob_g3 = Elem(ChoiceProba_g, 3)
# prob_g4 = Elem(ChoiceProba_g, 4)
# prob_g5 = Elem(ChoiceProba_g, 5)
# prob_g6 = Elem(ChoiceProba_g, 6)
# prob_g7 = Elem(ChoiceProba_g, 7)


# In[27]:


simulate = {'Prob. groceries never': prob_g1}  # ,
#'Prob. groceries less often': prob_g2,
#'Prob. groceries 1x/month': prob_g3,
#'Prob. groceries 2,3x/month': prob_g4,
#'Prob. groceries 1x/week': prob_g5,
#'Prob. groceries 2,3x/week': prob_g6,
#'Prob. groceries everyday': prob_g7}


# In[28]:


biogeme = bio.BIOGEME(database, simulate, numberOfDraws=400)
biogeme.modelName = 'latent_light_simul'


# In[23]:


betas = biogeme.freeBetaNames
results = res.bioResults(pickleFile='latent_light.pickle')
betaValues = results.getBetaValues()


# In[24]:


simulatedValues = biogeme.simulate(betaValues)


# In[25]:


print(simulatedValues.describe())


# In[26]:


simulatedValues


# In[ ]:
