#!/bin/bash
## Set up virtual environment for the packages to be included in the autosubnet lambda function

CURRENTDIR=`echo $PWD`
lambda_name="autosubnet"
zip_file="${lambda_name}.zip"
files="autosubnet.py"


rm -rf ./requests
rm -rf ./netaddr
rm -rf ./urllib3
rm -rf ./chardet
rm -rf ./idna
rm -rf ./cryptography
rm -rf ./certifi

rm -rf ~/tmp
mkdir ~/tmp
cd ~/tmp
pip install virtualenv --user
virtualenv lambda_package
cd lambda_package
source bin/activate
pip install requests
pip install netaddr
pip install urllib3
pip install chardet
pip install idna
pip install cryptography
pip install certifi
deactivate

mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/requests $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/netaddr $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/urllib3 $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/chardet $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/idna $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/cryptography $CURRENTDIR
mv /home/user/tmp/lambda_package/lib/python3.6/site-packages/certifi $CURRENTDIR

echo "requests and netaddr package added to the current directory"

cd $CURRENTDIR
chmod 755 ${files}
rm -rf ${zip_file}
zip -r "${zip_file}" netaddr requests urllib3 chardet idna cryptography certifi ${files}
echo
echo "autosubnet lambda file created"


