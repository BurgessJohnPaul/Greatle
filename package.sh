#!/bin/bash
mkdir package
cd package
pcregrep -M 'BEGIN(.|\n)*?END' ../requirements.txt > ../lambda_reqs.txt
pip3 install -r ../lambda_reqs.txt --target .
zip -r9 ../function.zip .
cd ../
zip -g function.zip similarity_helper.py
zip -g function.zip dynamo_helper.py
zip -g function.zip language_helper.py
zip -g function.zip goal_helper.py
zip -g function.zip greatle.py
zip -g function.zip greetings.json