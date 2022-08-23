#!/usr/bin/env python

# python .\ejemplo1.py subcomando -u doberti

from do_artifactory import DoArtifactory
import logging, sys, pprint

def main():
    arti = DoArtifactory(config='config.yml')

    # Get a list with the releases versions of "project_A"
    list_releases = arti.list_releases("<REPOSITORY-NAME>")
    pprint.pprint(list_releases)

    # Download the release "0.0.1" from "project_A"
    arti.download_release(_repo="<REPOSITORY-NAME>", version="v0.0.0.1")

    # Download the latest release from "project_A"
    arti.download_release(_repo="<REPOSITORY-NAME>")

    # My current position in the directory tree
    current_path = arti.get_current_path()
    print(f'current_path:{current_path}')

    arti_list =  arti.search(_repo="<REPOSITORY-NAME>")
    for a in arti_list:
        print( a )


    print('*'*100)
    print("arti.search('*.zip'):")
    arti_list = arti.search('*.zip')
    for artifact in arti_list:
        print( artifact )

    #print('*'*100)
    #arti_list = arti.search2('*.zip')
    #for arti in arti_list:
    #    print( arti )

    print('*'*100)
    print("*** get_list_path ***")
    list_path = arti.get_list_path()
    for p in list_path:
        print(p)

    sys.exit(0)

if __name__ == "__main__":
    main()