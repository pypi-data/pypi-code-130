import boto3    
import os
import sys
import datetime

class AWS_Instances:
    def __init__(self, ec2resource, instanceType):
        self.instanceType = instanceType
        self.ec2resource = ec2resource
        self.instances = ec2resource.instances.filter(
            Filters=[{'Name': 'instance-type', 'Values': [instanceType]}, {'Name': 'instance-state-name',
             'Values': ['running']}])

    def getAllSystems(self):
        allInstances = []
        for i in self.instances:
            for t in i.tags:
                if t['Key'] == 'Name':
                    allInstances.append(t['Value'])
        return allInstances
    
    def getNumSystems(self):
        return len(list(self.instances))
    
    def getNumNormalSystems(self):
        numNormal = 0
        for i in self.instances:
            if i.spot_instance_request_id:
                continue
            else:
                numNormal = numNormal + 1
        return numNormal

    def getNormalSystemOwners(self):
        systemsAndTeams = []
        team = 'unknown'
        systemName = 'unnamed'
        for i in self.instances:
            if i.spot_instance_request_id:
                continue
            else:
                team = 'unknown'
                systemName = 'unnamed'
                if i.tags:
                    team = 'unknown'
                    for t in i.tags:
                        if t['Key'] == 'org-team':
                            team = t['Value']
                        if t['Key'] == 'Name':
                            systemName = t['Value']
                    systemsAndTeams.append((team, systemName))
        return systemsAndTeams
    
    def getNumSpotSystems(self):
        numSpot = 0
        for i in self.instances:
            if i.spot_instance_request_id:
                numSpot = numSpot + 1
        return numSpot
    
    def numSystemsWithoutReserveTag(self):
        need = 0
        doNotReserve = 0
        for i in self.instances:
            if 'reserve' not in [t['Key'] for t in i.tags]:
                doNotReserve = doNotReserve + 1
            else:
                for t in i.tags:
                    if t['Key'] == 'reserve':
                        if t['Value'] == 'true':
                            need = need + 1
                        else:
                            doNotReserve = doNotReserve + 1
        return doNotReserve
            
if __name__ == "__main__":
    ec2resource = boto3.resource('ec2')
    instance = 'm4.2xlarge'
    instanceData = AWS_Instances(ec2resource, instance)
    systemNameAndOwner = instanceData.getNormalSystemOwners()
    systemNameAndOwner.sort()
    print(systemNameAndOwner)
