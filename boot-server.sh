#!/bin/bash
yum -y install wget
pip install boto3 flask
# wget https://s3-us-west-2.amazonaws.com/gameday-resources/server.py
wget https://raw.githubusercontent.com/bcnewlin/unifixers/master/server.py
chmod +x server.py
python server.py 'bc405a4b23' 'https://dashboard.cash4code.net/score'
