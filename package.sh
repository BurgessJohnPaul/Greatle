#!/bin/bash
mkdir package
cd package
pip3 install -r ../requirements.txt --target .
zip -r9 ../function.zip .
cd ../
zip -g function.zip dynamo_helper.py
zip -g function.zip language_helper.py
zip -g function.zip greatle.py