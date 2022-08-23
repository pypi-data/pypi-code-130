#!/usr/bin/env python

#from do_artifactory import DoArtifactory
import do_artifactory
import sys, pprint

def main():
    project = 'orion'
    ARTIF_REPO = f'cdsp-firmware-{project}-generic-preprod-dc5'
    #arti = DoArtifactory(config='specific_example.yml', f_debug=True)
    arti = do_artifactory.DoArtifactory(config='specific_example.yml', f_debug=True)


    # Get a list with the releases
    list_releases = arti.list_releases(ARTIF_REPO)
    pprint.pprint(list_releases)


    # Download the latest release 
    arti.download_release(_repo=ARTIF_REPO)

    # Download the release "v0.0.0.1"
    arti.download_release(_repo=ARTIF_REPO, version="v0.0.0.1")


    sys.exit(0)

if __name__ == "__main__":
    main()