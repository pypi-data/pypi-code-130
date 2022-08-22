# -*- coding: utf-8 -*-
"""



"""
import os, sys, time, datetime,inspect, json, yaml, gc, pandas as pd, numpy as np, glob

######################################################################################
from utilmy.utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    ss = help_create(__file__)
    print(ss)


####################################################################################
def test_all():
    """
    """
    test1()

def test1():
    """function test1

    """    
    data = glob_s3(bucket_name="", path="", recursive=True, max_items_per_api_call="1000", extra_params=[])
    print(json.dumps(data, indent=2))






####################################################################################
def s3_get_filelist_cmd(parent_cmd: list) -> list:
    """ # The real logic of making the api call

    """
    import json
    from subprocess import PIPE, Popen

    files_list = []
    # Run the cmd that we were passed and store the output
    proc = Popen(parent_cmd, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

    # If the cmd exited without error code, continue
    if proc.returncode == 0:

        # Load the output as JSON and add the response to files_list
        output = json.loads(out.decode("utf8"))
        files_list.extend(output["Contents"])

        # If there is a valid NextToken make recursive calls until there isn't
        if output["NextToken"]:

            # Create a copy of parent cmd
            recursive_cmd = parent_cmd[:]

            # If there was a starting token in previous request remove it
            if "--starting-token" in recursive_cmd:
                recursive_cmd.pop(-1)
                recursive_cmd.pop(-1)

            # Add NextToken as starting-token to next cli cmd
            recursive_cmd.extend(["--starting-token", output["NextToken"]])

            # Run the cmd and add the result to files list
            files_list.extend(get_files(recursive_cmd))
    else:
        print("Oh No. An Error Occurred!")
        raise Exception(err.decode("utf8"))

    # Return files_list which contains all data for this
    return files_list



def s3_split_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key



def glob_s3(path: str = None, recursive: bool = True, max_items_per_api_call: str = 1000,
            fields = "name,date,size",
            return_format='tuple',
            extra_params: list = None) -> list:
    """  Glob files on S3 using AWS CLI

    Docs::

        https://bobbyhadz.com/blog/aws-cli-list-all-files-in-bucket



    """        
    bucket_name, path = s3_split_path(path)

    #### {Name: Key, LastModified: LastModified, Size: Size}
    if 'name' in fields : sfield += "{Name: Key,"
    if 'date' in fields : sfield += "LastModified: LastModified,"
    if 'size' in fields : sfield += "Size: Size,"   
    sfield += sfield[:-1] + "}"


    # Create cmd to list all objects with default pagination
    cmd = ["aws", "s3api", "list-objects-v2", "--bucket", bucket_name, "--output", "json",
               "--query", "{Contents: Contents[]." + sfield + "  ,NextToken: "
                          "NextToken}"]

    # If pagination is not required, add flag
    if not recursive:
        cmd.append("--no-paginate")
    else:
        # Note : max_items_per_api_call * 1000 is the limit of files that this function can process
        cmd.extend(["--max-items", str(max_items_per_api_call)])

    # If only specific path is needed to be listed, add it
    if path:
        cmd.extend(["--prefix", path])

    # If any extra params were passed, add them here
    if extra_params:
        cmd.extend(extra_params)


    # run cmd and return files data
    files_data = s3_get_filelist_cmd(cmd)

    if 'tuple' in return_format:
      flist = []
      for xi in files_data :
        xlist = []
        if "Name" in xi:          xlist.append( xi['Name'] )
        if "LastModified" in xi:  xlist.append( xi['LastModified'] )
        if "Output" in xi:        xlist.append( xi['Output'] )
        flist.append( xlist )
      return flist
    else :  
      return files_data








############################################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()




