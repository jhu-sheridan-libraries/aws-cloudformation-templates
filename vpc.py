from troposphere import Template, Ref, Tags, Join, Parameter, Output
from troposphere.ec2 import VPC as ec2VPC
from troposphere.ec2 import Subnet, NetworkAcl, NetworkAclEntry,\
     InternetGateway, VPCGatewayAttachment, RouteTable, Route,\
     SubnetRouteTableAssociation, SubnetNetworkAclAssociation
import semver
import argparse
import boto3


VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_PATCH = 1
VERSION_PRE = None
VERSION_BUILD = "build.1"
VERSION = semver.format_version(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_PRE, VERSION_BUILD)

#AWS PROFILE - Probably make this an argument
AWS_PROFILE="jhu"
AWS_BUCKET="msel-cf-templates"

CF_TEMPLATE_NAME = "vpc.template"

class VPC:
    t = Template()

    def buildTemplate(self):
        self.t.add_metadata({
            "Comments": "This will build a standard VPC with public and private subnets",
            "Version": VERSION,
            "Author": "Derek Belrose <dbelrose@jhu.edu>",
            })

        ### Back references
        ref_stack_id = Ref('AWS::StackId')
        ref_region = Ref('AWS::Region')
        ref_stack_name = Ref('AWS::StackName')
    
        ### Parameters
        self.t.add_parameter(Parameter(
            "AvailabilityZone",
            Description = "Default availablility zone to run this in",
            Type="String",
            Default = "us-east-1",
            AllowedValues = [
                "us-east-1", "us-east-2", "us-west-1", "us-west-2", "us-west-3"
                ],
                ConstraintDescription="must be a valud AWS AZ in the US"
            ))

        paramCIDR=self.t.add_parameter(Parameter(
            "VPCCidrBlock",
            Description = "The CIDR block that the VPC will contain",
            Type="String",
            Default = "10.0.0.0/16",
            ))

        paramDepartment=self.t.add_parameter(Parameter(
            "Department",
            Description="Department for Tags",
            Type="String",
            Default = "OPS",
            AllowedValues=[
                'OPS', 'LAG', 'DMS', 'GIS',
                ]
            ))

        # Template resources
        vpc=self.t.add_resource(ec2VPC(
            "VPC",
            CidrBlock=Ref(paramCIDR),
            EnableDnsSupport="True",
            EnableDnsHostnames="True",
            Tags=Tags(
                Name=Join('', [ ref_stack_name, '-VPC']),
                Department=Ref(paramDepartment)
                )
            ))

        ig=self.t.add_resource(InternetGateway(
            "InternetGateway",
            Tags=Tags(
                Name=Join('', [ref_stack_name, '-ig']),
                Department=Ref(paramDepartment)
                )
            ))

        vpciga=self.t.add_resource(VPCGatewayAttachment(
            "GatewayAttachment",
            InternetGatewayId=Ref(ig),
            VpcId=Ref(vpc)
            ))

        rt = self.t.add_resource(RouteTable(
            "RouteTable",
            VpcId=Ref(vpc)
            ))

        eroute = self.t.add_resource(Route(
            "ExternalRoute",
            RouteTableId=Ref(rt),
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref(ig)
            ))            
    
        ### Outputs
        self.t.add_output([
            Output(
                "VpcId",
                Description="VPC ID of the created VPC",
                Value=Ref(vpc)
                ),
            Output(
                "RouteTableId",
                Description="RouteTable Id",
                Value=Ref(rt)
                ),
        ])
        return self.t
    
    def uploadTemplate(self):
        botosession = boto3.Session(profile_name=AWS_PROFILE)
        s3_client = botosession.client('s3')
        res = s3_client.put_object(
            Body=self.t.to_json(),
            Bucket="msel-cf-templates",
            Key=CF_TEMPLATE_NAME
            )

    def __str__(self):
        return self.t.to_json()

def main():
    vpc = VPC()
    vpc.buildTemplate()
    vpc.uploadTemplate()
    
if __name__ == '__main__':
    main()
