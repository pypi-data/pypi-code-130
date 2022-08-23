import pandas as pd
import numpy as np
import smtplib, ssl
import gspread
from df2gspread import gspread2df as g2d
from bcpandas import SqlCreds, to_sql

# try:
#     from .pistil_db_utilities import create_db_connection_db_matching
# except:
#     from pistil_db_utilities import create_db_connection_db_matching


def get_stats(df, verbose=False):
    l = []
    for col in df.columns:
        if verbose:
            print(col)

        s = float(len(df))

        nn = float(df[col].count())
        nn_pct = nn / s

        unique = len(df[col].unique())
        unique_pct = round(unique / s, 2)

        null = pd.isnull(df[col]).sum()
        null_pct = round(null / s, 2)

        vc = df[col].value_counts()
        if len(vc) > 0:
            mf = pd.DataFrame(df[col].value_counts()).iloc[0, 0]
        else:
            mf = 0

        if nn != 0:
            mf_pct = round(mf / nn, 2)
        else:
            mf_pct = 0.0

        binary = len("{0:b}".format(unique))

        l.append([col, nn, nn_pct, unique, unique_pct, binary, null, null_pct, mf, mf_pct])
    d = pd.DataFrame(l, columns=['col', 'not_null', 'not_null_pct', 'unique_values', 'unique_pct', 'binary', 'null',
                                 'null_pct', 'most_frequent', 'mf_pct'])
    return d

def value_counts_pct(se_col):
    vc = se_col.value_counts(dropna=False).to_frame()
    vc_pct = (se_col.value_counts(dropna=False) / float(len(se_col))).to_frame()
    vc_pct = vc_pct.applymap(lambda x: str(100 * round(x, 2)) + '%')
    df = pd.concat([vc, vc_pct], axis=1)
    df.columns = [se_col.name, se_col.name + '_pct']
    return df

def get_precision_recall_fscore_mcc(tp, tn, fp, fn):
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = 2 * (precision * recall) / (precision + recall)

    N = tp + tn + fn + fp
    S = (tp + fn) / N
    P = (tp + fp) / N
    MCC = ((tp / N) - (S * P)) / np.sqrt((P * S * (1 - S)) * (1 - P)) 
    return precision, recall, fscore, MCC

def get_general_changes(df1, df2, key, verbose=False):
    inner_keys = list(set(df2[key]).intersection(df1[key]))
    inner_columns = list(set(df2.columns).intersection(df1.columns))

    if verbose:
        print(inner_columns)
        print(len(inner_keys), len(df1), len(df2))

    q1 = (df1[df1[key].isin(inner_keys)]
          .drop_duplicates(subset=key)
          .sort_values(by=key)
          [inner_columns]
          .set_index(key)
          .fillna('NaN_f')
          .applymap(lambda x: float(x) if type(x) == int or (type(x) == str and x.isnumeric()) else x)
          .applymap(lambda x: str(x))
          )

    q2 = (df2[df2[key].isin(inner_keys)]
          .drop_duplicates(subset=key)
          .sort_values(by=key)
          [inner_columns]
          .set_index(key)
          .fillna('NaN_f')
          .applymap(lambda x: float(x) if type(x) == int or (type(x) == str and x.isnumeric()) else x)
          .applymap(lambda x: str(x))
          )

    inner_columns.remove(key)
    comp = pd.DataFrame()
    for col in inner_columns:
        comp[col] = q1[col] == q2[col]

    aux = comp.T.copy(deep=True)
    l = []
    for col in aux:
        idx = list(aux[aux[col] == False].index)
        l.append([col, idx])

    aux = pd.merge(q1.reset_index(), q2.reset_index(), on=key, suffixes=('_CURRENT', '_NEW'))
    aux = aux[sorted(aux.columns)]

    changes = pd.DataFrame(l, columns=[key, 'changes'])
    changes['changes'] = changes['changes'].apply(lambda x: str(x))
    changes = pd.merge(changes, aux, on=key)

    return changes

def readable_time(time: float):
    if time < 60:
        print(f'time: {round(time, 2)} seconds\n')
    else:
        print(f'time: {round(time / 60, 2)} minutes\n')

# FUNCTIONS FOR FILLING BY KEYS
def fill_by_key(subdf: pd.core.frame.DataFrame, key: str, col_fill: str) -> pd.core.frame.DataFrame:
    full = (subdf[~pd.isnull(subdf[col_fill])]
        .drop_duplicates(key)
    [[key, col_fill]])
    empty = subdf[pd.isnull(subdf[col_fill])][[key]]

    filled = pd.merge(empty, full, on=key, how='left')
    filled.index = empty.index

    subdf[col_fill] = subdf[col_fill].fillna(filled[col_fill])
    return subdf


