def guessMetricByType(mainDict:dict, checkDict:dict):
   for i in checkDict:
      try:
         float(checkDict[i])
         mainDict[i] = 'count'
      except ValueError:
         mainDict[i] = 'string'
   return mainDict

##validation method - This is only for Output validation purpose
def validatePluginData(result):
     obj,mandatory ={'Errors':""},['heartbeat_required','plugin_version']
     value={'heartbeat_required':["true","false",True,False],'status':[0,1]}
     for field in mandatory:
        if field not in result:
            obj['Errors']=obj['Errors']+"# Mandatory field "+field+" is missing #"
     for field,val in value.items():
        if field in result and result[field] not in val:
            obj['Errors']=obj['Errors']+"# "+field+" can only be "+str(val)
     if 'plugin_version' in result and not isinstance(result['plugin_version'],int):
        obj['Errors']=obj['Errors']+"# Mandatory field plugin_version should be an integer #"
     RESERVED_KEYS='plugin_version|heartbeat_required|status|units|msg|onchange|display_name|AllAttributeChart'
     attributes_List=[]
     for key,value in result.items():
         if key not in RESERVED_KEYS:
            attributes_List.append(key)
     if len(attributes_List) == 0:
        obj['Errors']="# There should be atleast one \"Number\" type data metric present #"
     if obj['Errors'] !="":
        obj['Result']="**************Plugin output is not valid************"
     else:
        obj['Result']="**************Plugin output is valid**************"
        del obj['Errors']
     result['validation output']= obj