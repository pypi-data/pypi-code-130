import urllib.request
import urllib.parse
import sys, os
import argparse
import getpass
from configparser import ConfigParser
import zipfile
import progressbar
import requests
import time
import random
from pkg_resources import get_distribution, DistributionNotFound
from plexapi.myplex import MyPlexAccount
from pyputio.scan import update, notify, plexUpdate, readPlexCollections
from pyputio.plex import plexAuth

class DlProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
    	if os.environ.get("PUTIO_OUTPUT_MODE") == "silent" or os.environ.get("PUTIO_OUTPUT_MODE") == "json":
    		self.pbar = None
    	else:
	        if not self.pbar:
	            self.pbar=progressbar.ProgressBar(maxval=total_size)
	            self.pbar.start()

	        downloaded = block_num * block_size
	        if downloaded < total_size:
	            self.pbar.update(downloaded)
	        else:
	            self.pbar.finish()

def versionInfo():
    dist = get_distribution('pyputio')
    return "pyputio %s" % (dist.version)

def readSubpaths(library_path):
	paths = []
	for root, dirs, files in os.walk(library_path):
		for dir in dirs:
			if dir.startswith("."):
				continue
			else:
				paths.append(dir)
		break
	return paths

def current_time():
	current = time.time()
	return current

def readCredentials():
	if os.environ.get('PUTIO_USER') is None:
		PUTIO_USER = input("Enter your Put.io Username: ")
	else:
		PUTIO_USER = os.environ['PUTIO_USER'] 
			
	if os.environ.get('PUTIO_PASS') is None:
		PUTIO_PASS = urllib.parse.quote(getpass.getpass(prompt="Enter your Put.io Password: "))
	else:
		PUTIO_PASS = urllib.parse.quote(os.environ['PUTIO_PASS'])

	if os.environ.get('PUTIO_LIBRARY_PATH') is None:
		PUTIO_LIBRARY_PATH = input("Enter the Plex Library path: ")
	else:
		PUTIO_LIBRARY_PATH = os.environ['PUTIO_LIBRARY_PATH']

	if os.environ.get('PUTIO_LIBRARY_SUBPATH') is None:
		subpaths = readSubpaths(PUTIO_LIBRARY_PATH)
		if os.environ.get("PUTIO_PLEX_UPDATE") is not None:
			collections = readPlexCollections()
			print("You have PLEX connected to the following Libraries:\n")
			for c in collections:
				print(c)
			print("select the local subpath below for the appropriate Plex library above.\n")
		PUTIO_LIBRARY_SUBPATH = input("Enter the subdirectory %s to download and unpack to: " % (subpaths))
	else:
		PUTIO_LIBRARY_SUBPATH = os.environ['PUTIO_LIBRARY_SUBPATH']

	authentication = {}
	authentication['username'] = PUTIO_USER
	authentication['password'] = PUTIO_PASS
	authentication['library_path'] = PUTIO_LIBRARY_PATH
	authentication['library_subpath'] = PUTIO_LIBRARY_SUBPATH
	return authentication

def readConfig():
	parser = ConfigParser()
	parser.read(os.environ["PUTIO_CONFIG_PATH"])
	PUTIO_USER = parser.get('putio_config', 'username')
	PUTIO_PASS = urllib.parse.quote(parser.get('putio_config', 'password'))
	if parser.has_option('putio_config', 'library_path') is False:
		PUTIO_LIBRARY_PATH = input("Enter the Plex Library root directory (/mnt/Plex) : ")
	else:
		PUTIO_LIBRARY_PATH = parser.get('putio_config', 'library_path')
	if parser.has_option('putio_config', 'library_subpath') is False:
		subpaths = readSubpaths(PUTIO_LIBRARY_PATH)
		if os.environ.get("PUTIO_PLEX_UPDATE") is not None:
			collections = readPlexCollections()
			print("You have PLEX connected to the following Libraries:\n")
			for c in collections:
				print(c)
			print("select the local subpath below for the appropriate Plex library above.\n")
		PUTIO_LIBRARY_SUBPATH = input("Enter the subdirectory %s to download and unpack to: " % (subpaths))
	else:
		PUTIO_LIBRARY_SUBPATH = parser.get('putio_config', 'library_subpath')
	authentication = {}
	authentication['username'] = PUTIO_USER
	authentication['password'] = PUTIO_PASS
	authentication['library_path'] = PUTIO_LIBRARY_PATH
	authentication['library_subpath'] = PUTIO_LIBRARY_SUBPATH
	return authentication