def fill_by_keys(subdf: pd.core.frame.DataFrame, keys: list, col_fill: str) -> pd.core.frame.DataFrame:
    full = (subdf[~pd.isnull(subdf[col_fill])]
            .drop_duplicates(subset=keys)
            [keys + [col_fill]]
            .dropna())

    empty = subdf[pd.isnull(subdf[col_fill])][keys].dropna()

    filled = pd.merge(empty, full, on=keys, how='left')
    filled.index = empty.index

    subdf[col_fill] = subdf[col_fill].fillna(filled[col_fill])
    return subdf


def fill_by_keys_many_sources(keys, dest, source, col_fill):
    df1 = dest[keys]
    df2 = source[keys + [col_fill]].dropna().drop_duplicates()
    filled = pd.merge(df1, df2, on=keys, how='left')[col_fill]
    dest[col_fill] = dest[col_fill].fillna(filled)
    return dest


def fill_info(df,col_info,col_fill,fill_func,subs_dict: dict = None,multi_col:bool = False,nnext=10,verbose=False, **kwarg):
    '''
    This function is used to fill data in a column (col_fill) using data from another column (col_info).
    The logic used fill the information is executed in the "fill_func".
    A dictionary with the substitution rules can be used as an optional parameter.
    
    Arguments:
    
    df: dataframe
    col_info: column to extract information from
    col_fill: column to be filled with information    
    fill_func: function to handle the logic
    subs_dict: dictionary with substitution rules -optional   
    multi_col: multiple columns as info
    verbose: display information about coverage
    kwarg: keyword variable arguments - optional
    '''
    s=None
    query = df[pd.isnull(df[col_fill])]
    
    if len(query)>0:
        if multi_col is False:
            if subs_dict is not None:
                if kwarg:
                    s = query[col_info].apply(fill_func,subs_dict=subs_dict,**kwarg).copy(deep=True)
                else:
                    s = query[col_info].apply(fill_func,subs_dict=subs_dict).copy(deep=True)
            else:
                s = query[col_info].apply(fill_func).copy(deep=True)
        else:
            if subs_dict is not None:
                if kwarg:
                    s = query[col_info].apply(fill_func,subs_dict=subs_dict,**kwarg,axis=1).copy(deep=True)
                else:
                    s = query[col_info].apply(fill_func,subs_dict=subs_dict,axis=1).copy(deep=True)
            else:
                s = query[col_info].apply(fill_func,axis=1).copy(deep=True)
    
        df[col_fill] = df[col_fill].fillna(s)

        query = df[pd.isnull(df[col_fill])]

        coverage = (~pd.isnull(df[col_fill])).sum()/len(df)
        if verbose: print(coverage)

        next_address = ((query[col_info].value_counts().cumsum())/len(df)) + coverage
        if verbose: print(next_address[:nnext])
            
    else:
        print(f'no null values for {col_fill}')
    
    return df

def get_composite_key(x,cols):
    l=[]
    for i,k in enumerate(x):
        if k=='':
            k='null'
        k=(str(k).lower()
           .replace('.','_')
           .replace(' ','_'))
        k=f'[{cols[i]}]_{k}'
        l.append(k)
    return '__'.join(l)

def get_stores_brand_count(last=None,current=None,library_retailers=None,sources=None):
    
    if sources is None:
        sources = ['Weedmaps','I Heart Jane', 'Dutchie', 'Meadow', 'Treez','Weedmaps (sec)']
    else:
        l=[]
        for k in sources:
            if k=='ihj':
                k='I Heart Jane'
            else:
                k=k.title()
            l.append(k)
        sources = l
    
    aux=library_retailers[library_retailers['operational_store']=='1'].copy(deep=True)
    valid_stores = aux['store_name'].to_list()
    
    if last is not None:
        aux=last[last['store_name'].isin(valid_stores)]
        aux=aux.groupby('store_name')['brand'].nunique().reset_index()
        q=set(valid_stores) -  set(aux['store_name'])
        q=pd.DataFrame(q,columns=['store_name'])
        q['brand'] = 0
        aux=aux.append(q)
        last = aux.copy(deep=True)
        last.columns = ['store','last']
    
    if current is not None:
        aux=current[current['store_name'].isin(valid_stores)]
        aux=aux.groupby('store_name')['brand'].nunique().reset_index()
        q=set(valid_stores) -  set(aux['store_name'])
        q=pd.DataFrame(q,columns=['store_name'])
        q['brand'] = 0
        aux=aux.append(q)
        current = aux.copy(deep=True)
        current.columns = ['store','current']
    
    if current is not None and last is None:
        return current
    elif last is not None and current is None:
        return last
    
    aux=pd.merge(last,current,on='store')
    return aux


