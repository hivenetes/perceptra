#!/bin/bash
# Script to run transcribe_mic.py with specified parameters

SERVER="184.105.6.78:50051"
INPUT_DEVICE=0
LANGUAGE_CODE="en-US"

python3 transcribe_mic.py --server $SERVER --input-device $INPUT_DEVICE --language-code $LANGUAGE_CODE
