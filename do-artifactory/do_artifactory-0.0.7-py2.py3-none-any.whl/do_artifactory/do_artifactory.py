# pip install python-gitlab
#import gitlab

# pip install dohq-artifactory
from artifactory import ArtifactoryPath

import os
import re
import yaml
import sys
import json
import pathlib
import traceback
import pprint

#########################################
#
# Maintainer: doberti
#
#########################################
# 
# // Set your Linux environment:
# setenv ARTIF_REPO <ARTIF_REPO>
# setenv ARTIF_USER <ARTIF_USER>
# setenv ARTIF_PASS <ARTIF_PASS>
#
#########################################


class DoArtifactory:
    
    def __init__(self, config='config.yml', f_debug=False):
        self.f_debug = f_debug
        with open(config) as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
            print(settings)
        self.current_path = '.'
        self.ARTIF_URL = os.getenv('ARTIF_URL', settings['ARTIF_URL'])
        self.ARTIF_REPO = os.getenv('ARTIF_REPO', settings['ARTIF_REPO'])
        self.ARTIF_USER = os.getenv('ARTIF_USER', settings['ARTIF_USER'])
        self.ARTIF_PASS = os.getenv('ARTIF_PASS', settings['ARTIF_PASS'])
        self.VERBOSE_LEVEL = os.getenv('VERBOSE_LEVEL', settings['VERBOSE_LEVEL'])
        
        print(self.VERBOSE_LEVEL)
        self.aql = ArtifactoryPath(self.ARTIF_URL, auth=(self.ARTIF_USER,self.ARTIF_PASS))

        ''' ADD USER AUTH!
        def user_auth(self, yml, verbose=False):
            input("username: ")
            input("password: ")                                
        '''
    def set_current_path(self, path):
        self.current_path = path
    
    def get_current_path(self):
        return self.current_path

    def search(self, _name=None, _repo=None, _type='any'):
        if not(_repo): _repo = self.ARTIF_REPO
        print( 'repo: {}'.format(_repo) )
        
        if _name:
            artifacts_list = self.aql.aql("items.find",{
                        "type": _type,
                        "repo": _repo,
                        "name": _name,
                        "path": self.current_path
                    }, ".include",
                ["type", "repo", "path", "name"]) 
        else:
            artifacts_list = self.aql.aql("items.find",{
                        "type": _type,
                        "repo": _repo,
                        "path": self.current_path
                    }, ".include",
                ["type", "repo", "path", "name"])
        return artifacts_list
    
    '''
    ejemplo: upload("/home/pepe/hello.txt", "carpetaA/carpetaB/")
    '''
    def upload(self, _path_source, _path_dest, _repo=None):
        if not(_repo): _repo = self.ARTIF_REPO
        if self.VERBOSE_LEVEL > 0:
            print( 'repo: {}'.format(_repo) )
        
        path = ArtifactoryPath( 
                    "{}{}/{}".format( self.ARTIF_URL, _repo, _path_dest )
                    ,auth=( self.ARTIF_USER, self.ARTIF_PASS ) 
        )
        
        try:
            path.mkdir()
        except Exception as e:
            pass
        
        return path.deploy_file(_path_source)
    
    ''' This download option requires an Artifactory license, so I created my own library
    def download(self, _path_source, _path_dest='download.zip', _repo=None):
        if not(_repo): _repo = self.ARTIF_REPO
        if self.VERBOSE_LEVEL > 0:
            print( 'repo: {}'.format(_repo) )
    
        path = ArtifactoryPath( 
                    "{}{}/{}".format( self.ARTIF_URL, _repo, _path_source )
                    ,auth=( self.ARTIF_USER, self.ARTIF_PASS ) 
        )
        
        #with path.archive(archive_type="zip", check_sum=False) as archive:
        #    with open(_path_dest, "wb") as out:
        #        out.write(archive.read())

        # download folder archive in chunks
        return path.archive().writeto(out=_path_dest, chunk_size=100 * 1024)
    '''

    def download(self, _path_source, _repo=None, _archiveType='zip'):
        if not(_repo): _repo = self.ARTIF_REPO
        if self.VERBOSE_LEVEL > 0:
            print( 'repo: {}'.format(_repo) )

        
        import urllib3
        import requests
        import shutil
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        myHeaders = urllib3.util.make_headers(basic_auth='{}:{}'.format(self.ARTIF_USER, self.ARTIF_PASS))
        url = "{}api/archive/download/{}/{}?archiveType={}".format( self.ARTIF_URL, _repo, _path_source, _archiveType )
        filename = 'download.'+_archiveType
        print(url)
        
        with open(filename, 'wb') as out:
            r = http.request('GET', url, headers=myHeaders, preload_content=False)
            shutil.copyfileobj(r, out)

    
    def set_path(self, _path):
        self.current_path = _path
        
    def set_repo(self, _repo):
        self.ARTIF_REPO = _repo

    def list_releases(self, _repo=None):
        if not(_repo): _repo = self.ARTIF_REPO
        _type='any'
        artifacts_list = self.aql.aql("items.find",{
                    "type": _type,
                    "repo": _repo,
                    "path": 'release'
                }, ".include",
            ["type", "repo", "path", "name", "modified"],
            ".sort",
            {"$desc": ["modified"]},
            )
        list_names = []
        for arti in artifacts_list:
            list_names.append(arti['name'])
        
        return list_names


    def download_file(self, _repo=None, _path=None, _name=None):
        
        if not(_repo): _repo = self.ARTIF_REPO
        if _path is None:
            print('Error: You must set a path to the file')
        if _name is None:
            print('Error: You must set a file name')
        else:
            # Download an specific release
            _type = 'any'
            artifacts_list = self.aql.aql("items.find",{
                        "type": _type,
                        "repo": _repo,
                        #"depth":'2',
                        "name":{"$match":f'{_name}'},
                        "path":{"$match":f'{_path}'},
                    }, ".include",
                ["type", "repo", "path", "name", "modified"],
                ".sort",
                {"$desc": ["modified"]},
                )

            if self.VERBOSE_LEVEL > 0:
                print( f'artifacts_list: {artifacts_list}' )
            
            for arti in artifacts_list:
                target_path = f'{self.ARTIF_URL}/{_repo}/{_path}'
                target_path = target_path.replace('//','/')
                target_path = target_path.replace('http:/','http://')
                target_path = target_path.replace('https:/','https://')
                if self.f_debug: print( f'target_path:{target_path}' )
                aux_aql = ArtifactoryPath(target_path, auth=(self.ARTIF_USER,self.ARTIF_PASS))
                with aux_aql.open() as fd, open(_path, "wb") as out:
                    out.write(fd.read())
                break

    def download_release(self, _repo=None, version=None):
        
        if not(_repo): _repo = self.ARTIF_REPO
        if version is None:
            # Download latest release
            list_releases = self.list_releases(_repo)
            version = list_releases[0]
            _type = 'any'
            artifacts_list = self.aql.aql("items.find",{
                        "type": _type,
                        "repo": _repo,
                        #"depth":'2',
                        #"name":{"$match":'*.zip'},
                        "path":{"$match":f'release/{version}'},
                    }, ".include",
                ["type", "repo", "path", "name", "modified"],
                ".sort",
                {"$desc": ["modified"]},
                )

            for arti in artifacts_list:
                target_path = f'{self.ARTIF_URL}/{_repo}/{arti["path"]}/{arti["name"]}'
                target_path = target_path.replace('//','/')
                target_path = target_path.replace('http:/','http://')
                target_path = target_path.replace('https:/','https://')
                if self.f_debug: print( f'target_path:{target_path}' )
                aux_aql = ArtifactoryPath(target_path, auth=(self.ARTIF_USER,self.ARTIF_PASS))
                with aux_aql.open() as fd, open(arti["name"], "wb") as out:
                    out.write(fd.read())
                break
        else:
            # Download an specific release
            list_releases = self.list_releases(_repo)
            if version in list_releases:
                _type = 'any'
                artifacts_list = self.aql.aql("items.find",{
                            "type": _type,
                            "repo": _repo,
                            #"depth":'2',
                            #"name":{"$match":'*.zip'},
                            "path":{"$match":f'release/{version}'},
                        }, ".include",
                    ["type", "repo", "path", "name", "modified"],
                    ".sort",
                    {"$desc": ["modified"]},
                    )

                for arti in artifacts_list:
                    target_path = f'{self.ARTIF_URL}/{_repo}/{arti["path"]}/{arti["name"]}'
                    target_path = target_path.replace('//','/')
                    target_path = target_path.replace('http:/','http://')
                    target_path = target_path.replace('https:/','https://')
                    if self.f_debug: print( f'target_path:{target_path}' )
                    aux_aql = ArtifactoryPath(target_path, auth=(self.ARTIF_USER,self.ARTIF_PASS))
                    with aux_aql.open() as fd, open(arti["name"], "wb") as out:
                        out.write(fd.read())
                    break
            else:
                print(f"Error, the release {version} is not in the current project releases list:")
                pprint.pprint( self.list_releases(_repo, _repo) )
                sys.exit(1)
        

    def search2(self, _filename, _repo=None, _type='file'):
        if not(_repo): _repo = self.ARTIF_REPO
        aqlargs = [
            "items.find",
            {
                "$and": [
                    {"repo": _repo},
                    {"type": _type},
                    {"path":"{}".format(_filename)},
                    {"created": {"$gt": "2019-07-10T19:20:30.45+01:00"}},
                ]
            },
            ".include",
            ["repo", "path", "name"],
            ".sort",
            {"$asc": ["repo", "path", "name"]},
        ]

        # items.find(
        #     {
        #         "$or": [{"repo": "docker-prod"}],
        #         "type": "file",
        #         "created": {"$gt": "2019-07-10T19:20:30.45+01:00"},
        #     }
        # ).include("repo", "path", "name",).sort({"$asc": ["repo", "path", "name"]})

        artifacts_list = self.aql.aql("items.find",aqlargs)
        return artifacts_list

    # ????????
    def get_list_path(self, _repo=None, _folder=''):
        if not(_repo): _repo = self.ARTIF_REPO
        #print(_repo)
        if _folder == '':
            _folder = '/' + _folder
        listpath = ArtifactoryPath( 
                    self.ARTIF_URL + _repo + _folder
                    ,auth=( self.ARTIF_USER, self.ARTIF_PASS ) 
        )
        return listpath


if __name__ == "__main__":
    
    arti = DoArtifactory()

    print('*'*100)
    arti_list = arti.search('*.zip')
    
    for arti in arti_list:
        print( arti )

    #print('*'*100)
    #arti_list = arti.search2('*.zip')
    #for arti in arti_list:
    #    print( arti )

    print('*'*100)
    list_path = arti.get_list_path()
    for p in list_path:
        print(p)
    
    sys.exit(0)




