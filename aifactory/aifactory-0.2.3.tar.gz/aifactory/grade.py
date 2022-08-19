import os
from sys import argv
import requests

api_url_test= "https://grade-bridge-test.aifactory.space"#"http://localhost:9123/grade"
api_url = "https://grade-bridge.aifactory.space"#"http://localhost:9123/grade"

def submit(key, submit_file_path):
  values = {"key": key}
  res = requests.post(api_url, files = {'file': open(submit_file_path,'rb', )}, data=values)  
  if res.status_code == 200 or res.status_code == 201: 
    print("success")
    return
  print(res.status_code)  
  print(res.text)

def submit_test(key, submit_file_path):
  values = {"key": key}
  res = requests.post(api_url_test, files = {'file': open(submit_file_path,'rb', )}, data=values)  
  if res.status_code == 200 or res.status_code == 201: 
    print("success")
    return
  print(res.status_code)  
  print(res.text)