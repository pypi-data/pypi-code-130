import requests, zipfile,sys,os,tarfile
zip_file_url = "https://www.s79.ir/tmp/test.tar.gz"


print("===================================")
print("====== Flask project manager ======")
print("===================================")
print("Initializing new flask project....")
print("Downloading requirements ....")

def main():
    r = requests.get(zip_file_url, stream=True)
    with open('tmp.tgz', 'wb') as file:
        file.write(r.raw.read())
    tar = tarfile.open("tmp.tgz")
    tar.extractall(path=os.getcwd())
    tar.close()
    os.remove('tmp.tgz')


if __name__ == '__main__':
    main()

if __name__ == 'sina_seifouri.__main__':
    main()
