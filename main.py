#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import RPi.GPIO as GPIO
import os
import sys
import time
from slackclient import SlackClient


PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
servo = GPIO.PWM(PIN, 50)       # GPIO.PWM(PIN, [[34m~Q波[34m~U(Hz)])

val = [2.5,3.6875,4.875,6.0625,7.25,8.4375,9.625,10.8125,12]

slack_token = os.environ["SLACK_TOKEN"]
sc = SlackClient(slack_token)
client = boto3.client('rekognition')
object = "person"

def slack_post_message(message):
    sc.api_call(
      "chat.postMessage",
      channel="#test-reserve-room",
      text=message
    )


if __name__ == "__main__":

    while True:


        print "take picture..."
        os.system('fswebcam door_close.jpg')
        print "uploading to S3..."
        os.system('aws s3 cp door_close.jpg s3://bucket-name/door_close.jpg')
        # rekognition
        print "analize image by rekognition..."
        response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': 'bucket-name',
                'Name': 'door_close.jpg'
            }
        },
        MaxLabels=123,
        MinConfidence=10,
        )
        
 	print ""
        print "============Rekognition Response================="
        print response
        print "================================================="
        print ""

 
        for i in response['Labels']:

            if i['Confidence'] > 12:
       
                print ""
		print "==============Detected Thing===================="
                print i['Name']
                print "================================================="
                print ""

                if i['Name'] == True:
                    print("Desired object [" + object  + "] is Detected.")
                    slack_post_message("doorを閉めるぜ！")


                    try:
                        servo.start(0.0)
                
                        servo.ChangeDutyCycle(val[0])
                        print("servo.ChangeDutyCycle(val[0])")
                        print(val[0])
                        time.sleep(3)
                        servo.ChangeDutyCycle(val[8])
                        print("servo.ChangeDutyCycle(val[8])")
                        print(val[8])
                        time.sleep(3)
                        servo.ChangeDutyCycle(val[0])
                        print("servo.ChangeDutyCycle(val[0])")
                        print(val[0])
                        time.sleep(3)
                
                
                    except KeyboardInterrupt:
                        pass


        servo.ChangeDutyCycle(val[4])
        time.sleep(5)
        servo.stop()
        GPIO.cleanup()
