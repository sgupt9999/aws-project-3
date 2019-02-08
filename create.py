#!/usr/local/bin/python3.6

import boto3
import sys

def bucket_exists(bucket):
        # check if this bucket already exists
        client = boto3.client('s3')
        response = client.list_buckets()
        for bucket2 in response['Buckets']:
                if bucket2['Name'] == bucket:
                        return True
        return False

VPCStack = 'sharedinfrastructure'

AppStack = 'ApplicationEnvironment'
app_version = '1'
app_private_cidr_a = '10.20.8.0/24'
app_private_cidr_b = '10.20.9.0/24'
app_public_cidr_a = '10.20.10.0/24'
app_public_cidr_b = '10.20.11.0/24'
	
client = boto3.client('cloudformation')
vpcfile = open('cfn-sharedinfra.yaml')
vpctemplate = vpcfile.read()
response = client.create_stack(StackName=VPCStack,TemplateBody=vpctemplate)
print(response['StackId'])
print()

waiter = client.get_waiter('stack_create_complete')
waiter.wait(StackName = response['StackId'])

response2=client.describe_stacks(StackName='sharedinfrastructure')
print(response2['Stacks'][0]['Outputs'])
for dict in response2['Stacks'][0]['Outputs']:
	if dict['OutputKey'] == 'appbucketurl':
		appbucketurl = dict['OutputValue']
		#print(dict['OutputValue'])


## get the resources from VPC stack needed to run the application stack

vpc = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='VPC')['StackResourceDetail']['PhysicalResourceId']
s3appbucket = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='S3AppBucket')['StackResourceDetail']['PhysicalResourceId']
privateroutetablea = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='RouteTablePrivateA')['StackResourceDetail']['PhysicalResourceId']
privateroutetableb = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='RouteTablePrivateB')['StackResourceDetail']['PhysicalResourceId']
publicroutetable = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='RouteTablePublic')['StackResourceDetail']['PhysicalResourceId']

s3 = boto3.client('s3')
# Add the App and Test files to the newly created S3 bucket
for x in range(1,4):
	content = open('App' + str(x) + '.zip','rb')
	s3.put_object(Bucket=s3appbucket,Key='App' + str(x) + '.zip',Body=content)
	content = open('Test' + str(x) + '.zip','rb')
	s3.put_object(Bucket=s3appbucket,Key='Test' + str(x) + '.zip',Body=content)


# create the application stack
app_file = open('cfn-app1.yaml')
app_template = app_file.read()
app_response = client.create_stack(StackName=AppStack,TemplateBody=app_template,Parameters=[{'ParameterKey':'APPBucketURL','ParameterValue':appbucketurl},\
                                        {'ParameterKey':'PRIVATERTA','ParameterValue':privateroutetablea},\
                                        {'ParameterKey':'PRIVATERTB','ParameterValue':privateroutetableb},\
                                        {'ParameterKey':'PUBLICRT','ParameterValue':publicroutetable},\
                                        {'ParameterKey':'VPCID','ParameterValue':vpc},\
                                        {'ParameterKey':'APPVERSION','ParameterValue':app_version},\
                                        {'ParameterKey':'APPPrivateCIDRA','ParameterValue':app_private_cidr_a},\
                                        {'ParameterKey':'APPPrivateCIDRB','ParameterValue':app_private_cidr_b},\
                                        {'ParameterKey':'APPPublicCIDRA','ParameterValue':app_public_cidr_a},\
                                        {'ParameterKey':'APPPublicCIDRB','ParameterValue':app_public_cidr_b}\
					])
app_waiter = client.get_waiter('stack_create_complete')
app_waiter.wait(StackName = app_response['StackId'])
print("All Done")