def send_email(sender_email=None,receiver_email=None,password=None,message=None):

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    
    if sender_email is None:
        sender_email = "mendesdev20@gmail.com"  # Enter your address
        
    if receiver_email is None:
        receiver_email = "andremendes19912@gmail.com"  # Enter receiver address
        
    if password is None:
        password = 'pass#123#pass#123'
        
    if message is None:
        message = """
                The code is running
             """

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def delete_column_gsheet(spreadsheetId: str
                         ,sheetName: str
                         ,start_index: int = 0
                         ,end_index: int = 0)->None:
    
    gc = gspread.service_account()

    spreadsheet = gc.open_by_key(spreadsheetId)
    sheetId = spreadsheet.worksheet(sheetName)._properties['sheetId']
    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                        "startIndex": start_index,
                        "endIndex": end_index
                    }
                }
            }
        ]
    }
    res = spreadsheet.batch_update(body)
    print(res)
    
def standardize_columns(df):
    """
    Standardizes string columns only:
    1-Remove trailing spaces from ends
    2-Lowercase each value
    """
    
    std_strings = lambda x: x.strip().lower() if isinstance(x, str) else x
    return df.applymap(std_strings)    
    
def load_subs_df2dict(form: str ='sheets'
                      , sheet_id: str = None
                      , table_name: str = None
                      , wks_name : str = None
                      , schema: str = None                                            
                      , tup_keys: dict = None):
    
    '''This function will download a google spreadsheet as a dataframe and convert to a dictionary.
    the dictionary can contain lists, tuples or dictionaries.
    if a column is not present in dic_keys or tup_keys it is treated as a list
    the parameters dic_keys and tup_keys define the colum types.    
    for tuples it will use every column that starts with key and generate a single tuple
    
    Arguments:
    form: "sheet" to read from google spread sheet or "database" from sql database
    sheet_id: spreadsheet id in google drive
    table_name: table name in sql server
    wks_name: work sheet name in spreadsheet file
    schema: database schema in sql server    
    tup_keys: rows of tuple type    
    '''
    
    if form =='sheets':
        #downloading pre roll substitutions
        sheet_id = sheet_id
        wks_name = wks_name
        subs_df = g2d.download(gfile=sheet_id,wks_name=wks_name,col_names=True,row_names=False).reset_index(drop=True)
   
    elif form =='database':
        conn = create_db_connection_db_matching()
        subs_df = pd.read_sql_table(table_name=table_name,schema= schema,con=conn)
        conn.close()        
    
    #dictionary functions in source notebooks
    dict_sources = ['dutchie','ihj','meadow','treez','weedmaps','general']    
    
    #full substitutions dictionary
    subs_dic = {}   
        
    for source in dict_sources:
        subsdf_filtered = subs_df[['function','type','key','key2','value']][
            (subs_df['source'] == source) ]                    

        # standardize string columns
        subsdf_filtered = standardize_columns(subsdf_filtered)
        
        #creates preroll style dict from df, tuples and dicts as keys        
        subs_dic_temp = df2dict_dic_li_tup(subsdf_filtered, tup_keys = tup_keys)                                   

        subs_dic[source] = subs_dic_temp               
                
    return subs_dic

def df2dict_dic_li_tup(subs_df, tup_keys = None):
    '''This function will turns a dataframe into a dictionary containing lists, tuples or dictionaries,
    depending on what's passed as a parameter for list_keys and tup_keys. For dictionaries, it will use both key and value.
    for lists/, what matters is only the 'value' field,for tuples it will use every column that starts with key
    and generate a single tuple    
    if a column is not present in dic_keys or tup_keys it is treated as a list
    '''    
        
    subs_dic = {}
    dic_keys = set(subs_df['type'])
       
    if tup_keys is not None:
        dic_keys = dic_keys - tup_keys
    
    #if li_keys is not None:
        #dic_keys = dic_keys - li_keys

    #initializing the dictionary
    for function in subs_df['function']:
        subs_dic[function] = {}
        for t in set(subs_df['type'][subs_df['function'] == function]):
            if t in dic_keys:
                subs_dic[function][t] = {}            
            # quick fix to turn lists into dict keys
            #elif t in li_keys:
                #subs_dic[function][t] = []                
            elif (tup_keys is not None) and (t in tup_keys):
                subs_dic[function][t] = {(): ''}
            else:
                print('invalid structure type: '+str(t))

    #populating
    for row in subs_df.itertuples():

        if row.type in dic_keys:    
            
            if row.key == 'null':
                print('null key in row: ' + str(row))
 
            subs_dic[row.function][row.type][row.key] = row.value
                
        # quick fix to turn lists into dict keys
        #elif row.type in li_keys:
            #subs_dic[row.function][row.type].append(row.value)            

        elif row.type in tup_keys:       
            #columns with name starting with key 
            tups_cols = subs_df.columns[subs_df.columns.map(lambda x: x.startswith("key"))]
            
            #first col with key name, adds +1 because index is being used in df.itertuples()
            first_keyloc = subs_df.columns.get_loc(tups_cols[0]) +1         
            subs_dic[row.function][row.type][row[first_keyloc:-1]] = row.value
            
            if () in subs_dic[row.function][row.type].keys():
                del subs_dic[row.function][row.type][()]
        else:
            print('Invalid structure: '+row.type)
    return subs_dic

