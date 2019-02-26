**AWS Project 3**

**cfn-sharedinfra.yaml**
* Create a new VPC with 2 public subnets
* The 2 public subnets have a NAT gateway each
* Create 2 S3 buckets - one for the webserver code and the testing script
* The 2nd bucket will hold the lambda function for CIDR range generation

**create4.py**
* Create the zipped package for autosubnet lambda function and upload to the S3 Lambda bucket
