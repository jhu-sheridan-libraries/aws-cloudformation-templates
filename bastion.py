#!/usr/bin/env python

from __future__ import print_function
from troposphere import Template, Join, Ref, Parameter, Output, GetAtt, Base64, Condition,\
     Equals, Not, If, Tags
from troposphere.ec2 import Instance, SecurityGroup, SecurityGroupRule, SecurityGroupIngress

import boto3

from default import *
CF_TEMPLATE_NAME="bastion.template"

with open('bastion/userdata.sh', 'r') as fileUserData:
    UserData = fileUserData.read()

class Bastion:
    def __init__(self):
        self.t = Template()

    def buildParameters(self):
        self.t.add_parameter(Parameter(
            "KeyName",
            Description="SSH Key to be used for user",
            Type="String"
        ))

        self.t.add_parameter(Parameter(
            "SubnetId",
            Description="Public mapped subnet to access the Bastion host",
            Type="String"
        ))

        self.t.add_parameter(Parameter(
            "ImageId",
            Description="Image used to boot this host",
            Type="String",
        ))

        self.t.add_parameter(Parameter(
            "VpcId",
            Description="VPC that this host belongs to",
            Type="String"
            ))
        self.paramUserData=self.t.add_parameter(Parameter(
            "UserData",
            Description="Plaintext userdata string",
            Type="String",
            Default=UserData
        ))
        self.paramDepartment=self.t.add_parameter(Parameter(
            'Department',
            Description='Department that is managing this resource',
            Type='String',
            Default='OPS',
            AllowedValues=[
                'OPS', 'LAG', 'DMS', 'GIS',
            ],
        ))
                
        
    def buildTemplate(self):
        ref_stack_id = Ref('AWS::StackId')
        ref_stack_name = Ref('AWS::StackName')
        
        security_group=self.t.add_resource(SecurityGroup(
            'BastionSshSecurityGroup',
            GroupDescription="Allow SSH from anywhere to the Bastion Host",
            VpcId=Ref("VpcId"),
            SecurityGroupIngress=[
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=22,
                    ToPort=22,
                    CidrIp='0.0.0.0/0',
                ),
            ],
        ))
                    
        host=self.t.add_resource(Instance(
            "Bastion",
            KeyName=Ref("KeyName"),
            InstanceType="t2.nano",
            ImageId=Ref("ImageId"),
            SecurityGroupIds=[Ref(security_group)],
            SubnetId=Ref("SubnetId"),
            UserData=Base64(Ref(self.paramUserData)),
            Tags=Tags(
                Name=Join('', [ref_stack_name, '-BastionHost']),
                Department=Ref(self.paramDepartment),
            )
        ))

        self.t.add_output(Output(
            "InstanceId",
            Description="Instance Id of the Bastion Host",
            Value=Ref(host),
            ))

        self.t.add_output(Output(
            "BastionDns",
            Description="DNS of Bastion Host",
            Value=GetAtt(host, "PublicDnsName"),
            )),

    def buildConditions(self):
        pass
            
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
    bastion = Bastion()
    bastion.buildParameters()
    bastion.buildConditions()
    bastion.buildTemplate()
    bastion.uploadTemplate()

if __name__ == '__main__':
    main()
