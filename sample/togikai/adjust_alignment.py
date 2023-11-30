import os
import sys
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np
import smbus            # use I2C
import math
from time import sleep  # time module

def writetofile(path,STEERING_RIGHT_PWM,STEERING_CENTER_PWM,STEERING_LEFT_PWM,THROTTLE_FORWARD_PWM,THROTTLE_STOPPED_PWM,THROTTLE_REVERSE_PWM):
    f = open(path,'w')
    f.write('DO NOT CHANGE PARAMETER!!\n')
    f.write('STEERING_RIGHT_PWM\n')
    f.write(str(STEERING_RIGHT_PWM))
    f.write('\n')
    f.write('STEERING_CENTER_PWM\n')
    f.write(str(STEERING_CENTER_PWM))
    f.write('\n')
    f.write('STEERING_LEFT_PWM\n')
    f.write(str(STEERING_LEFT_PWM))
    f.write('\n\n')
    f.write('THROTTLE_FORWARD_PWM\n')
    f.write(str(THROTTLE_FORWARD_PWM))
    f.write('\n')
    f.write('THROTTLE_STOPPED_PWM\n')
    f.write(str(THROTTLE_STOPPED_PWM))
    f.write('\n')
    f.write('THROTTLE_REVERSE_PWM\n')
    f.write(str(THROTTLE_REVERSE_PWM))
    f.write('\n\n')
    f.close()

def Accel(Duty):
    if Duty >= 0:
        throttle_pwm = int(THROTTLE_STOPPED_PWM - (THROTTLE_STOPPED_PWM - THROTTLE_FORWARD_PWM)*Duty/100)
        pwm.set_pwm(13, 0, throttle_pwm)
    elif Duty == 0:
        pwm.set_pwm(13, 0, THROTTLE_STOPPED_PWM)
        time.sleep(0.01)
    else:
        #Need to Reverse -> Stop -> Reverse
        pwm.set_pwm(13, 0, THROTTLE_REVERSE_PWM)
        time.sleep(0.05)
        pwm.set_pwm(13, 0, THROTTLE_STOPPED_PWM)
        time.sleep(0.05)
        throttle_pwm = int(THROTTLE_STOPPED_PWM + (THROTTLE_REVERSE_PWM - THROTTLE_STOPPED_PWM)*abs(Duty)/100)
        pwm.set_pwm(13, 0, throttle_pwm)
    #print('Throttle = ',throttle_pwm)
    #print(type(throttle_pwm))

def Steer(Duty):
    if Duty >= 0:
        steer_pwm = int(STEERING_CENTER_PWM + (STEERING_RIGHT_PWM - STEERING_CENTER_PWM)*Duty/100)
        pwm.set_pwm(14, 0, steer_pwm)
    else:
        steer_pwm = int(STEERING_CENTER_PWM - (STEERING_CENTER_PWM - STEERING_LEFT_PWM)*abs(Duty)/100)
        pwm.set_pwm(14, 0, steer_pwm)


path = '/home/pi/togikai/alignment_parameter.txt'

try:
    with open(path) as f:
        l = f.readlines()
        STEERING_RIGHT_PWM = int(l[2])
        STEERING_CENTER_PWM = int(l[4])
        STEERING_LEFT_PWM = int(l[6])
        THROTTLE_FORWARD_PWM = int(l[9])
        THROTTLE_STOPPED_PWM = int(l[11])
        THROTTLE_REVERSE_PWM = int(l[13])
except:
    STEERING_RIGHT_PWM = 490
    STEERING_CENTER_PWM = 390
    STEERING_LEFT_PWM = 290
    THROTTLE_FORWARD_PWM = 470
    THROTTLE_STOPPED_PWM = 390
    THROTTLE_REVERSE_PWM = 310
    writetofile(path,STEERING_RIGHT_PWM,STEERING_CENTER_PWM,STEERING_LEFT_PWM,THROTTLE_FORWARD_PWM,THROTTLE_STOPPED_PWM,THROTTLE_REVERSE_PWM)


pwm = Adafruit_PCA9685.PCA9685(address=0x40) #address:PCA9685のI2C Channel 0x40
pwm.set_pwm_freq(60)

Accel(0)
Steer(0)

print('========================================')
print('      Steer Adjustment(zero set)')
print('========================================')
while True:
    print('----------------------------------------')
    print('Press  l  /  r  and return to adjust.')
    print('After adjustment, press  e  and return.')
    print('----------------------------------------')
    ad = input()
    if ad == 'l':
        STEERING_CENTER_PWM -= 5
        print('PWM = ',STEERING_CENTER_PWM)
    elif ad == 'r':
        STEERING_CENTER_PWM += 5
        print('PWM = ',STEERING_CENTER_PWM)
    elif ad == 'e':
        STEERING_RIGHT_PWM = STEERING_CENTER_PWM + 100 #210522
        STEERING_LEFT_PWM = STEERING_CENTER_PWM - 100 #210522
        break
    pwm.set_pwm(14, 0, STEERING_CENTER_PWM)

print('========================================')
print('      Accel Adjustment(zero set)')
print('========================================')
while True:
    print('----------------------------------------')
    print('Press  +  /  -  and return to adjust.')
    print('After adjustment, press  e  and return.')
    print('----------------------------------------')
    ad = input()
    if ad == '+':
        THROTTLE_STOPPED_PWM -= 5
        print('PWM = ',THROTTLE_STOPPED_PWM)
    elif ad == '-':
        THROTTLE_STOPPED_PWM += 5
        print('PWM = ',THROTTLE_STOPPED_PWM)
    elif ad == 'e':
        THROTTLE_FORWARD_PWM = THROTTLE_STOPPED_PWM + 80 #210522
        THROTTLE_REVERSE_PWM = THROTTLE_STOPPED_PWM - 80 #210522
        break
    pwm.set_pwm(13, 0, THROTTLE_STOPPED_PWM)

writetofile(path,STEERING_RIGHT_PWM,STEERING_CENTER_PWM,STEERING_LEFT_PWM,THROTTLE_FORWARD_PWM,THROTTLE_STOPPED_PWM,THROTTLE_REVERSE_PWM)

print(path,STEERING_RIGHT_PWM,STEERING_CENTER_PWM,STEERING_LEFT_PWM,THROTTLE_FORWARD_PWM,THROTTLE_STOPPED_PWM,THROTTLE_REVERSE_PWM)
