import requests as r

def getsvTableAll(access_token,subscription_key,rootUrl,activeOU,siteview,table,pagesize,cursor):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    url = F"{rootUrl}/{activeOU}/siteview/data/{table}?pagesize={pagesize}&cursor={cursor}"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getsvTableChanges(access_token,subscription_key,rootUrl,activeOU,siteview,table,pagesize,cursor,date):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    url = F"{rootUrl}/{activeOU}/siteview/data/changedrecords/{table}?pagesize={pagesize}&cursor={cursor}&startdateutc={date}"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL

def getsvTableSingleFilter(access_token,subscription_key,rootUrl,activeOU,siteview,table,pagesize,cursor,filterColumn,filterValue):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    url = F"{rootUrl}/{activeOU}/siteview/data/{table}?&{filterColumn}={filterValue}&pagesize={pagesize}&cursor={cursor}"
    IDWELL = r.get(url=url,headers=call_headers)
    return IDWELL


def svPostBatchJob(access_token,subscription_key,rootUrl,activeOU,siteview,table,body):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    body = body
    url = F"{rootUrl}/{activeOU}/siteview/data/{table}/batchjob"
    batchJobID = r.post(url=url,headers=call_headers,json=body)
    return batchJobID



def svGetBatchJob(access_token,subscription_key,rootUrl,activeOU,siteview,batchJobID):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    url = F"{rootUrl}/{activeOU}/siteview/data/batchjob/{batchJobID}"

    batch = r.get(url=url,headers=call_headers)
    return batch

def svReturnBatchStatus(access_token,subscription_key,url,siteview):
    call_headers = {
                "Content-Type":'application/json',
                "Authorization":"Bearer %s" %(access_token),
                "Ocp-Apim-Subscription-Key":subscription_key,
                "siteview":siteview
                }
    url = F"{url}"
    batch_status = r.get(url=url,headers=call_headers)
    return batch_status