def credentialResponse(credentials):
	authentication = {}
	authentication['username'] = credentials['username']
	authentication['password'] = credentials['password']
	authentication['library_path'] = credentials['library_path']
	authentication['library_subpath'] = credentials['library_subpath']
	return authentication

def credentials():
	if os.environ.get('PUTIO_CONFIG_PATH') is None:
		credentials = readCredentials()
		return credentialResponse(credentials)
	else:
		credentials = readConfig()
		return credentialResponse(credentials)

def dlUrl(credentials,url):
	url_path = url.split("https://")[-1]
	request = {}
	request['raw_url'] = url
	request['end_url'] = url_path.split()
	request['file_name'] = url.split("https://")[-1].split("put.io/zipstream")[1].split("?")[0]
	request['end_path'] = "%s/%s%s" % (credentials['library_path'], credentials['library_subpath'], request['file_name'])
	request['new_url'] = "https://%s:%s@%s" % (credentials['username'], credentials['password'], url_path)
	return request

def do_download(dLurl,credentials):
	password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
	top_level_url = dLurl['raw_url']
	password_mgr.add_password(None, top_level_url, credentials['username'], credentials['password'])
	handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
	opener = urllib.request.build_opener(handler)
	start_time = current_time()
	download_path = urllib.request.urlretrieve(dLurl['raw_url'], "%s/%s%s" % (credentials['library_path'], credentials['library_subpath'], dLurl['file_name']), DlProgressBar())
	end_time = current_time()
	report = {}
	if os.environ.get('PUTIO_REPORT_TIME') is not None:
		timed = end_time - start_time, " seconds."
		report['download_time'] = "%s seconds." % (str(round(timed[0], 2)))
	report['full_path'] = dLurl['end_path']
	report['library_extract_path'] = "%s/%s" % (credentials['library_path'], credentials['library_subpath'])
	report['url'] = dLurl['end_url']
	report['diag'] = download_path
	return report

def manual_do_download(dLurl,credentials):
	print("Downloading...")
	start_time = current_time()
	download_path = os.system("wget --user '%s' --password '%s' '%s' -O %s" % (credentials['username'], credentials['password'], dLurl['raw_url'], dLurl['end_path']))
	end_time = current_time()
	report = {}
	if os.environ.get('PUTIO_REPORT_TIME') is not None:
		timed = end_time - start_time, " seconds."
		report['download_time'] = "%s seconds." % (str(round(timed[0], 2)))
	report['full_path'] = dLurl['end_path']
	report['library_extract_path'] = "%s/%s" % (credentials['library_path'], credentials['library_subpath'])
	report['url'] = dLurl['end_url']
	report['diag'] = download_path
	return report

def download(url):
	creds = credentials()
	if os.environ.get("PUTIO_DIR_CREATE") is not None:
		dl_dir = "%s/%s" % (creds['library_path'], creds['library_subpath'])
		if not os.path.exists(dl_dir):
			os.makedirs(dl_dir)
	# url = sys.argv[1]
	if "put.io" in url:
		dl_url = dlUrl(creds,url)
	else:
		return "Bad URL"
		exit(1)
	if os.environ.get('PUTIO_MANUAL_DL') is not None:
		downloader = manual_do_download(dl_url,creds)
	else:
		downloader = do_download(dl_url,creds)
	return downloader

def extract(downloader):
	path_to_zip_file = downloader['full_path']
	directory_to_extract_to = downloader['library_extract_path']
	report = {}
	with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
		start_time = current_time()
		if os.environ.get("PUTIO_OUTPUT_MODE") == "silent" or os.environ.get("PUTIO_OUTPUT_MODE") == "progress" or os.environ.get("PUTIO_OUTPUT_MODE") == "json":
			pass
		else:
			print("Extracting %s...\n" % (path_to_zip_file))
		zip_ref.extractall(directory_to_extract_to)
		end_time = current_time()
		if os.environ.get('PUTIO_REPORT_TIME') is not None:
			timed = end_time - start_time, " seconds."
			report['extract_time'] = "%s seconds." % (str(round(timed[0], 2)))

	if os.environ.get("PUTIO_CLEAN") is not None:
		clean(path_to_zip_file)
	if "download_time" in downloader:
		if os.environ['PUTIO_REPORT_TIME'] is not None:
                        report['download_time'] = downloader['download_time']
	report['archive'] = path_to_zip_file
	report['unpacked_to'] = downloader['library_extract_path']
	if os.environ.get('PUTIO_NOTIFY') is not None:
		if os.environ.get('PUSHOVER_USER') is None and os.environ.get('PUSHOVER_TOKEN') is None:
			print("[WARN] Ensure PUSHOVER_TOKEN and PUSHOVER_USER are set in environment.")
		else:
			notify("%s: Extracting..." % (downloader['full_path']))
	return report

