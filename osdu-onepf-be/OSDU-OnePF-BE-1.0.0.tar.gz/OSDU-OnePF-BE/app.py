from flask import Flask, request, jsonify,render_template,redirect,flash,session,send_from_directory
from flask_cors import CORS, cross_origin
from blueprints.main.views import main
from blueprints.dbservice_handler.views import dbservice
from blueprints.searchservice_handler.views import searchservice
from blueprints.edsservice_handler.views import edsservice
from blueprints.seismicdata_handler.views import seismicservice
from blueprints.validation_handler.views import validationservice
from blueprints.ddmsservice_handler.views import wellboreddmsservice
from blueprints.ingestion_handler.views import ingestionservice
from blueprints.file_handler.views import filehandlerservice
from blueprints.schemamapping_handler.views import schemamappingservice

#ignore comment out things
# dbupdate = DBUpdation()
# dbinsertion = DBinsertion()
# dbdeletion=DBDeletion()

#importing the os module

#
#
#
#
# #Read required paths from config1.json file
# with open(os.path.join("config1.json"),"r") as f:
#     path=json.load(f)
# with open(os.path.join(root,path['global_client']),"r") as f:
#    global_client =json.load(f)
# with open(os.path.join(root,path['global_config']), "r") as f:
#         global_config = json.load(f)
#
# #File upload folder for any file uploaded
# UPLOAD_FOLDER =os.path.join(root,path['uploadFolder'])
# ALLOWED_EXTENSIONS = {'las','zip'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# config = configparser.RawConfigParser()
# config.read(os.path.join(root,path['dataloadConfig']))
#
#
#
#
#
# @app.route("/topicmodelingnew", methods=['GET','POST'])
#
# def topicmodelingnew():
#     f = request.files['file']
#     data = pd.read_excel(f)
#     data['input_data'] = data['Title']
#     prdsol=CareSimiQuery()
#     list_data = []
#     for i in data['input_data']:
#         osdu_list=prdsol.getsimilarity(i)
#         list_data.append(osdu_list)
#     dataframe = pd.DataFrame()
#     dataframe['Customer Input'] = data['Input_Schema']
#     dataframe['Customer Input_Title'] = data['Title']
#     df = pd.DataFrame(list_data, columns =['Result1', 'Result2', 'Result3','Result4','Result5'], dtype = float)
#     dataframe['Result1']=df['Result1']
#     dataframe['Result2']=df['Result2']
#     dataframe['Result3']=df['Result3']
#     dataframe['Result4']=df['Result4']
#     dataframe['Result5']=df['Result5']
#     myData = dataframe.values
#     result=dataframe.to_json(orient = 'values')
#     return result
#
# #validates number of records by applying rules
# @app.route('/saveschemanew', methods=['GET', 'POST'])
# def saveschemanew():
#     data = request.json
#     dbinsertion.InsertionMany("mongodb://localhost:27017/","osdu_db","Mapped_Schema",data)
#     return {'status':'ok'}
#
# #validates number of records by applying rules
# @app.route('/validatenew', methods=['GET', 'POST'])
# def validatenew():
#     data = pd.read_csv(os.path.join(root,path['meta']))
#     jsonreq = request.json
#     ind = jsonreq
#     for index, row in data.iterrows():
#         if index not in ind:
#             data.drop(index, inplace=True)
#     data.to_csv(os.path.join(root,path['finalInp']),index=False)
#     valdation = Validations()
#     val = valdation.result()
#     data = val.to_json(orient='values')
#     return data
#
# @app.route('/filegenerationnew', methods=['GET', 'POST'])
# def filegenerationnew():
#     data=pd.read_csv(os.path.join(root,path['method2Schema1']))
#     return data.to_json(orient="values")
#
# @app.route("/uploadfilesnew", methods=['GET', 'POST'])
# def uploadfilesnew():
#     las_ex = Las_Extraction()
#     section_json_list = 0
#     upload_file = request.files['file']
#     session["uploadfile"] = upload_file.filename
#     if upload_file.filename.split('.')[-1] == "las":
#         las_object, section_list = las_ex.extract_sections(upload_file.read().decode("latin-1"))
#         session["file"] = las_object # las file object
#         session["sec_list"] = section_list # Las dynamic sssions
#         session["ext"] = config_extractor.las_extension # Las extension
#     else:
#         session["file"] = os.path.join(root,path['segyfile'])#upload_file
#         session["sec_list"] = config_extractor.Segy_headers # Segy headers are static and keep into the config file as list.
#         session["ext"] = config_extractor.segy_extension # SEGY file extension
#         section_list = config_extractor.Segy_headers
#     return jsonify(section_list)
#
# #segy, las files
# @app.route("/sectionheadersnew", methods=['GET', 'POST'])
# def sectionheadersnew():
#     las_ex = Las_Extraction()
#     segy_ex = Segy_Extraction()
#     jsonre = request.json
#     section = request.form['symbol']
#     # Get the session variable created previously
#     file_object = request.files['file']
#     file_extension = config_extractor.las_extension
#     if file_object.filename.split('.')[-1] == "las":
#         las_object, section_list = las_ex.extract_sections(file_object.read().decode("latin-1"))
#         final_dataframe = las_ex.extract_LAS_data(las_object, section, section_list)  # Prepare output dataset for the selected file section
#     else:
#         final_dataframe = segy_ex.extract_data(os.path.join(root,path['segyfile']), section)
#     return final_dataframe.to_json(orient='split')
#
#   #ingestion
# @app.route('/manifestnew')
# def manifestnew():
#     os.chdir(os.path.join(root,path['ingestionPath']))
#     subprocess.call(os.path.join(root,path['run'] ) % (str(global_config['data-partition-id']),),shell=True)
#     os.chdir(root)
#     responseData = '{"status":"success"}'
#     return responseData
#
# @app.route('/dataingestionnew')
# def dataingestionnew():
#     os.chdir(os.path.join(root,path['ingestionPath']))
#     subprocess.call([os.path.join(root,path['load'])],shell=True)
#     os.chdir(root)
#     responseData = '{"status":"success"}'
#     return responseData
#
# @app.route('/dataverification')
# def dataverification():
#     time.sleep(5)
#     responseData = '{"status":"success"}'
#     return responseData
#
# #ddms service
# @app.route('/ddmsSearchServicenew', methods=['GET', 'POST'])
# def ddmsSearchServicenew():
#     if request.method == 'POST':
#         jsonreq = request.json
#         wellbore_name=jsonreq["search"]
#         subprocess.call(os.path.join(root,path['ddmsSearch']) % (str(wellbore_name),),shell=True)
#         with open(os.path.join(root,path['output_search']), 'r') as myfile:
#             result=myfile.read()
#             result="{"+'"'+result+"}"
#             result= result.replace('Matching Wellbore ids:','Matching Wellbore ids":')
#         return result
# @app.route('/ddmsListnew', methods=['GET', 'POST'])
# def ddmsListnew():
#     if request.method == 'POST':
#         jsonreq = request.json
#         wellbore_id=jsonreq["search"]
#         pathddms=os.path.join(root,path['ddmsList'])
#         subprocess.call(os.path.join(root,path['ddmsList']) % (str(wellbore_id),), shell=True)
#         with open(os.path.join(root,path['output_list']), 'r') as myfile:
#             data = myfile.read()
#         value = json.loads(data)
#         # return jsonify(data)
#         return value
# #ddms
# @app.route('/upload_filenew', methods=['GET', 'POST'])
# def upload_filenew():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             extension= pathlib.Path(file.filename).suffix
#             if extension==".zip":
#                 with zipfile.ZipFile(file, 'r') as zip_ref:
#                     zip_ref.extractall(os.path.join(root,path['uploadFolder']))
#                 os.chdir(os.path.join(root,path['uploadFolder']))
#                 all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
#                 latest_subdir = max(all_subdirs, key=os.path.getmtime)
#                 path=os.path.join(root,path['uploadFolder'])+latest_subdir
#                 os.chdir(root)
#             else:
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#                 path=os.path.join(root,path['uploadFolder'])+file.filename
#             subprocess.Popen(os.path.join(root,path['ddms']) % (str(path),),shell=True)
#             return '{"message":"Records added successfully"}'
#
# #validation
# @app.route('/datavalidatenew')
# def datavalidationnew():
#     data = pd.read_csv(os.path.join(root,path['meta']))
#     myData=data.to_json(orient = 'values')
#     return myData;
#
# #validation
# @app.route('/deletenewrule', methods=['GET', 'POST'])
# def deletenewrule():
#     data = pd.read_csv(os.path.join(root,path['meta']))
#     ind=request.json
#     finalInd=ind
#     data.drop(data.index[[finalInd]], inplace=True)
#     data.to_csv(os.path.join(root,path['meta']),index=False)
#     data1 = pd.read_csv(os.path.join(root,path['meta']))
#     result=data.to_json(orient = 'values')
#     return result
# #validation
# @app.route('/addnew', methods=['GET', 'POST'])
# def addnewrule():
#         final_df = pd.DataFrame(columns=['Rule', 'InputFileQuery', 'OutputFileQuery'])
#         jsonreq = request.json
#         Rule = jsonreq["rule"]
#         csv_query = jsonreq["IQuery"]
#         osdu_query = jsonreq["OQuery"]
#         final_df['Rule'] = [Rule]
#         final_df['InputFileQuery'] = [csv_query]
#         final_df['OutputFileQuery'] = [osdu_query]
#         final_df.to_csv(os.path.join(root,path['meta']), mode='a', index=False, header=False)
#         data = pd.read_csv(os.path.join(root,path['meta']))
#         result=data.to_json(orient = 'values')
#         return result
#
# #servicehandler
# @app.route('/servicesnew')
# def servicesnew():
#     session.clear()
#     session['response'] = request.args.get('type')
#     roles=session['response']
#     final_value=config.get(session['response'].upper(), "payload")
#     final_value=eval(final_value)
#     session['payload_value'] = final_value
#     url=config.get(session['response'].upper(), "url")
#     if '{}' in url:
#         enable=True
#         return final_value
#     return final_value
# #service handler
# @app.route('/searchservicesnew1')
# def searchservicesnew1():
#     para = request.form.get('parameters','')
#     path_variables = request.args.get('popup')
#     search_query = request.args.get('search')
#     typeApi=request.args.get('type')
#     if search_query:
#         search_query = eval(search_query)
#     session['payload_value'] = search_query
#     if "formbutton" in request.values:
#         if request.args.get('popup'):
#             session['path_variables']=request.args.get('popup')
#         enviornment_variable = 'aws'
#
#         search_url, method = config.get(typeApi.upper(), "url"), config.get(typeApi.upper(),"method")
#         api = Api_Functions()
#         value = api.get_value(method, search_url, search_query, path_variables, para)
#         return json.dumps(value)
#     return ""
#
#
# # service handler
# @app.route('/searchservicesnew')
# def searchservicesnew():
#     para = request.form.get('parameters','')
#     path_variables = request.args.get('popup')
#     search_query = request.args.get('search')
#     typeApi=request.args.get('type')
#     if search_query:
#         search_query = eval(search_query)
#     session['payload_value'] = search_query
#     if "formbutton" in request.values:
#         if request.args.get('popup'):
#             session['path_variables']=request.args.get('popup')
#         #search_query = session['payload_value']
#         #session['payload_value'] = search_query
#         enviornment_variable = 'aws'
#
#         search_url, method = config.get(typeApi.upper(), "url"), config.get(typeApi.upper(),"method")
#         api = Api_Functions()
#         value = api.get_value(method, search_url, search_query, path_variables, para)
#         return json.dumps(value)
#         #return render_template("services.html", result=json.dumps(value))
#
#     return ""
#    # return render_template("services.html")
#
#
# #eds service
# @app.route('/eds_search' , methods=['GET', 'POST'])
# def eds_search():
#     if request.method == 'POST':
#         data_provider_name=request.json['data_provider_name']
#         data_type=request.json['data_type']
#         search_eds = SearchEDS()
#         result = search_eds.search_external_source(data_provider_name ,data_type)
#     return jsonify(result)
# #eds service
# @app.route('/register_eds_registry' , methods=['GET', 'POST'])
# def register_eds_registry():
#     if request.method == 'POST':
#         name=request.json['Name']
#         description=request.json['Description']
#         tokenurl=request.json['TokenUrl']
#         security_flow_type=request.json['security_flow_type']
#         osdu_implemntation=request.json['osdu_implemntation']
#         register_eds=RegisterEDS()
#         result= register_eds.source_registry_schema(name,description,security_flow_type,tokenurl,'False')
#         result = result[1]
#     return jsonify(result)
# #eds service
# @app.route('/register_eds_datajob' , methods=['GET', 'POST'])
# def register_eds_datajob():
#     if request.method == 'POST':
#         name=request.json['name']
#         #connectedsourcedatajobid=request.form['connectedsourcedatajobid']
#         connectedsourceregistryentryid=request.json['connectedsourceregistryentryid']
#         fetchkind=request.json['fetchkind']
#         filter= request.json['filter']
#         searchurl=request.json['searchurl']
#         scheduleUTC=request.json['scheduleUTC']
#         register_eds=RegisterEDS()
#         result= register_eds.source_datajob_schema(name,connectedsourceregistryentryid,fetchkind,filter,searchurl,scheduleUTC)
#         result = result[1]
#     return jsonify(result)
# """
# @app.route('/fetch_eds' , methods=['GET', 'POST'])
# def fetch_eds():
#     if request.method == 'POST':
#         name=request.json['name']
#         fetchkind=request.json['fetchkind']
#         filter= request.json['filter']
#         fetch_eds=FeatchEDS()
#         result= fetch_eds.search_external_source(name,fetchkind,filter)
#     return '{"status":"ingestion completed"}' """
#
# @app.route("/SeismicSubprojectnew", methods=['GET', 'POST'])
# def SeismicSubprojectnew():
#         jsonreq = request.json
#         tenant=jsonreq["tenant"]
#         subproject=jsonreq["subproject"]
#         mail=jsonreq["mail"]
#         legaltag=jsonreq["legal"]
#         os.chdir(os.path.join(root,path['seismic']))
#         subprocess.call(os.path.join(root,path['sddmsSubproject']) % (str(tenant),str(subproject),str(mail),str(legaltag),), shell=True)
#         os.chdir(os.path.join(root,path['rootFolder']))
#         with open(os.path.join(root,path['output_subproject']), 'r') as myfile:
#             data=myfile.read()
#             data= data.replace(">","")
#         #data = data.to_json(orient='values')
#         return {"response":data}
#         #return render_template('subproject.html',data=data)
# @app.route("/SeismicListnew", methods=['GET', 'POST'])
# def SeismicListnew():
#     jsonreq = request.json
#     path1=jsonreq["path"]
#     os.chdir(os.path.join(root,path['seismic']))
#     subprocess.call(os.path.join(root,path['sddmsList']) % (str(path1),), shell=True)
#     os.chdir(root)
#     with open(os.path.join(root,path['output_seislist']), 'r') as myfile:
#         data=myfile.read()
#     return {"response":data}
#     #return render_template('seisList.html',data=data)
# @app.route("/SeismicTenantnew", methods=['GET', 'POST'])
# def SeismicTenantnew():
#         esd=request.json['esd']
#         gcpid=request.json['gcpid']
#         acl=request.json['acl']
#         response=seismicDdms.tenant(esd,gcpid,acl)
#         # return jsonify(response)
#         return {"response":response}
#         #return render_template('tenant.html',data=response)
# @app.route("/SeismicLoadnew", methods=['GET', 'POST'])
# def SeismicLoadnew():
#     tenant = request.form['tenant']
#     subproject = request.form['subproject']
#     file_folder = request.form['file_folder']
#     files = request.files['file']
#     os.chdir(os.path.join(root,path['seismic']))
#     files.save(files.filename)
#     subprocess.call(os.path.join(root,path['sddmsLoad']) % (str(tenant), str(subproject), str(file_folder), str(files.filename),), shell=True)
#     #subprocess.Popen(['/home/osduuser/OSDUONEPLATFORM/sample.sh %s' % ( files.filename)], shell=True)
#     os.chdir(root)
#     with open(os.path.join(root,path['output_seisload']), 'r') as myfile:
#         data=myfile.read()
#     return {"response":data}
#     # return {"response":"ok"}
#
# #Global DB_configuration
# @app.route("/global_configFetchnew", methods=['GET', 'POST'])
# def global_configFetchnew():
#     global result
#     data = request.form['selectedTab']
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     mydb = myclient["osdu_db"]
#     mycol = mydb["Gobal_config"]
#     if (data=='GCP' or data=='IBM'):
#         result = '{"status":"NotAvailable"}'
#     else:
#         myquery = {'cloudPlatform':data}
#         mydoc = mycol.find(myquery)
#         for result in mydoc:
#             del result['_id']
#     return result
# @app.route("/global_configInsertnew", methods=['GET', 'POST'])
# def global_configInsertnew():
#     jsonre = request.json
#     tab = jsonre[0]
#     select_tab = tab['selectedTab']
#     newdata = jsonre[1]
#     myquery = {'cloudPlatform':select_tab}
#     insert_one = dbupdate.Update_one(global_client['clientname'],global_client['dbname'],global_client['collection'],myquery,newdata)
#     return {"status":"ok"}
# @app.route("/global_configUpdatenew", methods=['GET', 'POST'])
# def global_configUpdatenew():
#     jsonre = request.json
#     tab = jsonre[0]
#     select_tab = tab['selectedTab']
#     newdata = jsonre[1]
#     myquery = {'cloudPlatform':select_tab}
#     insert_one = dbupdate.Update_one(global_client['clientname'],global_client['dbname'],global_client['collection'],myquery,newdata)
#     return {"status":"ok"}
# @app.route("/global_configDeletenew", methods=['GET', 'POST'])
# def global_configDeletenew():
#     jsonre = request.json
#     tab = jsonre[0]
#     select_tab = tab['selectedTab']
#     newdata = jsonre[1]
#     myquery = {'cloudPlatform':select_tab}
#     delete_one = dbdeletion.Deletevalue("mongodb://localhost:27017/","osdu_db","Gobal_config",myquery,newdata)
#     return {"status":"ok"}
# @app.route("/dbSettingnew", methods=['GET', 'POST'])
# def dbSettingnew():
#     jsonre = request.json
#     json_object = json.dumps(jsonre)
#     with open(os.path.join(root,path['global_client']), "w") as outfile:
#         outfile.write(json_object)
#     return {'status':'ok'}
# @app.route("/setEnv", methods=['GET', 'POST'])
# def setEnv():
#     env = request.form['selectedEnv']
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     mydb = myclient["osdu_db"]
#     mycol = mydb["Gobal_config"]
#     myquery = {'cloudPlatform':env}
#     mydoc = mycol.find(myquery)
#     for result in mydoc:
#         del result['_id']
#     with open("global_config.json", "w") as outfile:
#         json.dump(result, outfile)
#     exec(open('dataini.py').read())
#     return {'status':'ok'}

# if __name__ == "__main__":
#     app.secret_key = 'super secret key'
#     app.config['SESSION_TYPE'] = 'filesystem'
#     app.config["SESSION_PERMANENT"] = False
#     Session(app)
#     app.run(host='0.0.0.0', port=5020)


#File upload folder for any file uploaded
# UPLOAD_FOLDER =os.path.join(root,path['uploadFolder'])
# ALLOWED_EXTENSIONS = {'las','zip'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#ignore comment out things

def create_app():
    # #Register a flask app
    app = Flask(__name__, static_url_path='')
    CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config["SESSION_PERMANENT"] = False

    # register blueprint
    # app.register_blueprint(main)
    app.register_blueprint(dbservice)
    app.register_blueprint(searchservice)
    app.register_blueprint(edsservice)
    app.register_blueprint(seismicservice)
    app.register_blueprint(validationservice)
    app.register_blueprint(wellboreddmsservice)
    app.register_blueprint(filehandlerservice)
    app.register_blueprint(schemamappingservice)
    app.register_blueprint(ingestionservice)
    return app

if __name__ == "__main__":
    create_app().run()