#!/usr/bin/env python

from __future__ import print_function
from troposphere import Template, Ref, Join, Parameter, Equals, Output
from troposphere.ec2 import Subnet as ec2Subnet
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.cloudformation import Stack
import semver
import boto3

from default import *
CF_TEMPLATE_NAME="subnet.template"

class Subnet():
    VERSION_MAJOR = 0
    VERSION_MINOR = 0
    VERSION_PATCH = 1
    VERSION_PRE = None
    VERSION_BUILD = "build.1"
    VERSION = semver.format_version(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_PRE, VERSION_BUILD)
    conditions = {
    }


            
    def __init__(self): 
        self.t = Template()       

    def buildParams(self):
        self.paramVPCID=self.t.add_parameter(Parameter(
            "VPCID",
            Description="The VPCID that this subnet will be attached to",
            Type="String"
        ))

        self.paramDepartment=self.t.add_parameter(Parameter(
            "Department",
            Description="The department that is managing this resource",
            Type="String",
            Default="OPS",
        ))
        
        self.paramCIDRBLock=self.t.add_parameter(Parameter(
            "CidrBlock",
            Description="The CIDR Block that will make up this subnet",
            Type="String",
        ))

        self.paramMapPublicIP=self.t.add_parameter(Parameter(
            "MapPublicIP",
            Description="Boolean switch for Mapping a public IP on Launch",
            Type="String",
            Default="False",
            AllowedValues=[
                "True", "False" ],
        ))

        self.paramRouteTable=self.t.add_parameter(Parameter(
            "RouteTableId",
            Description="Route Table to attach subnets",
            Type="String",
        ))

    def buildTemplate(self):
        self.buildParams()
        
        for c in self.conditions:
            self.t.add_condition(c, self.conditions[c])

        mysubnet=self.t.add_resource(ec2Subnet(
            "Subnet",
            CidrBlock=Ref(self.paramCIDRBLock),
            MapPublicIpOnLaunch=Ref(self.paramMapPublicIP),
            VpcId=Ref(self.paramVPCID),
        ))

        self.t.add_resource(SubnetRouteTableAssociation(
            "SubnetAssociation",
            RouteTableId=Ref(self.paramRouteTable),
            SubnetId=Ref(mysubnet),
            ))
        
        self.t.add_output([
            Output(
                "SubnetId",
                Description="SubnetId of the created Subnet",
                Value=Ref(mysubnet)
                )
            ])
            
    def uploadTemplate(self):
        botosession = boto3.Session(profile_name=AWS_PROFILE)
        s3_client = botosession.client('s3')
        res = s3_client.put_object(
            Body=self.t.to_json(),
            Bucket=AWS_BUCKET,
            Key=CF_TEMPLATE_NAME
            )

    def __str__(self):
        return self.t.to_json()

    
def main():
    subnet = Subnet()
    subnet.buildTemplate()
    subnet.uploadTemplate()
if __name__ == '__main__':
    main()
