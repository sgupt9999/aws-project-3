#!/bin/bash
## Set up virtual environment for the packages to be included in the autosubnet lambda function

CURRENTDIR=`echo $PWD`
lambda_name="autosubnet"
zip_file="${lambda_name}.zip"
files="autosubnet.py"


rm -rf ./requests
rm -rf ./netaddr

rm -rf ~/tmp
mkdir ~/tmp
cd ~/tmp
pip install virtualenv --user
virtualenv lambda_package
cd lambda_package
source bin/activate
pip install requests
pip install netaddr
deactivate

mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/requests $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/netaddr $CURRENTDIR

echo "requests and netaddr package added to the current directory"

cd $CURRENTDIR
chmod 755 ${files}
rm -rf ${zip_file}
zip -r "${zip_file}" netaddr requests ${files}
echo
echo "autosubnet lambda file created"


