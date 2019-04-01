#!/bin/bash
mkdir package
cd package
pip3 install -r ../requirements.txt --target .
zip -r9 ../function.zip .
cd ../
zip -g function.zip similarity_helper.py
zip -g function.zip dynamo_helper.py
zip -g function.zip language_helper.py
zip -g function.zip goal_helper.py
zip -g function.zip discovery_helper.py
zip -g function.zip greatle.py
zip -g function.zip greetings.json