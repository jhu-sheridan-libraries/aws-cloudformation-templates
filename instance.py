from __future__ import print_function
from troposphere import Template, Join, Ref, Parameter, Output, GetAtt
from troposphere.ec2 import Instance, SecurityGroup, SecurityGroupRule, SecurityGroupIngress

import boto3

class Ec2Instance:
    def __init__(self):
        self.t = Template()

    def buildParameters(self):
        self.paramKeyName=self.t.add_parameter(Parameter(
            "KeyName",
            Description="SSH Key to be used for user",
            Type="String",
        ))

        self.paramUserData=self.t.add_parameter(Parameter(
            "UserData"
            Description="UserData for the EC2 Instance",
            Type="String",
        ))

        self.paramSubnetId=self.t.add_parameter(Parameter(
            "SubnetId",
            Description="SubnetId to attach the EC2 Instance to",
            Type="String",
        ))


def main():
    pass

if __name__ == '__main__':
    main()
