import sys #line:18
import time #line:19
import copy #line:20
from time import strftime #line:22
from time import gmtime #line:23
import pandas as pd #line:25
import numpy #line:26
class cleverminer :#line:28
    version_string ="1.0.1"#line:30
    def __init__ (OOO0O0OOOO000OOO0 ,**OO0OO000OOOO000OO ):#line:32
        OOO0O0OOOO000OOO0 ._print_disclaimer ()#line:33
        OOO0O0OOOO000OOO0 .stats ={'total_cnt':0 ,'total_ver':0 ,'total_valid':0 ,'control_number':0 ,'start_prep_time':time .time (),'end_prep_time':time .time (),'start_proc_time':time .time (),'end_proc_time':time .time ()}#line:42
        OOO0O0OOOO000OOO0 .options ={'max_categories':100 ,'max_rules':None ,'optimizations':True }#line:46
        OOO0O0OOOO000OOO0 .kwargs =None #line:47
        if len (OO0OO000OOOO000OO )>0 :#line:48
            OOO0O0OOOO000OOO0 .kwargs =OO0OO000OOOO000OO #line:49
        OOO0O0OOOO000OOO0 .verbosity ={}#line:50
        OOO0O0OOOO000OOO0 .verbosity ['debug']=False #line:51
        OOO0O0OOOO000OOO0 .verbosity ['print_rules']=False #line:52
        OOO0O0OOOO000OOO0 .verbosity ['print_hashes']=True #line:53
        OOO0O0OOOO000OOO0 .verbosity ['last_hash_time']=0 #line:54
        OOO0O0OOOO000OOO0 .verbosity ['hint']=False #line:55
        if "opts"in OO0OO000OOOO000OO :#line:56
            OOO0O0OOOO000OOO0 ._set_opts (OO0OO000OOOO000OO .get ("opts"))#line:57
        if "opts"in OO0OO000OOOO000OO :#line:58
            if "verbose"in OO0OO000OOOO000OO .get ('opts'):#line:59
                if OO0OO000OOOO000OO ['verbose'].upper ()=='FULL':#line:60
                    OOO0O0OOOO000OOO0 .verbosity ['debug']=True #line:61
                    OOO0O0OOOO000OOO0 .verbosity ['print_rules']=True #line:62
                    OOO0O0OOOO000OOO0 .verbosity ['print_hashes']=False #line:63
                    OOO0O0OOOO000OOO0 .verbosity ['hint']=True #line:64
                elif OO0OO000OOOO000OO ['verbose'].upper ()=='RULES':#line:65
                    OOO0O0OOOO000OOO0 .verbosity ['debug']=False #line:66
                    OOO0O0OOOO000OOO0 .verbosity ['print_rules']=True #line:67
                    OOO0O0OOOO000OOO0 .verbosity ['print_hashes']=True #line:68
                    OOO0O0OOOO000OOO0 .verbosity ['hint']=True #line:69
                elif OO0OO000OOOO000OO ['verbose'].upper ()=='HINT':#line:70
                    OOO0O0OOOO000OOO0 .verbosity ['debug']=False #line:71
                    OOO0O0OOOO000OOO0 .verbosity ['print_rules']=False #line:72
                    OOO0O0OOOO000OOO0 .verbosity ['print_hashes']=True #line:73
                    OOO0O0OOOO000OOO0 .verbosity ['last_hash_time']=0 #line:74
                    OOO0O0OOOO000OOO0 .verbosity ['hint']=True #line:75
        OOO0O0OOOO000OOO0 ._is_py310 =sys .version_info [0 ]>=4 or (sys .version_info [0 ]>=3 and sys .version_info [1 ]>=10 )#line:76
        if not (OOO0O0OOOO000OOO0 ._is_py310 ):#line:77
            print ("Warning: Python 3.10+ NOT detected. You should upgrade to Python 3.10 or greater to get better performance")#line:78
        else :#line:79
            if (OOO0O0OOOO000OOO0 .verbosity ['debug']):#line:80
                print ("Python 3.10+ detected.")#line:81
        OOO0O0OOOO000OOO0 ._initialized =False #line:82
        OOO0O0OOOO000OOO0 ._init_data ()#line:83
        OOO0O0OOOO000OOO0 ._init_task ()#line:84
        if len (OO0OO000OOOO000OO )>0 :#line:85
            if "df"in OO0OO000OOOO000OO :#line:86
                OOO0O0OOOO000OOO0 ._prep_data (OO0OO000OOOO000OO .get ("df"))#line:87
            else :#line:88
                print ("Missing dataframe. Cannot initialize.")#line:89
                OOO0O0OOOO000OOO0 ._initialized =False #line:90
                return #line:91
            OO0000OO0OOOO0OOO =OO0OO000OOOO000OO .get ("proc",None )#line:92
            if not (OO0000OO0OOOO0OOO ==None ):#line:93
                OOO0O0OOOO000OOO0 ._calculate (**OO0OO000OOOO000OO )#line:94
            else :#line:96
                if OOO0O0OOOO000OOO0 .verbosity ['debug']:#line:97
                    print ("INFO: just initialized")#line:98
        OOO0O0OOOO000OOO0 ._initialized =True #line:99
    def _set_opts (OOOO0O00OOO00O000 ,OO00000OOO0000O00 ):#line:101
        if "no_optimizations"in OO00000OOO0000O00 :#line:102
            OOOO0O00OOO00O000 .options ['optimizations']=not (OO00000OOO0000O00 ['no_optimizations'])#line:103
            print ("No optimization will be made.")#line:104
        if "max_rules"in OO00000OOO0000O00 :#line:105
            OOOO0O00OOO00O000 .options ['max_rules']=OO00000OOO0000O00 ['max_rules']#line:106
        if "max_categories"in OO00000OOO0000O00 :#line:107
            OOOO0O00OOO00O000 .options ['max_categories']=OO00000OOO0000O00 ['max_categories']#line:108
            if OOOO0O00OOO00O000 .verbosity ['debug']==True :#line:109
                print (f"Maximum number of categories set to {OOOO0O00OOO00O000.options['max_categories']}")#line:110
    def _init_data (OO000O0OOO00O0O00 ):#line:113
        OO000O0OOO00O0O00 .data ={}#line:115
        OO000O0OOO00O0O00 .data ["varname"]=[]#line:116
        OO000O0OOO00O0O00 .data ["catnames"]=[]#line:117
        OO000O0OOO00O0O00 .data ["vtypes"]=[]#line:118
        OO000O0OOO00O0O00 .data ["dm"]=[]#line:119
        OO000O0OOO00O0O00 .data ["rows_count"]=int (0 )#line:120
        OO000O0OOO00O0O00 .data ["data_prepared"]=0 #line:121
    def _init_task (OOOO0O0O0000OO000 ):#line:123
        if "opts"in OOOO0O0O0000OO000 .kwargs :#line:125
            OOOO0O0O0000OO000 ._set_opts (OOOO0O0O0000OO000 .kwargs .get ("opts"))#line:126
        OOOO0O0O0000OO000 .cedent ={'cedent_type':'none','defi':{},'num_cedent':0 ,'trace_cedent':[],'trace_cedent_asindata':[],'traces':[],'generated_string':'','rule':{},'filter_value':int (0 )}#line:136
        OOOO0O0O0000OO000 .task_actinfo ={'proc':'','cedents_to_do':[],'cedents':[]}#line:140
        OOOO0O0O0000OO000 .rulelist =[]#line:141
        OOOO0O0O0000OO000 .stats ['total_cnt']=0 #line:143
        OOOO0O0O0000OO000 .stats ['total_valid']=0 #line:144
        OOOO0O0O0000OO000 .stats ['control_number']=0 #line:145
        OOOO0O0O0000OO000 .result ={}#line:146
        OOOO0O0O0000OO000 ._opt_base =None #line:147
        OOOO0O0O0000OO000 ._opt_relbase =None #line:148
        OOOO0O0O0000OO000 ._opt_base1 =None #line:149
        OOOO0O0O0000OO000 ._opt_relbase1 =None #line:150
        OOOO0O0O0000OO000 ._opt_base2 =None #line:151
        OOOO0O0O0000OO000 ._opt_relbase2 =None #line:152
        O00OO0O00OOO0O0O0 =None #line:153
        if not (OOOO0O0O0000OO000 .kwargs ==None ):#line:154
            O00OO0O00OOO0O0O0 =OOOO0O0O0000OO000 .kwargs .get ("quantifiers",None )#line:155
            if not (O00OO0O00OOO0O0O0 ==None ):#line:156
                for O0OO000OOOOO000OO in O00OO0O00OOO0O0O0 .keys ():#line:157
                    if O0OO000OOOOO000OO .upper ()=='BASE':#line:158
                        OOOO0O0O0000OO000 ._opt_base =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:159
                    if O0OO000OOOOO000OO .upper ()=='RELBASE':#line:160
                        OOOO0O0O0000OO000 ._opt_relbase =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:161
                    if (O0OO000OOOOO000OO .upper ()=='FRSTBASE')|(O0OO000OOOOO000OO .upper ()=='BASE1'):#line:162
                        OOOO0O0O0000OO000 ._opt_base1 =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:163
                    if (O0OO000OOOOO000OO .upper ()=='SCNDBASE')|(O0OO000OOOOO000OO .upper ()=='BASE2'):#line:164
                        OOOO0O0O0000OO000 ._opt_base2 =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:165
                    if (O0OO000OOOOO000OO .upper ()=='FRSTRELBASE')|(O0OO000OOOOO000OO .upper ()=='RELBASE1'):#line:166
                        OOOO0O0O0000OO000 ._opt_relbase1 =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:167
                    if (O0OO000OOOOO000OO .upper ()=='SCNDRELBASE')|(O0OO000OOOOO000OO .upper ()=='RELBASE2'):#line:168
                        OOOO0O0O0000OO000 ._opt_relbase2 =O00OO0O00OOO0O0O0 .get (O0OO000OOOOO000OO )#line:169
            else :#line:170
                print ("Warning: no quantifiers found. Optimization will not take place (1)")#line:171
        else :#line:172
            print ("Warning: no quantifiers found. Optimization will not take place (2)")#line:173
    def mine (OOOO0000000O0000O ,**OOO0O00OOOOOOO00O ):#line:176
        if not (OOOO0000000O0000O ._initialized ):#line:177
            print ("Class NOT INITIALIZED. Please call constructor with dataframe first")#line:178
            return #line:179
        OOOO0000000O0000O .kwargs =None #line:180
        if len (OOO0O00OOOOOOO00O )>0 :#line:181
            OOOO0000000O0000O .kwargs =OOO0O00OOOOOOO00O #line:182
        OOOO0000000O0000O ._init_task ()#line:183
        if len (OOO0O00OOOOOOO00O )>0 :#line:184
            O000O00OO000O0O0O =OOO0O00OOOOOOO00O .get ("proc",None )#line:185
            if not (O000O00OO000O0O0O ==None ):#line:186
                OOOO0000000O0000O ._calc_all (**OOO0O00OOOOOOO00O )#line:187
            else :#line:188
                print ("Rule mining procedure missing")#line:189
    def _get_ver (O00000O00OOOO000O ):#line:192
        return O00000O00OOOO000O .version_string #line:193
    def _print_disclaimer (OO00OOO0O00OO00O0 ):#line:195
        print (f"Cleverminer version {OO00OOO0O00OO00O0._get_ver()}. Note: This version is for personal and educational use only. If you need PRO version (support, fixing structures for compactibility in future versions for production deployment, additional development, licensing of commercial use of subroutines used), feel free to ask authors. Most of these functionalities are maintained in best-effort, as soon as this project is at given conditions for free use and rapid development is needed, they cannot be guaranteed.")#line:197
    def _prep_data (O0OOO0OOOO00OO000 ,OOOO00O0000OO0O00 ):#line:203
        print ("Starting data preparation ...")#line:204
        O0OOO0OOOO00OO000 ._init_data ()#line:205
        O0OOO0OOOO00OO000 .stats ['start_prep_time']=time .time ()#line:206
        O0OOO0OOOO00OO000 .data ["rows_count"]=OOOO00O0000OO0O00 .shape [0 ]#line:207
        for OOO0OOO0OO0O0OOOO in OOOO00O0000OO0O00 .select_dtypes (exclude =['category']).columns :#line:208
            OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ]=OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ].apply (str )#line:209
        OO0OOOOO0O0000O00 =pd .DataFrame .from_records ([(OOOO000OOOO0000OO ,OOOO00O0000OO0O00 [OOOO000OOOO0000OO ].nunique ())for OOOO000OOOO0000OO in OOOO00O0000OO0O00 .columns ],columns =['Column_Name','Num_Unique']).sort_values (by =['Num_Unique'])#line:211
        if O0OOO0OOOO00OO000 .verbosity ['hint']:#line:212
            print ("Quick profile of input data: unique value counts are:")#line:213
            print (OO0OOOOO0O0000O00 )#line:214
            for OOO0OOO0OO0O0OOOO in OOOO00O0000OO0O00 .columns :#line:215
                if OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ].nunique ()<O0OOO0OOOO00OO000 .options ['max_categories']:#line:216
                    OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ]=OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ].astype ('category')#line:217
                else :#line:218
                    print (f"WARNING: attribute {OOO0OOO0OO0O0OOOO} has more than {O0OOO0OOOO00OO000.options['max_categories']} values, will be ignored.\r\n If you haven't set maximum number of categories and you really need more categories and you know what you are doing, please use max_categories option to increase allowed number of categories.")#line:219
                    del OOOO00O0000OO0O00 [OOO0OOO0OO0O0OOOO ]#line:220
        print ("Encoding columns into bit-form...")#line:221
        OO0OO00O00O0OOO0O =0 #line:222
        OO0O00O0OO00O0OOO =0 #line:223
        for O0000O0O0OOOO0O00 in OOOO00O0000OO0O00 :#line:224
            if O0OOO0OOOO00OO000 .verbosity ['debug']:#line:226
                print ('Column: '+O0000O0O0OOOO0O00 )#line:227
            O0OOO0OOOO00OO000 .data ["varname"].append (O0000O0O0OOOO0O00 )#line:228
            OOO0OOOOOOOOO00OO =pd .get_dummies (OOOO00O0000OO0O00 [O0000O0O0OOOO0O00 ])#line:229
            O00O000O00OO00OO0 =0 #line:230
            if (OOOO00O0000OO0O00 .dtypes [O0000O0O0OOOO0O00 ].name =='category'):#line:231
                O00O000O00OO00OO0 =1 #line:232
            O0OOO0OOOO00OO000 .data ["vtypes"].append (O00O000O00OO00OO0 )#line:233
            OO0O000000O0O0OO0 =0 #line:236
            OOOOO0OOO0O0O0OOO =[]#line:237
            O0000OOOO0OO0000O =[]#line:238
            for O0O0OOOO0O0OO000O in OOO0OOOOOOOOO00OO :#line:240
                if O0OOO0OOOO00OO000 .verbosity ['debug']:#line:242
                    print ('....category : '+str (O0O0OOOO0O0OO000O )+" @ "+str (time .time ()))#line:243
                OOOOO0OOO0O0O0OOO .append (O0O0OOOO0O0OO000O )#line:244
                OO0O0O0O0O0O0OO00 =int (0 )#line:245
                OO0OOO0O0OOOO0O0O =OOO0OOOOOOOOO00OO [O0O0OOOO0O0OO000O ].values #line:246
                OOO00OO00OOOOOO00 =numpy .packbits (OO0OOO0O0OOOO0O0O ,bitorder ='little')#line:248
                OO0O0O0O0O0O0OO00 =int .from_bytes (OOO00OO00OOOOOO00 ,byteorder ='little')#line:249
                O0000OOOO0OO0000O .append (OO0O0O0O0O0O0OO00 )#line:250
                OO0O000000O0O0OO0 +=1 #line:268
                OO0O00O0OO00O0OOO +=1 #line:269
            O0OOO0OOOO00OO000 .data ["catnames"].append (OOOOO0OOO0O0O0OOO )#line:271
            O0OOO0OOOO00OO000 .data ["dm"].append (O0000OOOO0OO0000O )#line:272
        print ("Encoding columns into bit-form...done")#line:274
        if O0OOO0OOOO00OO000 .verbosity ['hint']:#line:275
            print (f"List of attributes for analysis is: {O0OOO0OOOO00OO000.data['varname']}")#line:276
            print (f"List of category names for individual attributes is : {O0OOO0OOOO00OO000.data['catnames']}")#line:277
        if O0OOO0OOOO00OO000 .verbosity ['debug']:#line:278
            print (f"List of vtypes is (all should be 1) : {O0OOO0OOOO00OO000.data['vtypes']}")#line:279
        O0OOO0OOOO00OO000 .data ["data_prepared"]=1 #line:281
        print ("Data preparation finished.")#line:282
        if O0OOO0OOOO00OO000 .verbosity ['debug']:#line:283
            print ('Number of variables : '+str (len (O0OOO0OOOO00OO000 .data ["dm"])))#line:284
            print ('Total number of categories in all variables : '+str (OO0O00O0OO00O0OOO ))#line:285
        O0OOO0OOOO00OO000 .stats ['end_prep_time']=time .time ()#line:286
        if O0OOO0OOOO00OO000 .verbosity ['debug']:#line:287
            print ('Time needed for data preparation : ',str (O0OOO0OOOO00OO000 .stats ['end_prep_time']-O0OOO0OOOO00OO000 .stats ['start_prep_time']))#line:288
    def _bitcount (OO0OO00O000OOO0OO ,OO00OOO000000OOO0 ):#line:290
        O00OO0OO0OOO0OO00 =None #line:291
        if (OO0OO00O000OOO0OO ._is_py310 ):#line:292
            O00OO0OO0OOO0OO00 =OO00OOO000000OOO0 .bit_count ()#line:293
        else :#line:294
            O00OO0OO0OOO0OO00 =bin (OO00OOO000000OOO0 ).count ("1")#line:295
        return O00OO0OO0OOO0OO00 #line:296
    def _verifyCF (OOO0OO0OO00OOO000 ,_OO00O0O00O0OO0000 ):#line:299
        OO0OO000OO00O000O =OOO0OO0OO00OOO000 ._bitcount (_OO00O0O00O0OO0000 )#line:300
        OOOO0OO000OOOO0O0 =[]#line:301
        OOOO000000O0O0O00 =[]#line:302
        OO000OO000O0O00OO =0 #line:303
        O00OOO0OO0O0OOO00 =0 #line:304
        O0O0O000O0O0O0O00 =0 #line:305
        OO0OOOO0O00O00O0O =0 #line:306
        OOO00OOO0O00OO0O0 =0 #line:307
        O0OOO000OOO0OO0OO =0 #line:308
        O000O00000O0OO0OO =0 #line:309
        OO0000O0000000O0O =0 #line:310
        OOOOOOO00OO0OOOO0 =0 #line:311
        O0OOO0O0O0OOOOO0O =OOO0OO0OO00OOO000 .data ["dm"][OOO0OO0OO00OOO000 .data ["varname"].index (OOO0OO0OO00OOO000 .kwargs .get ('target'))]#line:312
        for O0OOOOOOOO0O00OO0 in range (len (O0OOO0O0O0OOOOO0O )):#line:313
            O00OOO0OO0O0OOO00 =OO000OO000O0O00OO #line:314
            OO000OO000O0O00OO =OOO0OO0OO00OOO000 ._bitcount (_OO00O0O00O0OO0000 &O0OOO0O0O0OOOOO0O [O0OOOOOOOO0O00OO0 ])#line:315
            OOOO0OO000OOOO0O0 .append (OO000OO000O0O00OO )#line:316
            if O0OOOOOOOO0O00OO0 >0 :#line:317
                if (OO000OO000O0O00OO >O00OOO0OO0O0OOO00 ):#line:318
                    if (O0O0O000O0O0O0O00 ==1 ):#line:319
                        OO0000O0000000O0O +=1 #line:320
                    else :#line:321
                        OO0000O0000000O0O =1 #line:322
                    if OO0000O0000000O0O >OO0OOOO0O00O00O0O :#line:323
                        OO0OOOO0O00O00O0O =OO0000O0000000O0O #line:324
                    O0O0O000O0O0O0O00 =1 #line:325
                    O0OOO000OOO0OO0OO +=1 #line:326
                if (OO000OO000O0O00OO <O00OOO0OO0O0OOO00 ):#line:327
                    if (O0O0O000O0O0O0O00 ==-1 ):#line:328
                        OOOOOOO00OO0OOOO0 +=1 #line:329
                    else :#line:330
                        OOOOOOO00OO0OOOO0 =1 #line:331
                    if OOOOOOO00OO0OOOO0 >OOO00OOO0O00OO0O0 :#line:332
                        OOO00OOO0O00OO0O0 =OOOOOOO00OO0OOOO0 #line:333
                    O0O0O000O0O0O0O00 =-1 #line:334
                    O000O00000O0OO0OO +=1 #line:335
                if (OO000OO000O0O00OO ==O00OOO0OO0O0OOO00 ):#line:336
                    O0O0O000O0O0O0O00 =0 #line:337
                    OOOOOOO00OO0OOOO0 =0 #line:338
                    OO0000O0000000O0O =0 #line:339
        OO000O00O00OO000O =True #line:342
        for OOO0O0O0000OOOO0O in OOO0OO0OO00OOO000 .quantifiers .keys ():#line:343
            if OOO0O0O0000OOOO0O .upper ()=='BASE':#line:344
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OO0OO000OO00O000O )#line:345
            if OOO0O0O0000OOOO0O .upper ()=='RELBASE':#line:346
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OO0OO000OO00O000O *1.0 /OOO0OO0OO00OOO000 .data ["rows_count"])#line:347
            if OOO0O0O0000OOOO0O .upper ()=='S_UP':#line:348
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OO0OOOO0O00O00O0O )#line:349
            if OOO0O0O0000OOOO0O .upper ()=='S_DOWN':#line:350
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OOO00OOO0O00OO0O0 )#line:351
            if OOO0O0O0000OOOO0O .upper ()=='S_ANY_UP':#line:352
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OO0OOOO0O00O00O0O )#line:353
            if OOO0O0O0000OOOO0O .upper ()=='S_ANY_DOWN':#line:354
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=OOO00OOO0O00OO0O0 )#line:355
            if OOO0O0O0000OOOO0O .upper ()=='MAX':#line:356
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=max (OOOO0OO000OOOO0O0 ))#line:357
            if OOO0O0O0000OOOO0O .upper ()=='MIN':#line:358
                OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=min (OOOO0OO000OOOO0O0 ))#line:359
            if OOO0O0O0000OOOO0O .upper ()=='RELMAX':#line:360
                if sum (OOOO0OO000OOOO0O0 )>0 :#line:361
                    OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=max (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 ))#line:362
                else :#line:363
                    OO000O00O00OO000O =False #line:364
            if OOO0O0O0000OOOO0O .upper ()=='RELMAX_LEQ':#line:365
                if sum (OOOO0OO000OOOO0O0 )>0 :#line:366
                    OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )>=max (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 ))#line:367
                else :#line:368
                    OO000O00O00OO000O =False #line:369
            if OOO0O0O0000OOOO0O .upper ()=='RELMIN':#line:370
                if sum (OOOO0OO000OOOO0O0 )>0 :#line:371
                    OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )<=min (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 ))#line:372
                else :#line:373
                    OO000O00O00OO000O =False #line:374
            if OOO0O0O0000OOOO0O .upper ()=='RELMIN_LEQ':#line:375
                if sum (OOOO0OO000OOOO0O0 )>0 :#line:376
                    OO000O00O00OO000O =OO000O00O00OO000O and (OOO0OO0OO00OOO000 .quantifiers .get (OOO0O0O0000OOOO0O )>=min (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 ))#line:377
                else :#line:378
                    OO000O00O00OO000O =False #line:379
        O0OO0OO000000O000 ={}#line:380
        if OO000O00O00OO000O ==True :#line:381
            OOO0OO0OO00OOO000 .stats ['total_valid']+=1 #line:383
            O0OO0OO000000O000 ["base"]=OO0OO000OO00O000O #line:384
            O0OO0OO000000O000 ["rel_base"]=OO0OO000OO00O000O *1.0 /OOO0OO0OO00OOO000 .data ["rows_count"]#line:385
            O0OO0OO000000O000 ["s_up"]=OO0OOOO0O00O00O0O #line:386
            O0OO0OO000000O000 ["s_down"]=OOO00OOO0O00OO0O0 #line:387
            O0OO0OO000000O000 ["s_any_up"]=O0OOO000OOO0OO0OO #line:388
            O0OO0OO000000O000 ["s_any_down"]=O000O00000O0OO0OO #line:389
            O0OO0OO000000O000 ["max"]=max (OOOO0OO000OOOO0O0 )#line:390
            O0OO0OO000000O000 ["min"]=min (OOOO0OO000OOOO0O0 )#line:391
            if sum (OOOO0OO000OOOO0O0 )>0 :#line:394
                O0OO0OO000000O000 ["rel_max"]=max (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 )#line:395
                O0OO0OO000000O000 ["rel_min"]=min (OOOO0OO000OOOO0O0 )*1.0 /sum (OOOO0OO000OOOO0O0 )#line:396
            else :#line:397
                O0OO0OO000000O000 ["rel_max"]=0 #line:398
                O0OO0OO000000O000 ["rel_min"]=0 #line:399
            O0OO0OO000000O000 ["hist"]=OOOO0OO000OOOO0O0 #line:400
        return OO000O00O00OO000O ,O0OO0OO000000O000 #line:402
    def _verify4ft (O000OOOOOOOO000OO ,_OOOO000000OO0O0O0 ):#line:404
        O000000OO00O0O0O0 ={}#line:405
        OO0O0O000O00O000O =0 #line:406
        for OOO00O0OOOO00OO00 in O000OOOOOOOO000OO .task_actinfo ['cedents']:#line:407
            O000000OO00O0O0O0 [OOO00O0OOOO00OO00 ['cedent_type']]=OOO00O0OOOO00OO00 ['filter_value']#line:409
            OO0O0O000O00O000O =OO0O0O000O00O000O +1 #line:410
        O00O0000000O00000 =O000OOOOOOOO000OO ._bitcount (O000000OO00O0O0O0 ['ante']&O000000OO00O0O0O0 ['succ']&O000000OO00O0O0O0 ['cond'])#line:412
        OOO00O00OOOO0O000 =None #line:413
        OOO00O00OOOO0O000 =0 #line:414
        if O00O0000000O00000 >0 :#line:423
            OOO00O00OOOO0O000 =O000OOOOOOOO000OO ._bitcount (O000000OO00O0O0O0 ['ante']&O000000OO00O0O0O0 ['succ']&O000000OO00O0O0O0 ['cond'])*1.0 /O000OOOOOOOO000OO ._bitcount (O000000OO00O0O0O0 ['ante']&O000000OO00O0O0O0 ['cond'])#line:424
        O0OOOO00O0OOOOOOO =1 <<O000OOOOOOOO000OO .data ["rows_count"]#line:426
        O0000O00O0OO0OO00 =O000OOOOOOOO000OO ._bitcount (O000000OO00O0O0O0 ['ante']&O000000OO00O0O0O0 ['succ']&O000000OO00O0O0O0 ['cond'])#line:427
        OOO0OO00000OO00O0 =O000OOOOOOOO000OO ._bitcount (O000000OO00O0O0O0 ['ante']&~(O0OOOO00O0OOOOOOO |O000000OO00O0O0O0 ['succ'])&O000000OO00O0O0O0 ['cond'])#line:428
        OOO00O0OOOO00OO00 =O000OOOOOOOO000OO ._bitcount (~(O0OOOO00O0OOOOOOO |O000000OO00O0O0O0 ['ante'])&O000000OO00O0O0O0 ['succ']&O000000OO00O0O0O0 ['cond'])#line:429
        O0OO0O0O0OO000OO0 =O000OOOOOOOO000OO ._bitcount (~(O0OOOO00O0OOOOOOO |O000000OO00O0O0O0 ['ante'])&~(O0OOOO00O0OOOOOOO |O000000OO00O0O0O0 ['succ'])&O000000OO00O0O0O0 ['cond'])#line:430
        O0OOO0OO0OO000OOO =0 #line:431
        if (O0000O00O0OO0OO00 +OOO0OO00000OO00O0 )*(O0000O00O0OO0OO00 +OOO00O0OOOO00OO00 )>0 :#line:432
            O0OOO0OO0OO000OOO =O0000O00O0OO0OO00 *(O0000O00O0OO0OO00 +OOO0OO00000OO00O0 +OOO00O0OOOO00OO00 +O0OO0O0O0OO000OO0 )/(O0000O00O0OO0OO00 +OOO0OO00000OO00O0 )/(O0000O00O0OO0OO00 +OOO00O0OOOO00OO00 )-1 #line:433
        else :#line:434
            O0OOO0OO0OO000OOO =None #line:435
        O0O0O0OOOO000O0O0 =0 #line:436
        if (O0000O00O0OO0OO00 +OOO0OO00000OO00O0 )*(O0000O00O0OO0OO00 +OOO00O0OOOO00OO00 )>0 :#line:437
            O0O0O0OOOO000O0O0 =1 -O0000O00O0OO0OO00 *(O0000O00O0OO0OO00 +OOO0OO00000OO00O0 +OOO00O0OOOO00OO00 +O0OO0O0O0OO000OO0 )/(O0000O00O0OO0OO00 +OOO0OO00000OO00O0 )/(O0000O00O0OO0OO00 +OOO00O0OOOO00OO00 )#line:438
        else :#line:439
            O0O0O0OOOO000O0O0 =None #line:440
        OO000O0O00OO00000 =True #line:441
        for O00O0OO0O0OOOO0O0 in O000OOOOOOOO000OO .quantifiers .keys ():#line:442
            if O00O0OO0O0OOOO0O0 .upper ()=='BASE':#line:443
                OO000O0O00OO00000 =OO000O0O00OO00000 and (O000OOOOOOOO000OO .quantifiers .get (O00O0OO0O0OOOO0O0 )<=O00O0000000O00000 )#line:444
            if O00O0OO0O0OOOO0O0 .upper ()=='RELBASE':#line:445
                OO000O0O00OO00000 =OO000O0O00OO00000 and (O000OOOOOOOO000OO .quantifiers .get (O00O0OO0O0OOOO0O0 )<=O00O0000000O00000 *1.0 /O000OOOOOOOO000OO .data ["rows_count"])#line:446
            if (O00O0OO0O0OOOO0O0 .upper ()=='PIM')or (O00O0OO0O0OOOO0O0 .upper ()=='CONF'):#line:447
                OO000O0O00OO00000 =OO000O0O00OO00000 and (O000OOOOOOOO000OO .quantifiers .get (O00O0OO0O0OOOO0O0 )<=OOO00O00OOOO0O000 )#line:448
            if O00O0OO0O0OOOO0O0 .upper ()=='AAD':#line:449
                if O0OOO0OO0OO000OOO !=None :#line:450
                    OO000O0O00OO00000 =OO000O0O00OO00000 and (O000OOOOOOOO000OO .quantifiers .get (O00O0OO0O0OOOO0O0 )<=O0OOO0OO0OO000OOO )#line:451
                else :#line:452
                    OO000O0O00OO00000 =False #line:453
            if O00O0OO0O0OOOO0O0 .upper ()=='BAD':#line:454
                if O0O0O0OOOO000O0O0 !=None :#line:455
                    OO000O0O00OO00000 =OO000O0O00OO00000 and (O000OOOOOOOO000OO .quantifiers .get (O00O0OO0O0OOOO0O0 )<=O0O0O0OOOO000O0O0 )#line:456
                else :#line:457
                    OO000O0O00OO00000 =False #line:458
            OOOOOOO0OOO0O00OO ={}#line:459
        if OO000O0O00OO00000 ==True :#line:460
            O000OOOOOOOO000OO .stats ['total_valid']+=1 #line:462
            OOOOOOO0OOO0O00OO ["base"]=O00O0000000O00000 #line:463
            OOOOOOO0OOO0O00OO ["rel_base"]=O00O0000000O00000 *1.0 /O000OOOOOOOO000OO .data ["rows_count"]#line:464
            OOOOOOO0OOO0O00OO ["conf"]=OOO00O00OOOO0O000 #line:465
            OOOOOOO0OOO0O00OO ["aad"]=O0OOO0OO0OO000OOO #line:466
            OOOOOOO0OOO0O00OO ["bad"]=O0O0O0OOOO000O0O0 #line:467
            OOOOOOO0OOO0O00OO ["fourfold"]=[O0000O00O0OO0OO00 ,OOO0OO00000OO00O0 ,OOO00O0OOOO00OO00 ,O0OO0O0O0OO000OO0 ]#line:468
        return OO000O0O00OO00000 ,OOOOOOO0OOO0O00OO #line:472
    def _verifysd4ft (OOO0O000O000OOOO0 ,_OO00OOO00O000O0O0 ):#line:474
        O00OO00000O0OOO0O ={}#line:475
        O0O0OOO0000O0O00O =0 #line:476
        for OOO00O0O00O0O0O0O in OOO0O000O000OOOO0 .task_actinfo ['cedents']:#line:477
            O00OO00000O0OOO0O [OOO00O0O00O0O0O0O ['cedent_type']]=OOO00O0O00O0O0O0O ['filter_value']#line:479
            O0O0OOO0000O0O00O =O0O0OOO0000O0O00O +1 #line:480
        OO00000OO0O000OOO =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:482
        OO0000OOO0O0OOO0O =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:483
        OO00OO00OOOO00OOO =None #line:484
        OOOO0OO0OOO0OO0OO =0 #line:485
        O0O00O0OOO0000000 =0 #line:486
        if OO00000OO0O000OOO >0 :#line:495
            OOOO0OO0OOO0OO0OO =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])*1.0 /OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:496
        if OO0000OOO0O0OOO0O >0 :#line:497
            O0O00O0OOO0000000 =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])*1.0 /OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:498
        O0OOOO0OO0O000000 =1 <<OOO0O000O000OOOO0 .data ["rows_count"]#line:500
        OOOO000O00OO0O000 =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:501
        O0OO0OOO0O0000OO0 =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['succ'])&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:502
        O00OOOO0O00000OO0 =OOO0O000O000OOOO0 ._bitcount (~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['ante'])&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:503
        O0O0O0OOO0000O00O =OOO0O000O000OOOO0 ._bitcount (~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['ante'])&~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['succ'])&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['frst'])#line:504
        OO0O0OO0O0O00OOO0 =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:505
        OOOO0OO000O00OOO0 =OOO0O000O000OOOO0 ._bitcount (O00OO00000O0OOO0O ['ante']&~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['succ'])&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:506
        OOO00OO0O0000OO0O =OOO0O000O000OOOO0 ._bitcount (~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['ante'])&O00OO00000O0OOO0O ['succ']&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:507
        O0O0OOOOOO00OO00O =OOO0O000O000OOOO0 ._bitcount (~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['ante'])&~(O0OOOO0OO0O000000 |O00OO00000O0OOO0O ['succ'])&O00OO00000O0OOO0O ['cond']&O00OO00000O0OOO0O ['scnd'])#line:508
        OOO0O00OO000OOOO0 =True #line:509
        for OOOOO0OO0O0O0O000 in OOO0O000O000OOOO0 .quantifiers .keys ():#line:510
            if (OOOOO0OO0O0O0O000 .upper ()=='FRSTBASE')|(OOOOO0OO0O0O0O000 .upper ()=='BASE1'):#line:511
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OO00000OO0O000OOO )#line:512
            if (OOOOO0OO0O0O0O000 .upper ()=='SCNDBASE')|(OOOOO0OO0O0O0O000 .upper ()=='BASE2'):#line:513
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OO0000OOO0O0OOO0O )#line:514
            if (OOOOO0OO0O0O0O000 .upper ()=='FRSTRELBASE')|(OOOOO0OO0O0O0O000 .upper ()=='RELBASE1'):#line:515
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OO00000OO0O000OOO *1.0 /OOO0O000O000OOOO0 .data ["rows_count"])#line:516
            if (OOOOO0OO0O0O0O000 .upper ()=='SCNDRELBASE')|(OOOOO0OO0O0O0O000 .upper ()=='RELBASE2'):#line:517
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OO0000OOO0O0OOO0O *1.0 /OOO0O000O000OOOO0 .data ["rows_count"])#line:518
            if (OOOOO0OO0O0O0O000 .upper ()=='FRSTPIM')|(OOOOO0OO0O0O0O000 .upper ()=='PIM1')|(OOOOO0OO0O0O0O000 .upper ()=='FRSTCONF')|(OOOOO0OO0O0O0O000 .upper ()=='CONF1'):#line:519
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OOOO0OO0OOO0OO0OO )#line:520
            if (OOOOO0OO0O0O0O000 .upper ()=='SCNDPIM')|(OOOOO0OO0O0O0O000 .upper ()=='PIM2')|(OOOOO0OO0O0O0O000 .upper ()=='SCNDCONF')|(OOOOO0OO0O0O0O000 .upper ()=='CONF2'):#line:521
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=O0O00O0OOO0000000 )#line:522
            if (OOOOO0OO0O0O0O000 .upper ()=='DELTAPIM')|(OOOOO0OO0O0O0O000 .upper ()=='DELTACONF'):#line:523
                OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OOOO0OO0OOO0OO0OO -O0O00O0OOO0000000 )#line:524
            if (OOOOO0OO0O0O0O000 .upper ()=='RATIOPIM')|(OOOOO0OO0O0O0O000 .upper ()=='RATIOCONF'):#line:527
                if (O0O00O0OOO0000000 >0 ):#line:528
                    OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )<=OOOO0OO0OOO0OO0OO *1.0 /O0O00O0OOO0000000 )#line:529
                else :#line:530
                    OOO0O00OO000OOOO0 =False #line:531
            if (OOOOO0OO0O0O0O000 .upper ()=='RATIOPIM_LEQ')|(OOOOO0OO0O0O0O000 .upper ()=='RATIOCONF_LEQ'):#line:532
                if (O0O00O0OOO0000000 >0 ):#line:533
                    OOO0O00OO000OOOO0 =OOO0O00OO000OOOO0 and (OOO0O000O000OOOO0 .quantifiers .get (OOOOO0OO0O0O0O000 )>=OOOO0OO0OOO0OO0OO *1.0 /O0O00O0OOO0000000 )#line:534
                else :#line:535
                    OOO0O00OO000OOOO0 =False #line:536
        O000OO0O0000O0O00 ={}#line:537
        if OOO0O00OO000OOOO0 ==True :#line:538
            OOO0O000O000OOOO0 .stats ['total_valid']+=1 #line:540
            O000OO0O0000O0O00 ["base1"]=OO00000OO0O000OOO #line:541
            O000OO0O0000O0O00 ["base2"]=OO0000OOO0O0OOO0O #line:542
            O000OO0O0000O0O00 ["rel_base1"]=OO00000OO0O000OOO *1.0 /OOO0O000O000OOOO0 .data ["rows_count"]#line:543
            O000OO0O0000O0O00 ["rel_base2"]=OO0000OOO0O0OOO0O *1.0 /OOO0O000O000OOOO0 .data ["rows_count"]#line:544
            O000OO0O0000O0O00 ["conf1"]=OOOO0OO0OOO0OO0OO #line:545
            O000OO0O0000O0O00 ["conf2"]=O0O00O0OOO0000000 #line:546
            O000OO0O0000O0O00 ["deltaconf"]=OOOO0OO0OOO0OO0OO -O0O00O0OOO0000000 #line:547
            if (O0O00O0OOO0000000 >0 ):#line:548
                O000OO0O0000O0O00 ["ratioconf"]=OOOO0OO0OOO0OO0OO *1.0 /O0O00O0OOO0000000 #line:549
            else :#line:550
                O000OO0O0000O0O00 ["ratioconf"]=None #line:551
            O000OO0O0000O0O00 ["fourfold1"]=[OOOO000O00OO0O000 ,O0OO0OOO0O0000OO0 ,O00OOOO0O00000OO0 ,O0O0O0OOO0000O00O ]#line:552
            O000OO0O0000O0O00 ["fourfold2"]=[OO0O0OO0O0O00OOO0 ,OOOO0OO000O00OOO0 ,OOO00OO0O0000OO0O ,O0O0OOOOOO00OO00O ]#line:553
        return OOO0O00OO000OOOO0 ,O000OO0O0000O0O00 #line:557
    def _verifynewact4ft (O00OO00OOO0000O0O ,_OO0OO0OOOO000O00O ):#line:559
        OOO0OO000OOO00O00 ={}#line:560
        for OO00O0OOO0000O0OO in O00OO00OOO0000O0O .task_actinfo ['cedents']:#line:561
            OOO0OO000OOO00O00 [OO00O0OOO0000O0OO ['cedent_type']]=OO00O0OOO0000O0OO ['filter_value']#line:563
        OOO000OOO0OO0OOO0 =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond'])#line:565
        O0O0OO0000O0O0OOO =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond']&OOO0OO000OOO00O00 ['antv']&OOO0OO000OOO00O00 ['sucv'])#line:566
        O00000O0000OOOO00 =None #line:567
        OO0O000O0000OO0OO =0 #line:568
        OOO00OOO0O000OO00 =0 #line:569
        if OOO000OOO0OO0OOO0 >0 :#line:578
            OO0O000O0000OO0OO =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond'])*1.0 /O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['cond'])#line:579
        if O0O0OO0000O0O0OOO >0 :#line:580
            OOO00OOO0O000OO00 =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond']&OOO0OO000OOO00O00 ['antv']&OOO0OO000OOO00O00 ['sucv'])*1.0 /O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['cond']&OOO0OO000OOO00O00 ['antv'])#line:582
        OO000OO0OOOOOOO0O =1 <<O00OO00OOO0000O0O .rows_count #line:584
        O000000O0OO0OOOOO =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond'])#line:585
        OOO00O0OO0O0OOOO0 =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&~(OO000OO0OOOOOOO0O |OOO0OO000OOO00O00 ['succ'])&OOO0OO000OOO00O00 ['cond'])#line:586
        O00O00000OOOOOOOO =O00OO00OOO0000O0O ._bitcount (~(OO000OO0OOOOOOO0O |OOO0OO000OOO00O00 ['ante'])&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond'])#line:587
        O000O0OO00000OOOO =O00OO00OOO0000O0O ._bitcount (~(OO000OO0OOOOOOO0O |OOO0OO000OOO00O00 ['ante'])&~(OO000OO0OOOOOOO0O |OOO0OO000OOO00O00 ['succ'])&OOO0OO000OOO00O00 ['cond'])#line:588
        O000OO0OOOOOOO00O =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond']&OOO0OO000OOO00O00 ['antv']&OOO0OO000OOO00O00 ['sucv'])#line:589
        O00OOO0OO0O0OO0O0 =O00OO00OOO0000O0O ._bitcount (OOO0OO000OOO00O00 ['ante']&~(OO000OO0OOOOOOO0O |(OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['sucv']))&OOO0OO000OOO00O00 ['cond'])#line:590
        O0O00000OO0OOOO0O =O00OO00OOO0000O0O ._bitcount (~(OO000OO0OOOOOOO0O |(OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['antv']))&OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['cond']&OOO0OO000OOO00O00 ['sucv'])#line:591
        OOOO0OOOOOO00OO00 =O00OO00OOO0000O0O ._bitcount (~(OO000OO0OOOOOOO0O |(OOO0OO000OOO00O00 ['ante']&OOO0OO000OOO00O00 ['antv']))&~(OO000OO0OOOOOOO0O |(OOO0OO000OOO00O00 ['succ']&OOO0OO000OOO00O00 ['sucv']))&OOO0OO000OOO00O00 ['cond'])#line:592
        OOO00OO00000O0000 =True #line:593
        for OO0OO0OO0OOO0OO0O in O00OO00OOO0000O0O .quantifiers .keys ():#line:594
            if (OO0OO0OO0OOO0OO0O =='PreBase')|(OO0OO0OO0OOO0OO0O =='Base1'):#line:595
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OOO000OOO0OO0OOO0 )#line:596
            if (OO0OO0OO0OOO0OO0O =='PostBase')|(OO0OO0OO0OOO0OO0O =='Base2'):#line:597
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=O0O0OO0000O0O0OOO )#line:598
            if (OO0OO0OO0OOO0OO0O =='PreRelBase')|(OO0OO0OO0OOO0OO0O =='RelBase1'):#line:599
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OOO000OOO0OO0OOO0 *1.0 /O00OO00OOO0000O0O .data ["rows_count"])#line:600
            if (OO0OO0OO0OOO0OO0O =='PostRelBase')|(OO0OO0OO0OOO0OO0O =='RelBase2'):#line:601
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=O0O0OO0000O0O0OOO *1.0 /O00OO00OOO0000O0O .data ["rows_count"])#line:602
            if (OO0OO0OO0OOO0OO0O =='Prepim')|(OO0OO0OO0OOO0OO0O =='pim1')|(OO0OO0OO0OOO0OO0O =='PreConf')|(OO0OO0OO0OOO0OO0O =='conf1'):#line:603
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OO0O000O0000OO0OO )#line:604
            if (OO0OO0OO0OOO0OO0O =='Postpim')|(OO0OO0OO0OOO0OO0O =='pim2')|(OO0OO0OO0OOO0OO0O =='PostConf')|(OO0OO0OO0OOO0OO0O =='conf2'):#line:605
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OOO00OOO0O000OO00 )#line:606
            if (OO0OO0OO0OOO0OO0O =='Deltapim')|(OO0OO0OO0OOO0OO0O =='DeltaConf'):#line:607
                OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OO0O000O0000OO0OO -OOO00OOO0O000OO00 )#line:608
            if (OO0OO0OO0OOO0OO0O =='Ratiopim')|(OO0OO0OO0OOO0OO0O =='RatioConf'):#line:611
                if (OOO00OOO0O000OO00 >0 ):#line:612
                    OOO00OO00000O0000 =OOO00OO00000O0000 and (O00OO00OOO0000O0O .quantifiers .get (OO0OO0OO0OOO0OO0O )<=OO0O000O0000OO0OO *1.0 /OOO00OOO0O000OO00 )#line:613
                else :#line:614
                    OOO00OO00000O0000 =False #line:615
        O00O0O0O00O0OOO0O ={}#line:616
        if OOO00OO00000O0000 ==True :#line:617
            O00OO00OOO0000O0O .stats ['total_valid']+=1 #line:619
            O00O0O0O00O0OOO0O ["base1"]=OOO000OOO0OO0OOO0 #line:620
            O00O0O0O00O0OOO0O ["base2"]=O0O0OO0000O0O0OOO #line:621
            O00O0O0O00O0OOO0O ["rel_base1"]=OOO000OOO0OO0OOO0 *1.0 /O00OO00OOO0000O0O .data ["rows_count"]#line:622
            O00O0O0O00O0OOO0O ["rel_base2"]=O0O0OO0000O0O0OOO *1.0 /O00OO00OOO0000O0O .data ["rows_count"]#line:623
            O00O0O0O00O0OOO0O ["conf1"]=OO0O000O0000OO0OO #line:624
            O00O0O0O00O0OOO0O ["conf2"]=OOO00OOO0O000OO00 #line:625
            O00O0O0O00O0OOO0O ["deltaconf"]=OO0O000O0000OO0OO -OOO00OOO0O000OO00 #line:626
            if (OOO00OOO0O000OO00 >0 ):#line:627
                O00O0O0O00O0OOO0O ["ratioconf"]=OO0O000O0000OO0OO *1.0 /OOO00OOO0O000OO00 #line:628
            else :#line:629
                O00O0O0O00O0OOO0O ["ratioconf"]=None #line:630
            O00O0O0O00O0OOO0O ["fourfoldpre"]=[O000000O0OO0OOOOO ,OOO00O0OO0O0OOOO0 ,O00O00000OOOOOOOO ,O000O0OO00000OOOO ]#line:631
            O00O0O0O00O0OOO0O ["fourfoldpost"]=[O000OO0OOOOOOO00O ,O00OOO0OO0O0OO0O0 ,O0O00000OO0OOOO0O ,OOOO0OOOOOO00OO00 ]#line:632
        return OOO00OO00000O0000 ,O00O0O0O00O0OOO0O #line:634
    def _verifyact4ft (OO00000OOO0O000O0 ,_O0OOO0O0OO0000OOO ):#line:636
        O0OOOOO0O0OOOO0OO ={}#line:637
        for O00OOO000000OO0OO in OO00000OOO0O000O0 .task_actinfo ['cedents']:#line:638
            O0OOOOO0O0OOOO0OO [O00OOO000000OO0OO ['cedent_type']]=O00OOO000000OO0OO ['filter_value']#line:640
        O0OOOOO000000OOO0 =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv-']&O0OOOOO0O0OOOO0OO ['sucv-'])#line:642
        O0OO00OO0O00OOOOO =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv+']&O0OOOOO0O0OOOO0OO ['sucv+'])#line:643
        O00OO0OOOOOO0O000 =None #line:644
        OO0O00000O000O00O =0 #line:645
        OOO0OO0OO0OO00O00 =0 #line:646
        if O0OOOOO000000OOO0 >0 :#line:655
            OO0O00000O000O00O =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv-']&O0OOOOO0O0OOOO0OO ['sucv-'])*1.0 /OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv-'])#line:657
        if O0OO00OO0O00OOOOO >0 :#line:658
            OOO0OO0OO0OO00O00 =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv+']&O0OOOOO0O0OOOO0OO ['sucv+'])*1.0 /OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv+'])#line:660
        O00OO0OOOOOO0OO00 =1 <<OO00000OOO0O000O0 .data ["rows_count"]#line:662
        OO0O00OO0000O0OOO =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv-']&O0OOOOO0O0OOOO0OO ['sucv-'])#line:663
        O0O0O000OO000O00O =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv-']&~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['sucv-']))&O0OOOOO0O0OOOO0OO ['cond'])#line:664
        OO0O0000O0O00OO00 =OO00000OOO0O000O0 ._bitcount (~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv-']))&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['sucv-'])#line:665
        OOOO000OOO0OO00OO =OO00000OOO0O000O0 ._bitcount (~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv-']))&~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['sucv-']))&O0OOOOO0O0OOOO0OO ['cond'])#line:666
        OO0O000OOO0OOOOOO =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['antv+']&O0OOOOO0O0OOOO0OO ['sucv+'])#line:667
        O0O00O0OOO00O0OOO =OO00000OOO0O000O0 ._bitcount (O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv+']&~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['sucv+']))&O0OOOOO0O0OOOO0OO ['cond'])#line:668
        O000OO0O00000OO00 =OO00000OOO0O000O0 ._bitcount (~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv+']))&O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['cond']&O0OOOOO0O0OOOO0OO ['sucv+'])#line:669
        OOOO0O0OOO0OO00O0 =OO00000OOO0O000O0 ._bitcount (~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['ante']&O0OOOOO0O0OOOO0OO ['antv+']))&~(O00OO0OOOOOO0OO00 |(O0OOOOO0O0OOOO0OO ['succ']&O0OOOOO0O0OOOO0OO ['sucv+']))&O0OOOOO0O0OOOO0OO ['cond'])#line:670
        O0O0OOOO0OO00OO0O =True #line:671
        for O000OOOO0O0O0OO00 in OO00000OOO0O000O0 .quantifiers .keys ():#line:672
            if (O000OOOO0O0O0OO00 =='PreBase')|(O000OOOO0O0O0OO00 =='Base1'):#line:673
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=O0OOOOO000000OOO0 )#line:674
            if (O000OOOO0O0O0OO00 =='PostBase')|(O000OOOO0O0O0OO00 =='Base2'):#line:675
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=O0OO00OO0O00OOOOO )#line:676
            if (O000OOOO0O0O0OO00 =='PreRelBase')|(O000OOOO0O0O0OO00 =='RelBase1'):#line:677
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=O0OOOOO000000OOO0 *1.0 /OO00000OOO0O000O0 .data ["rows_count"])#line:678
            if (O000OOOO0O0O0OO00 =='PostRelBase')|(O000OOOO0O0O0OO00 =='RelBase2'):#line:679
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=O0OO00OO0O00OOOOO *1.0 /OO00000OOO0O000O0 .data ["rows_count"])#line:680
            if (O000OOOO0O0O0OO00 =='Prepim')|(O000OOOO0O0O0OO00 =='pim1')|(O000OOOO0O0O0OO00 =='PreConf')|(O000OOOO0O0O0OO00 =='conf1'):#line:681
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=OO0O00000O000O00O )#line:682
            if (O000OOOO0O0O0OO00 =='Postpim')|(O000OOOO0O0O0OO00 =='pim2')|(O000OOOO0O0O0OO00 =='PostConf')|(O000OOOO0O0O0OO00 =='conf2'):#line:683
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=OOO0OO0OO0OO00O00 )#line:684
            if (O000OOOO0O0O0OO00 =='Deltapim')|(O000OOOO0O0O0OO00 =='DeltaConf'):#line:685
                O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=OO0O00000O000O00O -OOO0OO0OO0OO00O00 )#line:686
            if (O000OOOO0O0O0OO00 =='Ratiopim')|(O000OOOO0O0O0OO00 =='RatioConf'):#line:689
                if (OO0O00000O000O00O >0 ):#line:690
                    O0O0OOOO0OO00OO0O =O0O0OOOO0OO00OO0O and (OO00000OOO0O000O0 .quantifiers .get (O000OOOO0O0O0OO00 )<=OOO0OO0OO0OO00O00 *1.0 /OO0O00000O000O00O )#line:691
                else :#line:692
                    O0O0OOOO0OO00OO0O =False #line:693
        O0O00O0OOOOOOOO00 ={}#line:694
        if O0O0OOOO0OO00OO0O ==True :#line:695
            OO00000OOO0O000O0 .stats ['total_valid']+=1 #line:697
            O0O00O0OOOOOOOO00 ["base1"]=O0OOOOO000000OOO0 #line:698
            O0O00O0OOOOOOOO00 ["base2"]=O0OO00OO0O00OOOOO #line:699
            O0O00O0OOOOOOOO00 ["rel_base1"]=O0OOOOO000000OOO0 *1.0 /OO00000OOO0O000O0 .data ["rows_count"]#line:700
            O0O00O0OOOOOOOO00 ["rel_base2"]=O0OO00OO0O00OOOOO *1.0 /OO00000OOO0O000O0 .data ["rows_count"]#line:701
            O0O00O0OOOOOOOO00 ["conf1"]=OO0O00000O000O00O #line:702
            O0O00O0OOOOOOOO00 ["conf2"]=OOO0OO0OO0OO00O00 #line:703
            O0O00O0OOOOOOOO00 ["deltaconf"]=OO0O00000O000O00O -OOO0OO0OO0OO00O00 #line:704
            if (OO0O00000O000O00O >0 ):#line:705
                O0O00O0OOOOOOOO00 ["ratioconf"]=OOO0OO0OO0OO00O00 *1.0 /OO0O00000O000O00O #line:706
            else :#line:707
                O0O00O0OOOOOOOO00 ["ratioconf"]=None #line:708
            O0O00O0OOOOOOOO00 ["fourfoldpre"]=[OO0O00OO0000O0OOO ,O0O0O000OO000O00O ,OO0O0000O0O00OO00 ,OOOO000OOO0OO00OO ]#line:709
            O0O00O0OOOOOOOO00 ["fourfoldpost"]=[OO0O000OOO0OOOOOO ,O0O00O0OOO00O0OOO ,O000OO0O00000OO00 ,OOOO0O0OOO0OO00O0 ]#line:710
        return O0O0OOOO0OO00OO0O ,O0O00O0OOOOOOOO00 #line:712
    def _verify_opt (OOO000O0O0OO0OO0O ,OO0OO00000O000O00 ,O0OO0OOOO0OO0O00O ):#line:714
        OOO000O0O0OO0OO0O .stats ['total_ver']+=1 #line:715
        OO000O00OOO0OOOOO =False #line:716
        if not (OO0OO00000O000O00 ['optim'].get ('only_con')):#line:719
            return False #line:720
        if not (OOO000O0O0OO0OO0O .options ['optimizations']):#line:723
            return False #line:725
        OO0O0OO0O0O00OO0O ={}#line:727
        for O0OO0O000O0OO00OO in OOO000O0O0OO0OO0O .task_actinfo ['cedents']:#line:728
            OO0O0OO0O0O00OO0O [O0OO0O000O0OO00OO ['cedent_type']]=O0OO0O000O0OO00OO ['filter_value']#line:730
        OOO00OOOO0000O000 =1 <<OOO000O0O0OO0OO0O .data ["rows_count"]#line:732
        O0OO0OO000O0OO00O =OOO00OOOO0000O000 -1 #line:733
        O0OO0000OO0OOOOOO =""#line:734
        O0OOOOOOO000000OO =0 #line:735
        if (OO0O0OO0O0O00OO0O .get ('ante')!=None ):#line:736
            O0OO0OO000O0OO00O =O0OO0OO000O0OO00O &OO0O0OO0O0O00OO0O ['ante']#line:737
        if (OO0O0OO0O0O00OO0O .get ('succ')!=None ):#line:738
            O0OO0OO000O0OO00O =O0OO0OO000O0OO00O &OO0O0OO0O0O00OO0O ['succ']#line:739
        if (OO0O0OO0O0O00OO0O .get ('cond')!=None ):#line:740
            O0OO0OO000O0OO00O =O0OO0OO000O0OO00O &OO0O0OO0O0O00OO0O ['cond']#line:741
        O0O00OO00OOOO0O0O =None #line:744
        if (OOO000O0O0OO0OO0O .proc =='CFMiner')|(OOO000O0O0OO0OO0O .proc =='4ftMiner'):#line:769
            O00OO00OO0OO000OO =OOO000O0O0OO0OO0O ._bitcount (O0OO0OO000O0OO00O )#line:770
            if not (OOO000O0O0OO0OO0O ._opt_base ==None ):#line:771
                if not (OOO000O0O0OO0OO0O ._opt_base <=O00OO00OO0OO000OO ):#line:772
                    OO000O00OOO0OOOOO =True #line:773
            if not (OOO000O0O0OO0OO0O ._opt_relbase ==None ):#line:775
                if not (OOO000O0O0OO0OO0O ._opt_relbase <=O00OO00OO0OO000OO *1.0 /OOO000O0O0OO0OO0O .data ["rows_count"]):#line:776
                    OO000O00OOO0OOOOO =True #line:777
        if (OOO000O0O0OO0OO0O .proc =='SD4ftMiner'):#line:779
            O00OO00OO0OO000OO =OOO000O0O0OO0OO0O ._bitcount (O0OO0OO000O0OO00O )#line:780
            if (not (OOO000O0O0OO0OO0O ._opt_base1 ==None ))&(not (OOO000O0O0OO0OO0O ._opt_base2 ==None )):#line:781
                if not (max (OOO000O0O0OO0OO0O ._opt_base1 ,OOO000O0O0OO0OO0O ._opt_base2 )<=O00OO00OO0OO000OO ):#line:782
                    OO000O00OOO0OOOOO =True #line:784
            if (not (OOO000O0O0OO0OO0O ._opt_relbase1 ==None ))&(not (OOO000O0O0OO0OO0O ._opt_relbase2 ==None )):#line:785
                if not (max (OOO000O0O0OO0OO0O ._opt_relbase1 ,OOO000O0O0OO0OO0O ._opt_relbase2 )<=O00OO00OO0OO000OO *1.0 /OOO000O0O0OO0OO0O .data ["rows_count"]):#line:786
                    OO000O00OOO0OOOOO =True #line:787
        return OO000O00OOO0OOOOO #line:789
        if OOO000O0O0OO0OO0O .proc =='CFMiner':#line:792
            if (O0OO0OOOO0OO0O00O ['cedent_type']=='cond')&(O0OO0OOOO0OO0O00O ['defi'].get ('type')=='con'):#line:793
                O00OO00OO0OO000OO =bin (OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:794
                O00OOOO0O00O00OO0 =True #line:795
                for O000OO00O0O0O00O0 in OOO000O0O0OO0OO0O .quantifiers .keys ():#line:796
                    if O000OO00O0O0O00O0 =='Base':#line:797
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO )#line:798
                        if not (O00OOOO0O00O00OO0 ):#line:799
                            print (f"...optimization : base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:800
                    if O000OO00O0O0O00O0 =='RelBase':#line:801
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO *1.0 /OOO000O0O0OO0OO0O .data ["rows_count"])#line:802
                        if not (O00OOOO0O00O00OO0 ):#line:803
                            print (f"...optimization : base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:804
                OO000O00OOO0OOOOO =not (O00OOOO0O00O00OO0 )#line:805
        elif OOO000O0O0OO0OO0O .proc =='4ftMiner':#line:806
            if (O0OO0OOOO0OO0O00O ['cedent_type']=='cond')&(O0OO0OOOO0OO0O00O ['defi'].get ('type')=='con'):#line:807
                O00OO00OO0OO000OO =bin (OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:808
                O00OOOO0O00O00OO0 =True #line:809
                for O000OO00O0O0O00O0 in OOO000O0O0OO0OO0O .quantifiers .keys ():#line:810
                    if O000OO00O0O0O00O0 =='Base':#line:811
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO )#line:812
                        if not (O00OOOO0O00O00OO0 ):#line:813
                            print (f"...optimization : base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:814
                    if O000OO00O0O0O00O0 =='RelBase':#line:815
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO *1.0 /OOO000O0O0OO0OO0O .data ["rows_count"])#line:816
                        if not (O00OOOO0O00O00OO0 ):#line:817
                            print (f"...optimization : base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:818
                OO000O00OOO0OOOOO =not (O00OOOO0O00O00OO0 )#line:819
            if (O0OO0OOOO0OO0O00O ['cedent_type']=='ante')&(O0OO0OOOO0OO0O00O ['defi'].get ('type')=='con'):#line:820
                O00OO00OO0OO000OO =bin (OO0O0OO0O0O00OO0O ['ante']&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:821
                O00OOOO0O00O00OO0 =True #line:822
                for O000OO00O0O0O00O0 in OOO000O0O0OO0OO0O .quantifiers .keys ():#line:823
                    if O000OO00O0O0O00O0 =='Base':#line:824
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO )#line:825
                        if not (O00OOOO0O00O00OO0 ):#line:826
                            print (f"...optimization : ANTE: base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:827
                    if O000OO00O0O0O00O0 =='RelBase':#line:828
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O00OO00OO0OO000OO *1.0 /OOO000O0O0OO0OO0O .data ["rows_count"])#line:829
                        if not (O00OOOO0O00O00OO0 ):#line:830
                            print (f"...optimization : ANTE:  base is {O00OO00OO0OO000OO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:831
                OO000O00OOO0OOOOO =not (O00OOOO0O00O00OO0 )#line:832
            if (O0OO0OOOO0OO0O00O ['cedent_type']=='succ')&(O0OO0OOOO0OO0O00O ['defi'].get ('type')=='con'):#line:833
                O00OO00OO0OO000OO =bin (OO0O0OO0O0O00OO0O ['ante']&OO0O0OO0O0O00OO0O ['cond']&OO0O0OO0O0O00OO0O ['succ']).count ("1")#line:834
                O0O00OO00OOOO0O0O =0 #line:835
                if O00OO00OO0OO000OO >0 :#line:836
                    O0O00OO00OOOO0O0O =bin (OO0O0OO0O0O00OO0O ['ante']&OO0O0OO0O0O00OO0O ['succ']&OO0O0OO0O0O00OO0O ['cond']).count ("1")*1.0 /bin (OO0O0OO0O0O00OO0O ['ante']&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:837
                OOO00OOOO0000O000 =1 <<OOO000O0O0OO0OO0O .data ["rows_count"]#line:838
                OO0O00O0000O0000O =bin (OO0O0OO0O0O00OO0O ['ante']&OO0O0OO0O0O00OO0O ['succ']&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:839
                O00OO00O0O000O0O0 =bin (OO0O0OO0O0O00OO0O ['ante']&~(OOO00OOOO0000O000 |OO0O0OO0O0O00OO0O ['succ'])&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:840
                O0OO0O000O0OO00OO =bin (~(OOO00OOOO0000O000 |OO0O0OO0O0O00OO0O ['ante'])&OO0O0OO0O0O00OO0O ['succ']&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:841
                OOOOO0000000O0O0O =bin (~(OOO00OOOO0000O000 |OO0O0OO0O0O00OO0O ['ante'])&~(OOO00OOOO0000O000 |OO0O0OO0O0O00OO0O ['succ'])&OO0O0OO0O0O00OO0O ['cond']).count ("1")#line:842
                O00OOOO0O00O00OO0 =True #line:843
                for O000OO00O0O0O00O0 in OOO000O0O0OO0OO0O .quantifiers .keys ():#line:844
                    if O000OO00O0O0O00O0 =='pim':#line:845
                        O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=O0O00OO00OOOO0O0O )#line:846
                    if not (O00OOOO0O00O00OO0 ):#line:847
                        print (f"...optimization : SUCC:  pim is {O0O00OO00OOOO0O0O} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:848
                    if O000OO00O0O0O00O0 =='aad':#line:850
                        if (OO0O00O0000O0000O +O00OO00O0O000O0O0 )*(OO0O00O0000O0000O +O0OO0O000O0OO00OO )>0 :#line:851
                            O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=OO0O00O0000O0000O *(OO0O00O0000O0000O +O00OO00O0O000O0O0 +O0OO0O000O0OO00OO +OOOOO0000000O0O0O )/(OO0O00O0000O0000O +O00OO00O0O000O0O0 )/(OO0O00O0000O0000O +O0OO0O000O0OO00OO )-1 )#line:852
                        else :#line:853
                            O00OOOO0O00O00OO0 =False #line:854
                        if not (O00OOOO0O00O00OO0 ):#line:855
                            O0000O0O00OO0O0O0 =OO0O00O0000O0000O *(OO0O00O0000O0000O +O00OO00O0O000O0O0 +O0OO0O000O0OO00OO +OOOOO0000000O0O0O )/(OO0O00O0000O0000O +O00OO00O0O000O0O0 )/(OO0O00O0000O0000O +O0OO0O000O0OO00OO )-1 #line:856
                            print (f"...optimization : SUCC:  aad is {O0000O0O00OO0O0O0} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:857
                    if O000OO00O0O0O00O0 =='bad':#line:858
                        if (OO0O00O0000O0000O +O00OO00O0O000O0O0 )*(OO0O00O0000O0000O +O0OO0O000O0OO00OO )>0 :#line:859
                            O00OOOO0O00O00OO0 =O00OOOO0O00O00OO0 and (OOO000O0O0OO0OO0O .quantifiers .get (O000OO00O0O0O00O0 )<=1 -OO0O00O0000O0000O *(OO0O00O0000O0000O +O00OO00O0O000O0O0 +O0OO0O000O0OO00OO +OOOOO0000000O0O0O )/(OO0O00O0000O0000O +O00OO00O0O000O0O0 )/(OO0O00O0000O0000O +O0OO0O000O0OO00OO ))#line:860
                        else :#line:861
                            O00OOOO0O00O00OO0 =False #line:862
                        if not (O00OOOO0O00O00OO0 ):#line:863
                            O00OO0O0OO0O0OOOO =1 -OO0O00O0000O0000O *(OO0O00O0000O0000O +O00OO00O0O000O0O0 +O0OO0O000O0OO00OO +OOOOO0000000O0O0O )/(OO0O00O0000O0000O +O00OO00O0O000O0O0 )/(OO0O00O0000O0000O +O0OO0O000O0OO00OO )#line:864
                            print (f"...optimization : SUCC:  bad is {O00OO0O0OO0O0OOOO} for {O0OO0OOOO0OO0O00O['generated_string']}")#line:865
                OO000O00OOO0OOOOO =not (O00OOOO0O00O00OO0 )#line:866
        if (OO000O00OOO0OOOOO ):#line:867
            print (f"... OPTIMALIZATION - SKIPPING BRANCH at cedent {O0OO0OOOO0OO0O00O['cedent_type']}")#line:868
        return OO000O00OOO0OOOOO #line:869
    def _print (OOOO0O000O0000O0O ,OO0OOO0O00O0O0OOO ,_O00000OOO0OOOO0O0 ,_O00O000OO0O0O0OOO ):#line:872
        if (len (_O00000OOO0OOOO0O0 ))!=len (_O00O000OO0O0O0OOO ):#line:873
            print ("DIFF IN LEN for following cedent : "+str (len (_O00000OOO0OOOO0O0 ))+" vs "+str (len (_O00O000OO0O0O0OOO )))#line:874
            print ("trace cedent : "+str (_O00000OOO0OOOO0O0 )+", traces "+str (_O00O000OO0O0O0OOO ))#line:875
        OO0O000000OO0O000 =''#line:876
        O00O0O0OO000000O0 ={}#line:877
        O00000OOO000O0000 =[]#line:878
        for O000OOO0OO0OO0OO0 in range (len (_O00000OOO0OOOO0O0 )):#line:879
            O0OOO0000OOOOOO0O =OOOO0O000O0000O0O .data ["varname"].index (OO0OOO0O00O0O0OOO ['defi'].get ('attributes')[_O00000OOO0OOOO0O0 [O000OOO0OO0OO0OO0 ]].get ('name'))#line:880
            OO0O000000OO0O000 =OO0O000000OO0O000 +OOOO0O000O0000O0O .data ["varname"][O0OOO0000OOOOOO0O ]+'('#line:882
            O00000OOO000O0000 .append (O0OOO0000OOOOOO0O )#line:883
            OO00O0OOO0OO0OOOO =[]#line:884
            for OO0O00OO0OO0OO0OO in _O00O000OO0O0O0OOO [O000OOO0OO0OO0OO0 ]:#line:885
                OO0O000000OO0O000 =OO0O000000OO0O000 +str (OOOO0O000O0000O0O .data ["catnames"][O0OOO0000OOOOOO0O ][OO0O00OO0OO0OO0OO ])+" "#line:886
                OO00O0OOO0OO0OOOO .append (str (OOOO0O000O0000O0O .data ["catnames"][O0OOO0000OOOOOO0O ][OO0O00OO0OO0OO0OO ]))#line:887
            OO0O000000OO0O000 =OO0O000000OO0O000 [:-1 ]+')'#line:888
            O00O0O0OO000000O0 [OOOO0O000O0000O0O .data ["varname"][O0OOO0000OOOOOO0O ]]=OO00O0OOO0OO0OOOO #line:889
            if O000OOO0OO0OO0OO0 +1 <len (_O00000OOO0OOOO0O0 ):#line:890
                OO0O000000OO0O000 =OO0O000000OO0O000 +' & '#line:891
        return OO0O000000OO0O000 ,O00O0O0OO000000O0 ,O00000OOO000O0000 #line:895
    def _print_hypo (OO0OOO00O0OO00O0O ,O0OOOO000O0000000 ):#line:897
        OO0OOO00O0OO00O0O .print_rule (O0OOOO000O0000000 )#line:898
    def _print_rule (O0O00O00000000O0O ,OO0000O0000O00000 ):#line:900
        if O0O00O00000000O0O .verbosity ['print_rules']:#line:901
            print ('Rules info : '+str (OO0000O0000O00000 ['params']))#line:902
            for OO00000O0OO000O00 in O0O00O00000000O0O .task_actinfo ['cedents']:#line:903
                print (OO00000O0OO000O00 ['cedent_type']+' = '+OO00000O0OO000O00 ['generated_string'])#line:904
    def _genvar (O0OOO00O0OOO00OOO ,O0OO00000000OO000 ,OOOO000OO00OOO0O0 ,_OO0O0O00OOO000O00 ,_O000O00OOO0OO000O ,_O0000OO00O0OOOO00 ,_O0OO00OOO0OOOOO0O ,_OO0OOO00OOO0O0OOO ):#line:906
        for O0OOOOOO00O0O0OOO in range (OOOO000OO00OOO0O0 ['num_cedent']):#line:907
            if len (_OO0O0O00OOO000O00 )==0 or O0OOOOOO00O0O0OOO >_OO0O0O00OOO000O00 [-1 ]:#line:908
                _OO0O0O00OOO000O00 .append (O0OOOOOO00O0O0OOO )#line:909
                O0O0O00000OOO00OO =O0OOO00O0OOO00OOO .data ["varname"].index (OOOO000OO00OOO0O0 ['defi'].get ('attributes')[O0OOOOOO00O0O0OOO ].get ('name'))#line:910
                _OO0O00OOOOOO000O0 =OOOO000OO00OOO0O0 ['defi'].get ('attributes')[O0OOOOOO00O0O0OOO ].get ('minlen')#line:911
                _OOOOO00O00000O000 =OOOO000OO00OOO0O0 ['defi'].get ('attributes')[O0OOOOOO00O0O0OOO ].get ('maxlen')#line:912
                _O00O00O0OO000O0OO =OOOO000OO00OOO0O0 ['defi'].get ('attributes')[O0OOOOOO00O0O0OOO ].get ('type')#line:913
                OO0OOO0OO000O0O00 =len (O0OOO00O0OOO00OOO .data ["dm"][O0O0O00000OOO00OO ])#line:914
                _O0OO0O0O000O0000O =[]#line:915
                _O000O00OOO0OO000O .append (_O0OO0O0O000O0000O )#line:916
                _O0O0O0O00OO0O0O00 =int (0 )#line:917
                O0OOO00O0OOO00OOO ._gencomb (O0OO00000000OO000 ,OOOO000OO00OOO0O0 ,_OO0O0O00OOO000O00 ,_O000O00OOO0OO000O ,_O0OO0O0O000O0000O ,_O0000OO00O0OOOO00 ,_O0O0O0O00OO0O0O00 ,OO0OOO0OO000O0O00 ,_O00O00O0OO000O0OO ,_O0OO00OOO0OOOOO0O ,_OO0OOO00OOO0O0OOO ,_OO0O00OOOOOO000O0 ,_OOOOO00O00000O000 )#line:918
                _O000O00OOO0OO000O .pop ()#line:919
                _OO0O0O00OOO000O00 .pop ()#line:920
    def _gencomb (OO0O00O00O0000OO0 ,OOO0O0OO0O00000O0 ,OOOO000O000OO0000 ,_O00OO000O0OOO0OOO ,_OOO00O000O00000O0 ,_OOO00OOO00OO000OO ,_O00000000000OO000 ,_OO000O00OOO0OO0O0 ,OOO0OO00000OOOO0O ,_OO0OOO00O00OOOO0O ,_O00OO0O0OOO0OO0O0 ,_O0O0O0OO000000000 ,_O0O0000O000O00000 ,_O0O0O0O00O0000O00 ):#line:922
        _OO0OOOOO0OOO0O000 =[]#line:923
        if _OO0OOO00O00OOOO0O =="subset":#line:924
            if len (_OOO00OOO00OO000OO )==0 :#line:925
                _OO0OOOOO0OOO0O000 =range (OOO0OO00000OOOO0O )#line:926
            else :#line:927
                _OO0OOOOO0OOO0O000 =range (_OOO00OOO00OO000OO [-1 ]+1 ,OOO0OO00000OOOO0O )#line:928
        elif _OO0OOO00O00OOOO0O =="seq":#line:929
            if len (_OOO00OOO00OO000OO )==0 :#line:930
                _OO0OOOOO0OOO0O000 =range (OOO0OO00000OOOO0O -_O0O0000O000O00000 +1 )#line:931
            else :#line:932
                if _OOO00OOO00OO000OO [-1 ]+1 ==OOO0OO00000OOOO0O :#line:933
                    return #line:934
                O00OOO00OOO00OO0O =_OOO00OOO00OO000OO [-1 ]+1 #line:935
                _OO0OOOOO0OOO0O000 .append (O00OOO00OOO00OO0O )#line:936
        elif _OO0OOO00O00OOOO0O =="lcut":#line:937
            if len (_OOO00OOO00OO000OO )==0 :#line:938
                O00OOO00OOO00OO0O =0 ;#line:939
            else :#line:940
                if _OOO00OOO00OO000OO [-1 ]+1 ==OOO0OO00000OOOO0O :#line:941
                    return #line:942
                O00OOO00OOO00OO0O =_OOO00OOO00OO000OO [-1 ]+1 #line:943
            _OO0OOOOO0OOO0O000 .append (O00OOO00OOO00OO0O )#line:944
        elif _OO0OOO00O00OOOO0O =="rcut":#line:945
            if len (_OOO00OOO00OO000OO )==0 :#line:946
                O00OOO00OOO00OO0O =OOO0OO00000OOOO0O -1 ;#line:947
            else :#line:948
                if _OOO00OOO00OO000OO [-1 ]==0 :#line:949
                    return #line:950
                O00OOO00OOO00OO0O =_OOO00OOO00OO000OO [-1 ]-1 #line:951
            _OO0OOOOO0OOO0O000 .append (O00OOO00OOO00OO0O )#line:953
        elif _OO0OOO00O00OOOO0O =="one":#line:954
            if len (_OOO00OOO00OO000OO )==0 :#line:955
                OO0OOO000O0OOOO0O =OO0O00O00O0000OO0 .data ["varname"].index (OOOO000O000OO0000 ['defi'].get ('attributes')[_O00OO000O0OOO0OOO [-1 ]].get ('name'))#line:956
                try :#line:957
                    O00OOO00OOO00OO0O =OO0O00O00O0000OO0 .data ["catnames"][OO0OOO000O0OOOO0O ].index (OOOO000O000OO0000 ['defi'].get ('attributes')[_O00OO000O0OOO0OOO [-1 ]].get ('value'))#line:958
                except :#line:959
                    print (f"ERROR: attribute '{OOOO000O000OO0000['defi'].get('attributes')[_O00OO000O0OOO0OOO[-1]].get('name')}' has not value '{OOOO000O000OO0000['defi'].get('attributes')[_O00OO000O0OOO0OOO[-1]].get('value')}'")#line:960
                    exit (1 )#line:961
                _OO0OOOOO0OOO0O000 .append (O00OOO00OOO00OO0O )#line:962
                _O0O0000O000O00000 =1 #line:963
                _O0O0O0O00O0000O00 =1 #line:964
            else :#line:965
                print ("DEBUG: one category should not have more categories")#line:966
                return #line:967
        else :#line:968
            print ("Attribute type "+_OO0OOO00O00OOOO0O +" not supported.")#line:969
            return #line:970
        for O00000O0OOOO0O0OO in _OO0OOOOO0OOO0O000 :#line:973
                _OOO00OOO00OO000OO .append (O00000O0OOOO0O0OO )#line:975
                _OOO00O000O00000O0 .pop ()#line:976
                _OOO00O000O00000O0 .append (_OOO00OOO00OO000OO )#line:977
                _O0OOOO0OOOO0OOOO0 =_OO000O00OOO0OO0O0 |OO0O00O00O0000OO0 .data ["dm"][OO0O00O00O0000OO0 .data ["varname"].index (OOOO000O000OO0000 ['defi'].get ('attributes')[_O00OO000O0OOO0OOO [-1 ]].get ('name'))][O00000O0OOOO0O0OO ]#line:981
                _OOO00000000OOOO0O =1 #line:983
                if (len (_O00OO000O0OOO0OOO )<_O00OO0O0OOO0OO0O0 ):#line:984
                    _OOO00000000OOOO0O =-1 #line:985
                if (len (_OOO00O000O00000O0 [-1 ])<_O0O0000O000O00000 ):#line:987
                    _OOO00000000OOOO0O =0 #line:988
                _OOOO00O0OOO0OO000 =0 #line:990
                if OOOO000O000OO0000 ['defi'].get ('type')=='con':#line:991
                    _OOOO00O0OOO0OO000 =_O00000000000OO000 &_O0OOOO0OOOO0OOOO0 #line:992
                else :#line:993
                    _OOOO00O0OOO0OO000 =_O00000000000OO000 |_O0OOOO0OOOO0OOOO0 #line:994
                OOOO000O000OO0000 ['trace_cedent']=_O00OO000O0OOO0OOO #line:995
                OOOO000O000OO0000 ['traces']=_OOO00O000O00000O0 #line:996
                OOOO0OO0O0OO0OOO0 ,OO0OOOOO0O0OO0000 ,O00O0OO0O0O00O0OO =OO0O00O00O0000OO0 ._print (OOOO000O000OO0000 ,_O00OO000O0OOO0OOO ,_OOO00O000O00000O0 )#line:997
                OOOO000O000OO0000 ['generated_string']=OOOO0OO0O0OO0OOO0 #line:998
                OOOO000O000OO0000 ['rule']=OO0OOOOO0O0OO0000 #line:999
                OOOO000O000OO0000 ['filter_value']=_OOOO00O0OOO0OO000 #line:1000
                OOOO000O000OO0000 ['traces']=copy .deepcopy (_OOO00O000O00000O0 )#line:1001
                OOOO000O000OO0000 ['trace_cedent']=copy .deepcopy (_O00OO000O0OOO0OOO )#line:1002
                OOOO000O000OO0000 ['trace_cedent_asindata']=copy .deepcopy (O00O0OO0O0O00O0OO )#line:1003
                OOO0O0OO0O00000O0 ['cedents'].append (OOOO000O000OO0000 )#line:1005
                O0000OOO00O0OOOO0 =OO0O00O00O0000OO0 ._verify_opt (OOO0O0OO0O00000O0 ,OOOO000O000OO0000 )#line:1006
                if not (O0000OOO00O0OOOO0 ):#line:1012
                    if _OOO00000000OOOO0O ==1 :#line:1013
                        if len (OOO0O0OO0O00000O0 ['cedents_to_do'])==len (OOO0O0OO0O00000O0 ['cedents']):#line:1015
                            if OO0O00O00O0000OO0 .proc =='CFMiner':#line:1016
                                OO00O0000O0OOOOOO ,OOOO000O0O0OOO000 =OO0O00O00O0000OO0 ._verifyCF (_OOOO00O0OOO0OO000 )#line:1017
                            elif OO0O00O00O0000OO0 .proc =='4ftMiner':#line:1018
                                OO00O0000O0OOOOOO ,OOOO000O0O0OOO000 =OO0O00O00O0000OO0 ._verify4ft (_O0OOOO0OOOO0OOOO0 )#line:1019
                            elif OO0O00O00O0000OO0 .proc =='SD4ftMiner':#line:1020
                                OO00O0000O0OOOOOO ,OOOO000O0O0OOO000 =OO0O00O00O0000OO0 ._verifysd4ft (_O0OOOO0OOOO0OOOO0 )#line:1021
                            elif OO0O00O00O0000OO0 .proc =='NewAct4ftMiner':#line:1022
                                OO00O0000O0OOOOOO ,OOOO000O0O0OOO000 =OO0O00O00O0000OO0 ._verifynewact4ft (_O0OOOO0OOOO0OOOO0 )#line:1023
                            elif OO0O00O00O0000OO0 .proc =='Act4ftMiner':#line:1024
                                OO00O0000O0OOOOOO ,OOOO000O0O0OOO000 =OO0O00O00O0000OO0 ._verifyact4ft (_O0OOOO0OOOO0OOOO0 )#line:1025
                            else :#line:1026
                                print ("Unsupported procedure : "+OO0O00O00O0000OO0 .proc )#line:1027
                                exit (0 )#line:1028
                            if OO00O0000O0OOOOOO ==True :#line:1029
                                O0O00OOOO0O000OOO ={}#line:1030
                                O0O00OOOO0O000OOO ["rule_id"]=OO0O00O00O0000OO0 .stats ['total_valid']#line:1031
                                O0O00OOOO0O000OOO ["cedents_str"]={}#line:1032
                                O0O00OOOO0O000OOO ["cedents_struct"]={}#line:1033
                                O0O00OOOO0O000OOO ['traces']={}#line:1034
                                O0O00OOOO0O000OOO ['trace_cedent_taskorder']={}#line:1035
                                O0O00OOOO0O000OOO ['trace_cedent_dataorder']={}#line:1036
                                for O00O0O00OO0O00000 in OOO0O0OO0O00000O0 ['cedents']:#line:1037
                                    O0O00OOOO0O000OOO ['cedents_str'][O00O0O00OO0O00000 ['cedent_type']]=O00O0O00OO0O00000 ['generated_string']#line:1039
                                    O0O00OOOO0O000OOO ['cedents_struct'][O00O0O00OO0O00000 ['cedent_type']]=O00O0O00OO0O00000 ['rule']#line:1040
                                    O0O00OOOO0O000OOO ['traces'][O00O0O00OO0O00000 ['cedent_type']]=O00O0O00OO0O00000 ['traces']#line:1041
                                    O0O00OOOO0O000OOO ['trace_cedent_taskorder'][O00O0O00OO0O00000 ['cedent_type']]=O00O0O00OO0O00000 ['trace_cedent']#line:1042
                                    O0O00OOOO0O000OOO ['trace_cedent_dataorder'][O00O0O00OO0O00000 ['cedent_type']]=O00O0O00OO0O00000 ['trace_cedent_asindata']#line:1043
                                O0O00OOOO0O000OOO ["params"]=OOOO000O0O0OOO000 #line:1045
                                OO0O00O00O0000OO0 ._print_rule (O0O00OOOO0O000OOO )#line:1047
                                OO0O00O00O0000OO0 .rulelist .append (O0O00OOOO0O000OOO )#line:1053
                            OO0O00O00O0000OO0 .stats ['total_cnt']+=1 #line:1055
                            OO0O00O00O0000OO0 .stats ['total_ver']+=1 #line:1056
                    if _OOO00000000OOOO0O >=0 :#line:1057
                        if len (OOO0O0OO0O00000O0 ['cedents_to_do'])>len (OOO0O0OO0O00000O0 ['cedents']):#line:1058
                            OO0O00O00O0000OO0 ._start_cedent (OOO0O0OO0O00000O0 )#line:1059
                    OOO0O0OO0O00000O0 ['cedents'].pop ()#line:1060
                    if (len (_O00OO000O0OOO0OOO )<_O0O0O0OO000000000 ):#line:1061
                        OO0O00O00O0000OO0 ._genvar (OOO0O0OO0O00000O0 ,OOOO000O000OO0000 ,_O00OO000O0OOO0OOO ,_OOO00O000O00000O0 ,_OOOO00O0OOO0OO000 ,_O00OO0O0OOO0OO0O0 ,_O0O0O0OO000000000 )#line:1062
                else :#line:1063
                    OOO0O0OO0O00000O0 ['cedents'].pop ()#line:1064
                if len (_OOO00OOO00OO000OO )<_O0O0O0O00O0000O00 :#line:1065
                    OO0O00O00O0000OO0 ._gencomb (OOO0O0OO0O00000O0 ,OOOO000O000OO0000 ,_O00OO000O0OOO0OOO ,_OOO00O000O00000O0 ,_OOO00OOO00OO000OO ,_O00000000000OO000 ,_O0OOOO0OOOO0OOOO0 ,OOO0OO00000OOOO0O ,_OO0OOO00O00OOOO0O ,_O00OO0O0OOO0OO0O0 ,_O0O0O0OO000000000 ,_O0O0000O000O00000 ,_O0O0O0O00O0000O00 )#line:1066
                _OOO00OOO00OO000OO .pop ()#line:1067
    def _start_cedent (OO00O0O00000O00O0 ,O00OOOOOO00O0O0OO ):#line:1069
        if len (O00OOOOOO00O0O0OO ['cedents_to_do'])>len (O00OOOOOO00O0O0OO ['cedents']):#line:1070
            _OO0O00OO0O00OOO0O =[]#line:1071
            _OOOOO00000OOO0O0O =[]#line:1072
            OOOOOOOO00O0OO000 ={}#line:1073
            OOOOOOOO00O0OO000 ['cedent_type']=O00OOOOOO00O0O0OO ['cedents_to_do'][len (O00OOOOOO00O0O0OO ['cedents'])]#line:1074
            OO0OO0O0O0OO00000 =OOOOOOOO00O0OO000 ['cedent_type']#line:1075
            if ((OO0OO0O0O0OO00000 [-1 ]=='-')|(OO0OO0O0O0OO00000 [-1 ]=='+')):#line:1076
                OO0OO0O0O0OO00000 =OO0OO0O0O0OO00000 [:-1 ]#line:1077
            OOOOOOOO00O0OO000 ['defi']=OO00O0O00000O00O0 .kwargs .get (OO0OO0O0O0OO00000 )#line:1079
            if (OOOOOOOO00O0OO000 ['defi']==None ):#line:1080
                print ("Error getting cedent ",OOOOOOOO00O0OO000 ['cedent_type'])#line:1081
            _O00000O0O0OOOOOOO =int (0 )#line:1082
            OOOOOOOO00O0OO000 ['num_cedent']=len (OOOOOOOO00O0OO000 ['defi'].get ('attributes'))#line:1087
            if (OOOOOOOO00O0OO000 ['defi'].get ('type')=='con'):#line:1088
                _O00000O0O0OOOOOOO =(1 <<OO00O0O00000O00O0 .data ["rows_count"])-1 #line:1089
            OO00O0O00000O00O0 ._genvar (O00OOOOOO00O0O0OO ,OOOOOOOO00O0OO000 ,_OO0O00OO0O00OOO0O ,_OOOOO00000OOO0O0O ,_O00000O0O0OOOOOOO ,OOOOOOOO00O0OO000 ['defi'].get ('minlen'),OOOOOOOO00O0OO000 ['defi'].get ('maxlen'))#line:1090
    def _calc_all (O00OO0000O0O0OOO0 ,**O0OOO0O00OOO0OO0O ):#line:1093
        if "df"in O0OOO0O00OOO0OO0O :#line:1094
            O00OO0000O0O0OOO0 ._prep_data (O00OO0000O0O0OOO0 .kwargs .get ("df"))#line:1095
        if not (O00OO0000O0O0OOO0 ._initialized ):#line:1096
            print ("ERROR: dataframe is missing and not initialized with dataframe")#line:1097
        else :#line:1098
            O00OO0000O0O0OOO0 ._calculate (**O0OOO0O00OOO0OO0O )#line:1099
    def _check_cedents (OO0OOOO0O000O0OO0 ,O0OOO000O00OO0O0O ,**O00O0OO0O0OOO0OO0 ):#line:1101
        OO0O00O000OO0OO0O =True #line:1102
        if (O00O0OO0O0OOO0OO0 .get ('quantifiers',None )==None ):#line:1103
            print (f"Error: missing quantifiers.")#line:1104
            OO0O00O000OO0OO0O =False #line:1105
            return OO0O00O000OO0OO0O #line:1106
        if (type (O00O0OO0O0OOO0OO0 .get ('quantifiers'))!=dict ):#line:1107
            print (f"Error: quantifiers are not dictionary type.")#line:1108
            OO0O00O000OO0OO0O =False #line:1109
            return OO0O00O000OO0OO0O #line:1110
        for O0OOO00000OO00OO0 in O0OOO000O00OO0O0O :#line:1112
            if (O00O0OO0O0OOO0OO0 .get (O0OOO00000OO00OO0 ,None )==None ):#line:1113
                print (f"Error: cedent {O0OOO00000OO00OO0} is missing in parameters.")#line:1114
                OO0O00O000OO0OO0O =False #line:1115
                return OO0O00O000OO0OO0O #line:1116
            O00000OO0OO00O00O =O00O0OO0O0OOO0OO0 .get (O0OOO00000OO00OO0 )#line:1117
            if (O00000OO0OO00O00O .get ('minlen'),None )==None :#line:1118
                print (f"Error: cedent {O0OOO00000OO00OO0} has no minimal length specified.")#line:1119
                OO0O00O000OO0OO0O =False #line:1120
                return OO0O00O000OO0OO0O #line:1121
            if not (type (O00000OO0OO00O00O .get ('minlen'))is int ):#line:1122
                print (f"Error: cedent {O0OOO00000OO00OO0} has invalid type of minimal length ({type(O00000OO0OO00O00O.get('minlen'))}).")#line:1123
                OO0O00O000OO0OO0O =False #line:1124
                return OO0O00O000OO0OO0O #line:1125
            if (O00000OO0OO00O00O .get ('maxlen'),None )==None :#line:1126
                print (f"Error: cedent {O0OOO00000OO00OO0} has no maximal length specified.")#line:1127
                OO0O00O000OO0OO0O =False #line:1128
                return OO0O00O000OO0OO0O #line:1129
            if not (type (O00000OO0OO00O00O .get ('maxlen'))is int ):#line:1130
                print (f"Error: cedent {O0OOO00000OO00OO0} has invalid type of maximal length.")#line:1131
                OO0O00O000OO0OO0O =False #line:1132
                return OO0O00O000OO0OO0O #line:1133
            if (O00000OO0OO00O00O .get ('type'),None )==None :#line:1134
                print (f"Error: cedent {O0OOO00000OO00OO0} has no type specified.")#line:1135
                OO0O00O000OO0OO0O =False #line:1136
                return OO0O00O000OO0OO0O #line:1137
            if not ((O00000OO0OO00O00O .get ('type'))in (['con','dis'])):#line:1138
                print (f"Error: cedent {O0OOO00000OO00OO0} has invalid type. Allowed values are 'con' and 'dis'.")#line:1139
                OO0O00O000OO0OO0O =False #line:1140
                return OO0O00O000OO0OO0O #line:1141
            if (O00000OO0OO00O00O .get ('attributes'),None )==None :#line:1142
                print (f"Error: cedent {O0OOO00000OO00OO0} has no attributes specified.")#line:1143
                OO0O00O000OO0OO0O =False #line:1144
                return OO0O00O000OO0OO0O #line:1145
            for O0000000O00000OO0 in O00000OO0OO00O00O .get ('attributes'):#line:1146
                if (O0000000O00000OO0 .get ('name'),None )==None :#line:1147
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0} has no 'name' attribute specified.")#line:1148
                    OO0O00O000OO0OO0O =False #line:1149
                    return OO0O00O000OO0OO0O #line:1150
                if not ((O0000000O00000OO0 .get ('name'))in OO0OOOO0O000O0OO0 .data ["varname"]):#line:1151
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} not in variable list. Please check spelling.")#line:1152
                    OO0O00O000OO0OO0O =False #line:1153
                    return OO0O00O000OO0OO0O #line:1154
                if (O0000000O00000OO0 .get ('type'),None )==None :#line:1155
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has no 'type' attribute specified.")#line:1156
                    OO0O00O000OO0OO0O =False #line:1157
                    return OO0O00O000OO0OO0O #line:1158
                if not ((O0000000O00000OO0 .get ('type'))in (['rcut','lcut','seq','subset','one'])):#line:1159
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has unsupported type {O0000000O00000OO0.get('type')}. Supported types are 'subset','seq','lcut','rcut','one'.")#line:1160
                    OO0O00O000OO0OO0O =False #line:1161
                    return OO0O00O000OO0OO0O #line:1162
                if (O0000000O00000OO0 .get ('minlen'),None )==None :#line:1163
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has no minimal length specified.")#line:1164
                    OO0O00O000OO0OO0O =False #line:1165
                    return OO0O00O000OO0OO0O #line:1166
                if not (type (O0000000O00000OO0 .get ('minlen'))is int ):#line:1167
                    if not (O0000000O00000OO0 .get ('type')=='one'):#line:1168
                        print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has invalid type of minimal length.")#line:1169
                        OO0O00O000OO0OO0O =False #line:1170
                        return OO0O00O000OO0OO0O #line:1171
                if (O0000000O00000OO0 .get ('maxlen'),None )==None :#line:1172
                    print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has no maximal length specified.")#line:1173
                    OO0O00O000OO0OO0O =False #line:1174
                    return OO0O00O000OO0OO0O #line:1175
                if not (type (O0000000O00000OO0 .get ('maxlen'))is int ):#line:1176
                    if not (O0000000O00000OO0 .get ('type')=='one'):#line:1177
                        print (f"Error: cedent {O0OOO00000OO00OO0} / attribute {O0000000O00000OO0.get('name')} has invalid type of maximal length.")#line:1178
                        OO0O00O000OO0OO0O =False #line:1179
                        return OO0O00O000OO0OO0O #line:1180
        return OO0O00O000OO0OO0O #line:1181
    def _calculate (O0OOOOOO0O0O000OO ,**OOOO0OOO00000O000 ):#line:1183
        if O0OOOOOO0O0O000OO .data ["data_prepared"]==0 :#line:1184
            print ("Error: data not prepared")#line:1185
            return #line:1186
        O0OOOOOO0O0O000OO .kwargs =OOOO0OOO00000O000 #line:1187
        O0OOOOOO0O0O000OO .proc =OOOO0OOO00000O000 .get ('proc')#line:1188
        O0OOOOOO0O0O000OO .quantifiers =OOOO0OOO00000O000 .get ('quantifiers')#line:1189
        O0OOOOOO0O0O000OO ._init_task ()#line:1191
        O0OOOOOO0O0O000OO .stats ['start_proc_time']=time .time ()#line:1192
        O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do']=[]#line:1193
        O0OOOOOO0O0O000OO .task_actinfo ['cedents']=[]#line:1194
        if OOOO0OOO00000O000 .get ("proc")=='CFMiner':#line:1197
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do']=['cond']#line:1198
            if OOOO0OOO00000O000 .get ('target',None )==None :#line:1199
                print ("ERROR: no target variable defined for CF Miner")#line:1200
                return #line:1201
            if not (O0OOOOOO0O0O000OO ._check_cedents (['cond'],**OOOO0OOO00000O000 )):#line:1202
                return #line:1203
            if not (OOOO0OOO00000O000 .get ('target')in O0OOOOOO0O0O000OO .data ["varname"]):#line:1204
                print ("ERROR: target parameter is not variable. Please check spelling of variable name in parameter 'target'.")#line:1205
                return #line:1206
        elif OOOO0OOO00000O000 .get ("proc")=='4ftMiner':#line:1208
            if not (O0OOOOOO0O0O000OO ._check_cedents (['ante','succ'],**OOOO0OOO00000O000 )):#line:1209
                return #line:1210
            _OOOO000OOO0O0O0O0 =OOOO0OOO00000O000 .get ("cond")#line:1212
            if _OOOO000OOO0O0O0O0 !=None :#line:1213
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1214
            else :#line:1215
                OO00O0O0OO0000OOO =O0OOOOOO0O0O000OO .cedent #line:1216
                OO00O0O0OO0000OOO ['cedent_type']='cond'#line:1217
                OO00O0O0OO0000OOO ['filter_value']=(1 <<O0OOOOOO0O0O000OO .data ["rows_count"])-1 #line:1218
                OO00O0O0OO0000OOO ['generated_string']='---'#line:1219
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1221
                O0OOOOOO0O0O000OO .task_actinfo ['cedents'].append (OO00O0O0OO0000OOO )#line:1222
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('ante')#line:1226
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('succ')#line:1227
        elif OOOO0OOO00000O000 .get ("proc")=='NewAct4ftMiner':#line:1228
            _OOOO000OOO0O0O0O0 =OOOO0OOO00000O000 .get ("cond")#line:1231
            if _OOOO000OOO0O0O0O0 !=None :#line:1232
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1233
            else :#line:1234
                OO00O0O0OO0000OOO =O0OOOOOO0O0O000OO .cedent #line:1235
                OO00O0O0OO0000OOO ['cedent_type']='cond'#line:1236
                OO00O0O0OO0000OOO ['filter_value']=(1 <<O0OOOOOO0O0O000OO .data ["rows_count"])-1 #line:1237
                OO00O0O0OO0000OOO ['generated_string']='---'#line:1238
                print (OO00O0O0OO0000OOO ['filter_value'])#line:1239
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1240
                O0OOOOOO0O0O000OO .task_actinfo ['cedents'].append (OO00O0O0OO0000OOO )#line:1241
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('antv')#line:1242
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('sucv')#line:1243
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('ante')#line:1244
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('succ')#line:1245
        elif OOOO0OOO00000O000 .get ("proc")=='Act4ftMiner':#line:1246
            _OOOO000OOO0O0O0O0 =OOOO0OOO00000O000 .get ("cond")#line:1249
            if _OOOO000OOO0O0O0O0 !=None :#line:1250
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1251
            else :#line:1252
                OO00O0O0OO0000OOO =O0OOOOOO0O0O000OO .cedent #line:1253
                OO00O0O0OO0000OOO ['cedent_type']='cond'#line:1254
                OO00O0O0OO0000OOO ['filter_value']=(1 <<O0OOOOOO0O0O000OO .data ["rows_count"])-1 #line:1255
                OO00O0O0OO0000OOO ['generated_string']='---'#line:1256
                print (OO00O0O0OO0000OOO ['filter_value'])#line:1257
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1258
                O0OOOOOO0O0O000OO .task_actinfo ['cedents'].append (OO00O0O0OO0000OOO )#line:1259
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('antv-')#line:1260
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('antv+')#line:1261
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('sucv-')#line:1262
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('sucv+')#line:1263
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('ante')#line:1264
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('succ')#line:1265
        elif OOOO0OOO00000O000 .get ("proc")=='SD4ftMiner':#line:1266
            if not (O0OOOOOO0O0O000OO ._check_cedents (['ante','succ','frst','scnd'],**OOOO0OOO00000O000 )):#line:1269
                return #line:1270
            _OOOO000OOO0O0O0O0 =OOOO0OOO00000O000 .get ("cond")#line:1271
            if _OOOO000OOO0O0O0O0 !=None :#line:1272
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1273
            else :#line:1274
                OO00O0O0OO0000OOO =O0OOOOOO0O0O000OO .cedent #line:1275
                OO00O0O0OO0000OOO ['cedent_type']='cond'#line:1276
                OO00O0O0OO0000OOO ['filter_value']=(1 <<O0OOOOOO0O0O000OO .data ["rows_count"])-1 #line:1277
                OO00O0O0OO0000OOO ['generated_string']='---'#line:1278
                O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('cond')#line:1280
                O0OOOOOO0O0O000OO .task_actinfo ['cedents'].append (OO00O0O0OO0000OOO )#line:1281
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('frst')#line:1282
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('scnd')#line:1283
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('ante')#line:1284
            O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do'].append ('succ')#line:1285
        else :#line:1286
            print ("Unsupported procedure")#line:1287
            return #line:1288
        print ("Will go for ",OOOO0OOO00000O000 .get ("proc"))#line:1289
        O0OOOOOO0O0O000OO .task_actinfo ['optim']={}#line:1292
        OO0000O0OO00O00OO =True #line:1293
        for O0O00O0O000OOO0OO in O0OOOOOO0O0O000OO .task_actinfo ['cedents_to_do']:#line:1294
            try :#line:1295
                OO00OO0O00000O000 =O0OOOOOO0O0O000OO .kwargs .get (O0O00O0O000OOO0OO )#line:1296
                if OO00OO0O00000O000 .get ('type')!='con':#line:1300
                    OO0000O0OO00O00OO =False #line:1301
            except :#line:1303
                OO0O00O0OO00OOOO0 =1 <2 #line:1304
        if O0OOOOOO0O0O000OO .options ['optimizations']==False :#line:1306
            OO0000O0OO00O00OO =False #line:1307
        OO00O0000O0OO000O ={}#line:1308
        OO00O0000O0OO000O ['only_con']=OO0000O0OO00O00OO #line:1309
        O0OOOOOO0O0O000OO .task_actinfo ['optim']=OO00O0000O0OO000O #line:1310
        print ("Starting to mine rules.")#line:1318
        O0OOOOOO0O0O000OO ._start_cedent (O0OOOOOO0O0O000OO .task_actinfo )#line:1319
        O0OOOOOO0O0O000OO .stats ['end_proc_time']=time .time ()#line:1321
        print ("Done. Total verifications : "+str (O0OOOOOO0O0O000OO .stats ['total_cnt'])+", rules "+str (O0OOOOOO0O0O000OO .stats ['total_valid'])+",control number:"+str (O0OOOOOO0O0O000OO .stats ['control_number'])+", times: prep "+str (O0OOOOOO0O0O000OO .stats ['end_prep_time']-O0OOOOOO0O0O000OO .stats ['start_prep_time'])+", processing "+str (O0OOOOOO0O0O000OO .stats ['end_proc_time']-O0OOOOOO0O0O000OO .stats ['start_proc_time']))#line:1324
        O000O0OOO000O0O0O ={}#line:1325
        OOOO00OO0O00OO00O ={}#line:1326
        OOOO00OO0O00OO00O ["task_type"]=OOOO0OOO00000O000 .get ('proc')#line:1327
        OOOO00OO0O00OO00O ["target"]=OOOO0OOO00000O000 .get ('target')#line:1329
        OOOO00OO0O00OO00O ["self.quantifiers"]=O0OOOOOO0O0O000OO .quantifiers #line:1330
        if OOOO0OOO00000O000 .get ('cond')!=None :#line:1332
            OOOO00OO0O00OO00O ['cond']=OOOO0OOO00000O000 .get ('cond')#line:1333
        if OOOO0OOO00000O000 .get ('ante')!=None :#line:1334
            OOOO00OO0O00OO00O ['ante']=OOOO0OOO00000O000 .get ('ante')#line:1335
        if OOOO0OOO00000O000 .get ('succ')!=None :#line:1336
            OOOO00OO0O00OO00O ['succ']=OOOO0OOO00000O000 .get ('succ')#line:1337
        if OOOO0OOO00000O000 .get ('opts')!=None :#line:1338
            OOOO00OO0O00OO00O ['opts']=OOOO0OOO00000O000 .get ('opts')#line:1339
        O000O0OOO000O0O0O ["taskinfo"]=OOOO00OO0O00OO00O #line:1340
        OOO00OOOOOOO00O00 ={}#line:1341
        OOO00OOOOOOO00O00 ["total_verifications"]=O0OOOOOO0O0O000OO .stats ['total_cnt']#line:1342
        OOO00OOOOOOO00O00 ["valid_rules"]=O0OOOOOO0O0O000OO .stats ['total_valid']#line:1343
        OOO00OOOOOOO00O00 ["total_verifications_with_opt"]=O0OOOOOO0O0O000OO .stats ['total_ver']#line:1344
        OOO00OOOOOOO00O00 ["time_prep"]=O0OOOOOO0O0O000OO .stats ['end_prep_time']-O0OOOOOO0O0O000OO .stats ['start_prep_time']#line:1345
        OOO00OOOOOOO00O00 ["time_processing"]=O0OOOOOO0O0O000OO .stats ['end_proc_time']-O0OOOOOO0O0O000OO .stats ['start_proc_time']#line:1346
        OOO00OOOOOOO00O00 ["time_total"]=O0OOOOOO0O0O000OO .stats ['end_prep_time']-O0OOOOOO0O0O000OO .stats ['start_prep_time']+O0OOOOOO0O0O000OO .stats ['end_proc_time']-O0OOOOOO0O0O000OO .stats ['start_proc_time']#line:1347
        O000O0OOO000O0O0O ["summary_statistics"]=OOO00OOOOOOO00O00 #line:1348
        O000O0OOO000O0O0O ["rules"]=O0OOOOOO0O0O000OO .rulelist #line:1349
        OO000OOO0OOO000OO ={}#line:1350
        OO000OOO0OOO000OO ["varname"]=O0OOOOOO0O0O000OO .data ["varname"]#line:1351
        OO000OOO0OOO000OO ["catnames"]=O0OOOOOO0O0O000OO .data ["catnames"]#line:1352
        O000O0OOO000O0O0O ["datalabels"]=OO000OOO0OOO000OO #line:1353
        O0OOOOOO0O0O000OO .result =O000O0OOO000O0O0O #line:1356
    def print_summary (OOOOOO0O000OOOO00 ):#line:1358
        print ("")#line:1359
        print ("CleverMiner task processing summary:")#line:1360
        print ("")#line:1361
        print (f"Task type : {OOOOOO0O000OOOO00.result['taskinfo']['task_type']}")#line:1362
        print (f"Number of verifications : {OOOOOO0O000OOOO00.result['summary_statistics']['total_verifications']}")#line:1363
        print (f"Number of rules : {OOOOOO0O000OOOO00.result['summary_statistics']['valid_rules']}")#line:1364
        print (f"Total time needed : {strftime('%Hh %Mm %Ss', gmtime(OOOOOO0O000OOOO00.result['summary_statistics']['time_total']))}")#line:1365
        print (f"Time of data preparation : {strftime('%Hh %Mm %Ss', gmtime(OOOOOO0O000OOOO00.result['summary_statistics']['time_prep']))}")#line:1367
        print (f"Time of rule mining : {strftime('%Hh %Mm %Ss', gmtime(OOOOOO0O000OOOO00.result['summary_statistics']['time_processing']))}")#line:1368
        print ("")#line:1369
    def print_hypolist (O00OOO0O0000OO000 ):#line:1371
        O00OOO0O0000OO000 .print_rulelist ();#line:1372
    def print_rulelist (O0O0O00OO0000O000 ):#line:1374
        print ("")#line:1376
        print ("List of rules:")#line:1377
        if O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="4ftMiner":#line:1378
            print ("RULEID BASE  CONF  AAD    Rule")#line:1379
        elif O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="CFMiner":#line:1380
            print ("RULEID BASE  S_UP  S_DOWN Condition")#line:1381
        elif O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1382
            print ("RULEID BASE1 BASE2 RatioConf DeltaConf Rule")#line:1383
        else :#line:1384
            print ("Unsupported task type for rulelist")#line:1385
            return #line:1386
        for O0O0O0OO00O0O0OO0 in O0O0O00OO0000O000 .result ["rules"]:#line:1387
            OO0OO0OO0O000000O ="{:6d}".format (O0O0O0OO00O0O0OO0 ["rule_id"])#line:1388
            if O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="4ftMiner":#line:1389
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["base"])+" "+"{:.3f}".format (O0O0O0OO00O0O0OO0 ["params"]["conf"])+" "+"{:+.3f}".format (O0O0O0OO00O0O0OO0 ["params"]["aad"])#line:1390
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +" "+O0O0O0OO00O0O0OO0 ["cedents_str"]["ante"]+" => "+O0O0O0OO00O0O0OO0 ["cedents_str"]["succ"]+" | "+O0O0O0OO00O0O0OO0 ["cedents_str"]["cond"]#line:1391
            elif O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="CFMiner":#line:1392
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["base"])+" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["s_up"])+" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["s_down"])#line:1393
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +" "+O0O0O0OO00O0O0OO0 ["cedents_str"]["cond"]#line:1394
            elif O0O0O00OO0000O000 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1395
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["base1"])+" "+"{:5d}".format (O0O0O0OO00O0O0OO0 ["params"]["base2"])+"    "+"{:.3f}".format (O0O0O0OO00O0O0OO0 ["params"]["ratioconf"])+"    "+"{:+.3f}".format (O0O0O0OO00O0O0OO0 ["params"]["deltaconf"])#line:1396
                OO0OO0OO0O000000O =OO0OO0OO0O000000O +"  "+O0O0O0OO00O0O0OO0 ["cedents_str"]["ante"]+" => "+O0O0O0OO00O0O0OO0 ["cedents_str"]["succ"]+" | "+O0O0O0OO00O0O0OO0 ["cedents_str"]["cond"]+" : "+O0O0O0OO00O0O0OO0 ["cedents_str"]["frst"]+" x "+O0O0O0OO00O0O0OO0 ["cedents_str"]["scnd"]#line:1397
            print (OO0OO0OO0O000000O )#line:1399
        print ("")#line:1400
    def print_hypo (O000O0O0O00OOOOOO ,O0O0OOO00OOO00000 ):#line:1402
        O000O0O0O00OOOOOO .print_rule (O0O0OOO00OOO00000 )#line:1403
    def print_rule (OOOO000O0000O000O ,OOOO00O00O0000O0O ):#line:1406
        print ("")#line:1407
        if (OOOO00O00O0000O0O <=len (OOOO000O0000O000O .result ["rules"])):#line:1408
            if OOOO000O0000O000O .result ['taskinfo']['task_type']=="4ftMiner":#line:1409
                print ("")#line:1410
                O0O00O00O0O000000 =OOOO000O0000O000O .result ["rules"][OOOO00O00O0000O0O -1 ]#line:1411
                print (f"Rule id : {O0O00O00O0O000000['rule_id']}")#line:1412
                print ("")#line:1413
                print (f"Base : {'{:5d}'.format(O0O00O00O0O000000['params']['base'])}  Relative base : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_base'])}  CONF : {'{:.3f}'.format(O0O00O00O0O000000['params']['conf'])}  AAD : {'{:+.3f}'.format(O0O00O00O0O000000['params']['aad'])}  BAD : {'{:+.3f}'.format(O0O00O00O0O000000['params']['bad'])}")#line:1414
                print ("")#line:1415
                print ("Cedents:")#line:1416
                print (f"  antecedent : {O0O00O00O0O000000['cedents_str']['ante']}")#line:1417
                print (f"  succcedent : {O0O00O00O0O000000['cedents_str']['succ']}")#line:1418
                print (f"  condition  : {O0O00O00O0O000000['cedents_str']['cond']}")#line:1419
                print ("")#line:1420
                print ("Fourfold table")#line:1421
                print (f"    |  S  |  ¬S |")#line:1422
                print (f"----|-----|-----|")#line:1423
                print (f" A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold'][0])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold'][1])}|")#line:1424
                print (f"----|-----|-----|")#line:1425
                print (f"¬A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold'][2])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold'][3])}|")#line:1426
                print (f"----|-----|-----|")#line:1427
            elif OOOO000O0000O000O .result ['taskinfo']['task_type']=="CFMiner":#line:1428
                print ("")#line:1429
                O0O00O00O0O000000 =OOOO000O0000O000O .result ["rules"][OOOO00O00O0000O0O -1 ]#line:1430
                print (f"Rule id : {O0O00O00O0O000000['rule_id']}")#line:1431
                print ("")#line:1432
                print (f"Base : {'{:5d}'.format(O0O00O00O0O000000['params']['base'])}  Relative base : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_base'])}  Steps UP (consecutive) : {'{:5d}'.format(O0O00O00O0O000000['params']['s_up'])}  Steps DOWN (consecutive) : {'{:5d}'.format(O0O00O00O0O000000['params']['s_down'])}  Steps UP (any) : {'{:5d}'.format(O0O00O00O0O000000['params']['s_any_up'])}  Steps DOWN (any) : {'{:5d}'.format(O0O00O00O0O000000['params']['s_any_down'])}  Histogram maximum : {'{:5d}'.format(O0O00O00O0O000000['params']['max'])}  Histogram minimum : {'{:5d}'.format(O0O00O00O0O000000['params']['min'])}  Histogram relative maximum : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_max'])} Histogram relative minimum : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_min'])}")#line:1434
                print ("")#line:1435
                print (f"Condition  : {O0O00O00O0O000000['cedents_str']['cond']}")#line:1436
                print ("")#line:1437
                print (f"Histogram {O0O00O00O0O000000['params']['hist']}")#line:1438
            elif OOOO000O0000O000O .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1439
                print ("")#line:1440
                O0O00O00O0O000000 =OOOO000O0000O000O .result ["rules"][OOOO00O00O0000O0O -1 ]#line:1441
                print (f"Rule id : {O0O00O00O0O000000['rule_id']}")#line:1442
                print ("")#line:1443
                print (f"Base1 : {'{:5d}'.format(O0O00O00O0O000000['params']['base1'])} Base2 : {'{:5d}'.format(O0O00O00O0O000000['params']['base2'])}  Relative base 1 : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_base1'])} Relative base 2 : {'{:.3f}'.format(O0O00O00O0O000000['params']['rel_base2'])} CONF1 : {'{:.3f}'.format(O0O00O00O0O000000['params']['conf1'])}  CONF2 : {'{:+.3f}'.format(O0O00O00O0O000000['params']['conf2'])}  Delta Conf : {'{:+.3f}'.format(O0O00O00O0O000000['params']['deltaconf'])} Ratio Conf : {'{:+.3f}'.format(O0O00O00O0O000000['params']['ratioconf'])}")#line:1444
                print ("")#line:1445
                print ("Cedents:")#line:1446
                print (f"  antecedent : {O0O00O00O0O000000['cedents_str']['ante']}")#line:1447
                print (f"  succcedent : {O0O00O00O0O000000['cedents_str']['succ']}")#line:1448
                print (f"  condition  : {O0O00O00O0O000000['cedents_str']['cond']}")#line:1449
                print (f"  first set  : {O0O00O00O0O000000['cedents_str']['frst']}")#line:1450
                print (f"  second set : {O0O00O00O0O000000['cedents_str']['scnd']}")#line:1451
                print ("")#line:1452
                print ("Fourfold tables:")#line:1453
                print (f"FRST|  S  |  ¬S |  SCND|  S  |  ¬S |");#line:1454
                print (f"----|-----|-----|  ----|-----|-----| ")#line:1455
                print (f" A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold1'][0])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold1'][1])}|   A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold2'][0])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold2'][1])}|")#line:1456
                print (f"----|-----|-----|  ----|-----|-----|")#line:1457
                print (f"¬A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold1'][2])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold1'][3])}|  ¬A  |{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold2'][2])}|{'{:5d}'.format(O0O00O00O0O000000['params']['fourfold2'][3])}|")#line:1458
                print (f"----|-----|-----|  ----|-----|-----|")#line:1459
            else :#line:1460
                print ("Unsupported task type for rule details")#line:1461
            print ("")#line:1465
        else :#line:1466
            print ("No such rule.")#line:1467
    def get_rulecount (OOOOO00OOO0OO0OO0 ):#line:1469
        return len (OOOOO00OOO0OO0OO0 .result ["rules"])#line:1470
    def get_fourfold (OO0O000000000O0O0 ,OOO0OO0O0000O0000 ,order =0 ):#line:1472
        if (OOO0OO0O0000O0000 <=len (OO0O000000000O0O0 .result ["rules"])):#line:1474
            if OO0O000000000O0O0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1475
                O0O00000000OO00OO =OO0O000000000O0O0 .result ["rules"][OOO0OO0O0000O0000 -1 ]#line:1476
                return O0O00000000OO00OO ['params']['fourfold']#line:1477
            elif OO0O000000000O0O0 .result ['taskinfo']['task_type']=="CFMiner":#line:1478
                print ("Error: fourfold for CFMiner is not defined")#line:1479
                return None #line:1480
            elif OO0O000000000O0O0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1481
                O0O00000000OO00OO =OO0O000000000O0O0 .result ["rules"][OOO0OO0O0000O0000 -1 ]#line:1482
                if order ==1 :#line:1483
                    return O0O00000000OO00OO ['params']['fourfold1']#line:1484
                if order ==2 :#line:1485
                    return O0O00000000OO00OO ['params']['fourfold2']#line:1486
                print ("Error: for SD4ft-Miner, you need to provide order of fourfold table in order= parameter (valid values are 1,2).")#line:1487
                return None #line:1488
            else :#line:1489
                print ("Unsupported task type for rule details")#line:1490
        else :#line:1491
            print ("No such rule.")#line:1492
    def get_hist (O000OOO000O0O00O0 ,OO0OOO00O0O0O00O0 ):#line:1494
        if (OO0OOO00O0O0O00O0 <=len (O000OOO000O0O00O0 .result ["rules"])):#line:1496
            if O000OOO000O0O00O0 .result ['taskinfo']['task_type']=="CFMiner":#line:1497
                OOO0OO0000O0O0OO0 =O000OOO000O0O00O0 .result ["rules"][OO0OOO00O0O0O00O0 -1 ]#line:1498
                return OOO0OO0000O0O0OO0 ['params']['hist']#line:1499
            elif O000OOO000O0O00O0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1500
                print ("Error: SD4ft-Miner has no histogram")#line:1501
                return None #line:1502
            elif O000OOO000O0O00O0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1503
                print ("Error: 4ft-Miner has no histogram")#line:1504
                return None #line:1505
            else :#line:1506
                print ("Unsupported task type for rule details")#line:1507
        else :#line:1508
            print ("No such rule.")#line:1509
    def get_quantifiers (O0OO00O000OOOO00O ,OOO0000OOOOO0O00O ,order =0 ):#line:1511
        if (OOO0000OOOOO0O00O <=len (O0OO00O000OOOO00O .result ["rules"])):#line:1513
            OOO00OO0O0O00000O =O0OO00O000OOOO00O .result ["rules"][OOO0000OOOOO0O00O -1 ]#line:1514
            if O0OO00O000OOOO00O .result ['taskinfo']['task_type']=="4ftMiner":#line:1515
                return OOO00OO0O0O00000O ['params']#line:1516
            elif O0OO00O000OOOO00O .result ['taskinfo']['task_type']=="CFMiner":#line:1517
                return OOO00OO0O0O00000O ['params']#line:1518
            elif O0OO00O000OOOO00O .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1519
                return OOO00OO0O0O00000O ['params']#line:1520
            else :#line:1521
                print ("Unsupported task type for rule details")#line:1522
        else :#line:1523
            print ("No such rule.")#line:1524
