import boto3    
import os
import sys
import datetime

class ReservedInstances():
    def __init__(self, ec2client, instanceType):
        self.instanceType = instanceType
        self.ec2client = ec2client
        self.instances = ec2client.describe_reserved_instances(
        Filters=[{'Name': 'instance-type', 'Values': [instanceType]},{'Name': 'state', 'Values': ['active']}])
    
    def getNumRIStillAvailable(self, requestDate):
        riNum = 0
        for i in self.instances["ReservedInstances"]:
            if i['End'].replace(tzinfo=None) > requestDate:
                numInstances = i['InstanceCount']
                riNum = riNum + numInstances
        return riNum
    
    def getNumRIExpiring(self, requestDate):
        riNum = 0
        t = datetime.date.today()
        currentDate = datetime.datetime(t.year, t.month, t.day)
        for i in self.instances["ReservedInstances"]:
            if currentDate < i['End'].replace(tzinfo=None) < requestDate:
                numInstances = i['InstanceCount']
                riNum = riNum + numInstances
        return riNum