def manual_extract(downloader):
	path_to_zip_file = downloader['full_path']
	directory_to_extract_to = downloader['library_extract_path']
	report = {}
	start_time = current_time()
	extract = os.system("cd %s && unzip %s" % (directory_to_extract_to, path_to_zip_file))
	end_time = current_time()
	if os.environ.get("PUTIO_OUTPUT_MODE") == "silent" or os.environ.get("PUTIO_OUTPUT_MODE") == "progress":
		pass
	else:
		print(extract)
	if os.environ.get('PUTIO_REPORT_TIME') is not None:
		timed = end_time - start_time, " seconds."
		report['download_time'] = "%s seconds." % (str(round(timed[0], 2)))
	if os.environ.get("PUTIO_CLEAN") is not None:
		clean(path_to_zip_file)
	if "download_time" in downloader:
		if os.environ['PUTIO_REPORT_TIME'] is not None:
			report['download_time'] = downloader['download_time']
	report['archive'] = path_to_zip_file
	report['unpacked_to'] = downloader['library_extract_path']
	return report

def clean(path):
	op = os.remove(path)
	return op 

def env_handle(args,mode):
	if mode == "set":
		if args.username is not None:
			os.environ['PUTIO_USER'] = args.username
		if args.password is not None:
			os.environ['PUTIO_PASS'] = args.password
		if args.library_path is not None:
			os.environ['PUTIO_LIBRARY_PATH'] = args.library_path
		if args.library_subpath is not None:
			os.environ['PUTIO_LIBRARY_SUBPATH'] = args.library_subpath
		if args.config is not None:
			os.environ['PUTIO_CONFIG_PATH'] = args.config
		if args.notify is not None:
			os.environ['PUTIO_NOTIFY'] = args.notify
		if args.notify is not None:
			os.environ['PUTIO_OUTPUT_MODE'] = args.output
	else:
		if args.username is not None:
			os.environ['PUTIO_USER'] = ""
		if args.password is not None:
			os.environ['PUTIO_PASS'] = ""
		if args.library_path is not None:
			os.environ['PUTIO_LIBRARY_PATH'] = ""
		if args.library_subpath is not None:
			os.environ['PUTIO_LIBRARY_SUBPATH'] = ""
		if args.config is not None:
			os.environ['PUTIO_CONFIG_PATH'] = ""
		if args.notify is not None:
			os.environ['PUTIO_NOTIFY'] = ""
		if args.output is not None:
			os.environ['PUTIO_OUTPUT_MODE'] = ""
	return args


def main():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-U','--username', 
    help="Put.io Username")
	parser.add_argument('-P','--password',  
    help="Put.io Password")
	parser.add_argument('-p','--library_path', 
    help="Target Root Directory (i.e. /mnt/Plex)")
	parser.add_argument('-s','--library_subpath',  
    help="Target Root Directory (i.e. TV or Music)")
	parser.add_argument('-c','--config', 
    help="Put.io configuration file path")
	parser.add_argument('-u','--url', 
    help="Put.io Zip URL")
	parser.add_argument('-n','--notify',
	help="Notification via Pushover (Assumes PUSHOVER_USER and PUSHOVER_TOKEN in env)")
	parser.add_argument('-o', '--output',
	help="Output format (default, json, silent).")
	parser.add_argument('-v', '--version', 
    help="pyputio version", action='store_true')

	args = parser.parse_args()

	if args.url is not None:
		env_handle(args,"set")
		
		downloader = download(args.url)
		if os.environ.get('PUTIO_MANUAL') is not None:
			ex = manual_extract(downloader)
		else:
			ex = extract(downloader)
		env_handle(args,"unset")
	
		if os.environ.get("PUTIO_OUTPUT_MODE") == "silent":
			response = ""
		elif os.environ.get("PUTIO_OUTPUT_MODE") == "progress":
			response = ""
		else:
			response = ex

		if os.environ.get("PUTIO_PLEX_UPDATE") is not None:
			if os.environ.get("PLEX_USERNAME") is not None and os.environ.get("PLEX_PASSWORD") is not None:
				if os.environ.get("PLEX_SERVER_NAME") is not None:
					plexUpdate()

		return response
	else:
		return versionInfo()

# if __name__ == "__main__":
#     exit(main())
