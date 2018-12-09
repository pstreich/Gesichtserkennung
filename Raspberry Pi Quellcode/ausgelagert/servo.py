# Bibliotheken einbinden
import cv2
import os
import sys
import RPi.GPIO as GPIO

max_pwm = 249
min_pwm = 1

def move(servo, angle):
    		#Servomotor nach bestimmtem Winkel ausrichten
    		if (min_pwm <= angle <= max_pwm):
        		command = 'echo %s=%s > /dev/servoblaster' % (str(servo), str(angle))
        		os.system(command)