def convert_to_closer_valid_weight(x):
    """This function aggregates fractioned weights into their most common form, as observed in ihj as a reference.
    The value will almost always fallback to the closer discrete value, below. There are exceptions for 3.5 and 3.3"""
    if pd.isnull(x):
        return x
    valid_weights = [0.2
                 ,0.25
                 ,0.28
                 ,0.3
                 ,0.35
                 ,0.375
                 ,0.4
                 ,0.5
                 ,0.6
                 ,0.65
                 ,0.67
                 ,0.7
                 ,0.75
                 ,0.8
                 ,0.85
                 ,0.9
                 ,1
                 ,1.2
                 ,1.3
                 ,1.4
                 ,1.5
                 ,1.6
                 ,1.75
                 ,2
                 ,2.1
                 ,2.2
                 ,2.5
                 ,2.8
                 ,3.0
                 ,3.2
                 ,3.3
                 ,3.5
                 ,4
                 ,4.2
                 ,4.5
                 ,5
                 ,6
                 ,7
                 ,8
                 ,9
                 ,12
                 ,14
                 ,17.5
                 ,28
                ,56]
    if x in valid_weights:
        return x
    elif (x>3.37 and x<3.58):
        return 3.5
    elif (x>3.2 and x<=3.37):
        return 3.3
    else:
        valid_weights.append(x)
        #by default, sorts ascending
        valid_weights.sort()
        if valid_weights[-1]==x or valid_weights[0]==x:
            return x
        pos = valid_weights.index(x)
        #returns the closer weigth available, below
        if abs(x - valid_weights[pos-1])<1:
            return valid_weights[pos-1]
        return x
    
def get_fuzzy_mismatches(quality,catalog,brand):
    query = quality[quality['brand']==brand]
    df1=catalog[catalog['brand']==brand]

    df2=query[query['in_catalog']!=True][['brand','flavor','product_slug']]

    l=[]
    for v1 in df1['flavor']:
        for v2,idx in zip(df2['flavor'],df2.index):
            ratio = fuzz.ratio(v1,v2)
            if ratio>50:
                ps=df2.loc[idx]['product_slug']
                l.append([v2,v1,ratio,ps])
    d=pd.DataFrame(l,columns=['pistil','catalog','ratio','product_slug']).drop_duplicates()
    try:
        d['dict'] = d[['pistil','catalog']].apply(lambda x: f", '{x[0]}': '{x[1]}'",axis=1)
    except:
        pass
    d=d.sort_values(by='ratio',ascending=False)
    return d,df1,df2

def quality_control(df:pd.core.frame.DataFrame,operation:str):
    
    path = '/Users/mendes/Pistil/PistilData.Processing/pipeline/06_quality_control/tools/quality_control_utility_app/build/'
    qc = path+'qc'
    
    if operation=='delete':
        df[['id']].to_csv(path+'to_delete.csv',index=False)
        
    elif operation=='merge':
        df[['id','id_new']].to_csv(path+'to_merge.csv',index=False)
        
    elif operation=='update':
        df[['id','new']].to_csv(path+'to_update.csv',index=False)   
    else:
        print(f'the name: {operation}, is not valid. Use "delete, merge or update"')
        return None
    
    cmd = f'{qc} {operation} -f {path}to_{operation}.csv'
    #subprocess.call(cmd,cwd=path,shell=True)
    result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True, cwd=path)
    print(result.returncode, result.stdout, result.stderr)
    
def catch_end_number(s):
    import re
    for ss in s:
        pattern = '\d+$'
        result = re.findall(pattern,ss)
        if len(result)>0:
            return True
    return False

def generate_dates_tuples(start_date,end_date,step):

    dates = pd.date_range(start = start_date, end = end_date, freq =f'{step}d')

    dates_tuples = []
    for i in range(0,len(dates)-1):
        start_date = dates[i] + pd.DateOffset(1)
        end_date = dates[i+1]
        dates_tuples.append((start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d')))

    return dates_tuples