#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import RPi.GPIO as GPIO
import os
import sys
import time
import ta7291
from slackclient import SlackClient

slack_token = os.environ["SLACK_TOKEN"]
sc = SlackClient(slack_token)
client = boto3.client('rekognition')

def slack_post_message(message):
    sc.api_call(
      "chat.postMessage",
      channel="#test-reserve-room",
      text=message
    )


if __name__ == "__main__":

    while True:

        # S3にdoor_close.jpgをアップロード
        print "take picture..."
        os.system('fswebcam door_close.jpg')
        print "uploading..."
        os.system('aws s3 cp door_close.jpg s3://smart-recognition/door_close.jpg')
        # rekognition
        print "analize image..."
        response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': 'smart-recognition',
                'Name': 'door_close.jpg'
            }
        },
        MaxLabels=123,
        MinConfidence=70,
        )
        
 	print ""
        print "============Rekognition Response================="
        print response
        print "================================================="
        print ""

 
        for i in response['Labels']:

            if i['Confidence'] > 80:
       
                print ""
		print "==============Detected Thing===================="
                print i['Name']
                print "================================================="
                print ""

                if i['Name'] == "Person":
                    print "Turn motor On!!!"
                    print "Closing door!!!"
                    slack_post_message("doorを閉めるぜ！")

                    d = ta7291.ta7291(18, 24, 25)
              
                    print "Normal Powerup/down..."
                    for power in range(0, 100, 10):
                    	d.drive(power)
                    	time.sleep(0.3)
                    for power in range(100, 0, -10):
                    	d.drive(power)
                    	time.sleep(0.3)
                    
                    print "Max speed 10 seconds, and stop..."
                    d.drive(100)
                    time.sleep(1)
                    d.drive(0)
                    time.sleep(3)
                    
                    print "Max speed 10 seconds, and brake..."
                    d.drive(100)
                    time.sleep(10)
                    d.brake()
                    time.sleep(3)
                    
                    d.cleanup()

        #time.sleep(15)
