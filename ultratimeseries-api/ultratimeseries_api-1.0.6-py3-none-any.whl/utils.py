def validate(request,endpoint):

    print(endpoint+" "+"returned a status code of "+str(request.status_code))

    if(request.status_code == 200):
        return True
    else:
        return False

def actorRequestBody(key):
    return { "key" : key }

def actorGetBody(key):
    return "?key="+key

def specificActionBody(subject,action):
    return {
        "subject" : subject,
        "action" : action
    }

def messageCreateBody(subject,action,measure,value,date=""):
    
    return {
        "subject" : subject,
        "action" : action,
        "measure" : measure,
        "value" : value,
        "date" : date
    }

def messageQueryGroupBody(subject,action,aggregator,start=None,end=None,measure=None):
    queryString = "?subject="+subject+"&action="+action

    if(start != None):
        queryString += "&start="+start
    if(end != None):
        queryString += "&end="+end
    if(measure != None):
        queryString += "&dimension="+str(measure["dimension"])+"&unit="+str(measure["unit"])
    
    queryString += "&aggregator="+str(aggregator)

    return queryString

def messageQueryBody(subject,action,start=None,end=None,measure=None):

    queryString = "?subject="+subject+"&action="+action

    if(start != None):
        queryString += "&start="+start
    if(end != None):
        queryString += "&end="+end
    if(measure != None):
        queryString += "&dimension="+str(measure["dimension"])+"&unit="+str(measure["unit"])

    return queryString

def roleProperty(name,type):
    return {
        "name":name,
        "type":type
    }

def rolePropertySetValue(name,value):
    return {
        name: value
    }

def roleBody(role, properties):
    body = {
        "role" : role,
    }

    body["properties"] = []

    for i in properties:
        body['properties'].append(i)

    return body

def roleQueryBody(role):
    return "?role="+role

def roleAddActorBody(role,actor,properties):

    body = {
        "role" : role,
        "actor" : actor
    }

    body["properties"] = []

    for i in properties:
        body['properties'].append(i)

    return body

def alarmsCreateBody(subject,action,measure,limit,snooze,callback):
    return {
        "subject" : subject,
        "action" : action,
        "measure" : measure,
        "limit" : limit,
        "snooze" : snooze,
        "callback" : callback
    }

def alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl):
    return {
        "subject" : subject,
        "action" : action,
        "measure" : measure,
        "limit" : limit,
        "snooze" : snooze,
        "callback" : callback,
        "ttl":ttl

    }