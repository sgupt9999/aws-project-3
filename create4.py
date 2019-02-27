#!/usr/local/bin/python3.6

import boto3
import sys
import subprocess

def bucket_exists(bucket):
        # check if this bucket already exists
        client = boto3.client('s3')
        response = client.list_buckets()
        for bucket2 in response['Buckets']:
                if bucket2['Name'] == bucket:
                        return True
        return False

## User inputs

VPCStack = 'sharedinfrastructure'

AppStack = 'ApplicationEnvironment'
app_version = '1'
app_private_cidr_a = '10.20.8.0/24'
app_private_cidr_b = '10.20.9.0/24'
app_public_cidr_a = '10.20.10.0/24'
app_public_cidr_b = '10.20.11.0/24'

AutoSubnetStack = 'AutoSubnet'

## End of user inputs

client = boto3.client('cloudformation')
vpcfile = open('cfn-sharedinfra.yaml')
vpctemplate = vpcfile.read()
response = client.create_stack(StackName=VPCStack,TemplateBody=vpctemplate)
print('Creating VPC stack')

waiter = client.get_waiter('stack_create_complete')
try:
	waiter.wait(StackName = response['StackId'])
except:
	print('There was a problem creating VPC stack. Exiting the program')
	exit(1)
print('VPC stack successfully created')

response2=client.describe_stacks(StackName=VPCStack)
print(response2['Stacks'][0]['Outputs'])
for dict in response2['Stacks'][0]['Outputs']:
	if dict['OutputKey'] == 'appbucketurl':
		appbucketurl = dict['OutputValue']                                        
		#print(dict['OutputValue'])


## get the s3 app bucket to upload app and zip files
s3appbucket = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='S3AppBucket')['StackResourceDetail']['PhysicalResourceId']

s3 = boto3.client('s3')
# Add the App and Test files to the newly created S3 bucket
for x in range(1,4):
	content = open('App' + str(x) + '.zip','rb')
	s3.put_object(Bucket=s3appbucket,Key='App' + str(x) + '.zip',Body=content)
	content = open('Test' + str(x) + '.zip','rb')
	s3.put_object(Bucket=s3appbucket,Key='Test' + str(x) + '.zip',Body=content)

## get the s3 lambda bucket to upload the autosubnet lambda function
s3lambdabucket = client.describe_stack_resource(StackName=VPCStack,LogicalResourceId='S3LambdaBucket')['StackResourceDetail']['PhysicalResourceId']
## Run the autosubnet lambda creation Description
r = subprocess.call('./create_lambda_fn.sh')
content = open('autosubnet.zip','rb')
s3.put_object(Bucket=s3lambdabucket,Key='autosubnet.zip',Body=content)


## create the autosubnet stack
## The stack creates a DynamoDB table and a Lambda function based on the zip file in s3lambdabucket
subnet_file = open('cfn-autosubnet.yaml')
subnet_template = subnet_file.read()
subnet_response = client.create_stack(StackName=AutoSubnetStack,TemplateBody=subnet_template,Capabilities=['CAPABILITY_NAMED_IAM'])
subnet_waiter = client.get_waiter('stack_create_complete')
try:
    subnet_waiter.wait(StackName = subnet_response['StackId'])
except:
    print('AutoSubnet stack creation failed. Exiting the script')
    exit(2)
print('AutoSubnet stack created successfully')

# create the application stack
app_file = open('cfn-app4.yaml')
app_template = app_file.read()
app_response = client.create_stack(StackName=AppStack,TemplateBody=app_template,Parameters=[{'ParameterKey':'APPVERSION','ParameterValue':app_version}])
app_waiter = client.get_waiter('stack_create_complete')
try:
	app_waiter.wait(StackName = app_response['StackId'])
except:
    print('Application creation failed. Exiting the script')
	## Ideally here the S3 bucket would be emptied and the vpc stack would be deleted
    exit(2)
print("All stacks created successfully")
