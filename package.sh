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
zip -g function.zip journal_helper.py
zip -g function.zip speech_helper.py
zip -g function.zip sentiment_helper.py
zip -g function.zip meme_helper.py
zip -g function.zip greatle.py
zip -g function.zip greetings.json