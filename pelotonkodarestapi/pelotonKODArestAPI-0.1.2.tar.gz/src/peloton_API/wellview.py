import requests as r
import json

def getwvTableAll(access_token,subscription_key,rootUrl,activeOU,wellview,table,pagesize,cursor):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}?pagesize={pagesize}&cursor={cursor}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getwvTableChanges(access_token,subscription_key,rootUrl,activeOU,wellview,table,pagesize,cursor,date):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/changedrecords/{table}?pagesize={pagesize}&cursor={cursor}&startdateutc={date}"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL


def getwvWellHeaderAPI(apiNum,access_token,subscription_key,rootUrl,activeOU,wellview):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/wvwellheader?$wellida=${apiNum}"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getwvTableSingleFilter(access_token,subscription_key,rootUrl,activeOU,wellview,table,pagesize,cursor,filterColumn,filterValue):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}?pagesize={pagesize}&cursor={cursor}&{filterColumn}={filterValue}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getwvTableThreeFilter(access_token,subscription_key,rootUrl,activeOU,wellview,table,pagesize,cursor,filterColumn,filterValue,sfilterColumn,sfilterValue,tfilterColumn,tfilterValue):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}?pagesize={pagesize}&cursor={cursor}&{filterColumn}={filterValue}&{sfilterColumn}={sfilterValue}&{tfilterColumn}={tfilterValue}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL


def putwvNotesByWellByJob(access_token,subscription_key,rootUrl,activeOU,wellview,idwell,idrec,notes):
    url = F"{rootUrl}/{activeOU}/wellview/data/wvJobReportCostGen/entityId/{idwell}/recordId/{idrec}/note"
    put_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    payload = json.dumps(notes)         
    updateNotes = r.put(url=url,headers=put_headers,data=payload)
    return updateNotes



def wvPostBatchJob(access_token,subscription_key,rootUrl,activeOU,wellview,table,body):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    body = body
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}/batchjob"
    batchJobID = r.post(url=url,headers=call_headers,json=body)
    return batchJobID



def wvGetBatchJob(access_token,subscription_key,rootUrl,activeOU,wellview,batchJobID):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/batchjob/{batchJobID}"

    batch = r.get(url=url,headers=call_headers)
    return batch

def wvReturnBatchStatus(access_token,subscription_key,url,wellview):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{url}"
    batch_status = r.get(url=url,headers=call_headers)
    return batch_status

def getwvTableByEntityID(access_token,subscription_key,rootUrl,activeOU,wellview,table,cursor,pagesize,entityId):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}/entityId/{entityId}?pagesize={pagesize}&cursor={cursor}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getwvTableByEntityID_singleFilter(access_token,subscription_key,rootUrl,activeOU,wellview,table,cursor,pagesize,entityId,filterColumn,filterValue):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}/entityId/{entityId}?${filterColumn}=${filterValue}&?pagesize={pagesize}&cursor={cursor}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getwvTableForParent(access_token,subscription_key,rootUrl,activeOU,wellview,table,pagesize,cursor,parentId):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}/parentId/{parentId}?pagesize={pagesize}&cursor={cursor}&includecalcs=true&unitset=us"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL


def putwvColumnByIDREC(access_token,subscription_key,rootUrl,activeOU,wellview,table,idwell,idrec,column,writeVal):
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}/entityId/{idwell}/recordId/{idrec}/{column}?$unitset=us"
    put_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    payload = json.dumps(writeVal)         
    updateColumn = r.put(url=url,headers=put_headers,data=payload)
    return updateColumn


def postwvRowByIDWELL(access_token,subscription_key,rootUrl,activeOU,wellview,table,writeVal):
    url = F"{rootUrl}/{activeOU}/wellview/data/{table}"
    post_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "wellview":wellview
                }
    payload = json.dumps(writeVal)         
    insertRow = r.post(url=url,headers=post_headers,data=payload)
    return insertRow
