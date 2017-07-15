#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import cv2
import RPi.GPIO as GPIO
import os
import sys
import time

from slackclient import SlackClient


PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
servo = GPIO.PWM(PIN, 50)
val = [2.5,3.6875,4.875,6.0625,7.25,8.4375,9.625,10.8125,12]

slack_token = os.environ["SLACK_TOKEN"]
sc = SlackClient(slack_token)

bucket_name = os.environ["door_close_bucket"]
client = boto3.client('rekognition')
s3 = boto3.resource('s3')
object = "Person"

capture_image = "door_close.jpg"


def slack_post_message(message):
    sc.api_call(
      "chat.postMessage",
      channel="#test-reserve-room",
      text=message
    )


if __name__ == "__main__":

    while True:

        print("take picture...")
        c = cv2.VideoCapture(0)
        r, img = c.read()
        cv2.imwrite('./' + capture_image , img)
        c.release()
        print("uploading to S3...")
        s3.Bucket(bucket_name).upload_file('./' + capture_image , capture_image)
        # rekognition
        print("analize image by rekognition...")
        response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': capture_image
            }
        },
        MaxLabels=123,
        MinConfidence=10,
        )

        print("")
        print("============Rekognition Response=================")
        print(response)
        print("=================================================")
        print("")

 
        for i in response['Labels']:

            if i['Confidence'] > 12:
       
                print("")
                print("==============Detected Thing====================")
                print(i['Name'])
                print("=================================================")
                print("")

                if i['Name'] == object:
                    print("Desired object [" + object  + "] is Detected.")
                    # slack_post_message("doorを閉めるぜ！")


                    try:
                        servo.start(0.0)
                
                        servo.ChangeDutyCycle(val[0])
                        print("servo.ChangeDutyCycle(val[0])")
                        print(val[0])
                        time.sleep(1)
                        servo.ChangeDutyCycle(val[8])
                        print("servo.ChangeDutyCycle(val[8])")
                        print(val[8])
                        time.sleep(1.5)
                        servo.ChangeDutyCycle(val[0])
                        print("servo.ChangeDutyCycle(val[0])")
                        print(val[0])
                        time.sleep(1)
               
                
                    except KeyboardInterrupt:
                        pass


        time.sleep(1.5)
