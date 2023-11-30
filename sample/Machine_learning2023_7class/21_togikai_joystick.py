import pygame
import datetime
import os
import sys
sys.path.append('/home/pi/togikai/togikai_function/')
import togikai_drive
import togikai_ultrasonic
import signal
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np

from pygame.locals import *

# GPIOピン番号の指示方法
GPIO.setmode(GPIO.BOARD)

#超音波センサ初期設定
# Triger -- Fr:15, FrLH:13, RrLH:35, FrRH:32, RrRH:36
t_list=[15,13,35,32,36]
GPIO.setup(t_list,GPIO.OUT,initial=GPIO.LOW)
# Echo -- Fr:26, FrLH:24, RrLH:37, FrRH:31, RrRH:38
e_list=[26,24,37,31,38]
GPIO.setup(e_list,GPIO.IN)


#PWM制御の初期設定
##モータドライバ:PCA9685のPWMのアドレスを設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
##動作周波数を設定
pwm.set_pwm_freq(60)

#アライメント調整済みPWMパラメータ読み込み
PWM_PARAM = togikai_drive.ReadPWMPARAM(pwm)


#Gard 210523
#Steer Right
if PWM_PARAM[0][0] - PWM_PARAM[0][1] >= 100: #No change!
    PWM_PARAM[0][0] = PWM_PARAM[0][1] + 100  #No change!
    
#Steer Left
if PWM_PARAM[0][1] - PWM_PARAM[0][2] >= 100: #No change!
    PWM_PARAM[0][2] = PWM_PARAM[0][1] - 100  #No change!


#パラメータ
#前壁との最小距離
Cshort = 5
#右左折判定基準
short = 80
#モーター出力
FORWARD_S = 60 #<=100
FORWARD_C = 40 #<=100
REVERSE = -60 #<=100
#Stear
LEFT = 90 #<=100
RIGHT = -90 #<=100
#データ記録用配列作成
d = np.zeros(7)
#操舵、駆動モーターの初期化
togikai_drive.Accel(PWM_PARAM,pwm,time,0)
togikai_drive.Steer(PWM_PARAM,pwm,time,0)

#一時停止（Enterを押すとプログラム実行開始）
print('Press any key to continue')
#input()

#開始時間
start_time = time.time()


# ジョイスティックの初期化
pygame.joystick.init()
try:
   # ジョイスティックインスタンスの生成
   joystick = pygame.joystick.Joystick(0)
   joystick.init()
   print('ジョイスティックの名前:', joystick.get_name())
   print('ボタン数 :', joystick.get_numbuttons())
except pygame.error:
   print('ジョイスティックが接続されていません')

# F710の操作設定
# スティック
# 左スティック#０：左右、１：上下
# 右スティック#３：左右、４：上下
axis_steer = 0
axis_accel = 4
# ボタン
# 8: 'back', 9: 'start', 10: 'Logitech',
# 0: 'A', 1: 'B', 2: 'X', 3: 'Y',
# 4: 'LB',7: 'R1',8: 'right_stick_press',
button_A = 0
button_B = 1
button_Y = 3
button_X = 2
button_S = 7

#センサー値と出力初期化
FRdis = 0
LHdis = 0
RHdis = 0
steer = 0
accel1 = 0 #Aボタン >>FORWARD_S
accel2 = 0 #Bボタン >>FORWARD_C
#Bボタンでストップ
s=0
   
# pygameの初期化
pygame.init()

#ここから走行用プログラム
while True:
    for e in pygame.event.get():
        accel1 = joystick.get_button(button_A)
        accel2 = joystick.get_button(button_X)
    if accel1 >0 or accel2 >0 :
        print("\nStart running!\n")
        accel1 =0 
        accel2 =0
        break                

try:
    while True:
        stime = round(time.time()-start_time,1)
        #Frセンサ距離
        FRdis = round(togikai_ultrasonic.Mesure(GPIO,time,15,26),1)
        #FrLHセンサ距離
        LHdis = round(togikai_ultrasonic.Mesure(GPIO,time,13,24),1)
        #FrRHセンサ距離
        RHdis = round(togikai_ultrasonic.Mesure(GPIO,time,32,31),1)
        #RrLHセンサ距離
        #RLHdis = round(togikai_ultrasonic.Mesure(GPIO,time,35,37),1)
        #RrRHセンサ距離
        #RRHdis = round(togikai_ultrasonic.Mesure(GPIO,time,36,38),1)

        
        for e in pygame.event.get():
            steer = round(joystick.get_axis(0),2)
            accel1 = joystick.get_button(0)
            accel2 = joystick.get_button(3)
            s = joystick.get_button(1)
        
        #終了処理
        #if FRdis < Cshort and LHdis < Cshort and RHdis < Cshort or s==1:
        if FRdis < Cshort or s==1:
            GPIO.cleanup()
            d = np.vstack([d,[stime,steer,accel1,accel2, FRdis, RHdis, LHdis]])
            dt=str(datetime.datetime.now()).replace(" ","-")
            np.savetxt('./'+dt+'manual_record_data.csv', d, fmt='%.3e')
            #np.savetxt('/home/pi/Desktop/manual_record_data.csv', d, fmt='%.3e')
            print("stop")
            break

        #切れ角の調整（7分割、0,30,60,90,120,150,180のイメージ)
        if steer < -0.9 :
            steer = -0.9
        elif -0.9 < steer < -0.6 :
            steer = -0.6
        elif -0.6 < steer < -0.3 :
            steer = -0.3
        elif -0.3 < steer < 0.3 :
            steer = 0.0
        elif 0.6> steer > 0.3 :
            steer = 0.3
        elif 0.9> steer > 0.6 :
            steer = 0.6
        elif steer > 0.9 :
            steer = 0.9
        togikai_drive.Steer(PWM_PARAM,pwm,time,int(steer*100)) 

        #アクセル値入力
        if accel1 > 0.5:
            togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
        elif accel2 > 0.5:
            togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
            
        #記録
        print("stime,steer,accel1,accel2,FRdis,FRdis,LHdis,RHdis  = ",stime,steer,accel1,accel2,FRdis,LHdis,RHdis)
        #time.sleep(0.1)
        d = np.vstack([d,[stime,steer,accel1,accel2, FRdis, RHdis, LHdis]])

except KeyboardInterrupt:
    # np.savetxt(filename, d, fmt='%.3e')
    d = np.vstack([d,[stime,steer,accel1,accel2, FRdis, RHdis, LHdis]])
    np.savetxt('/home/pi/Desktop/manual_record_data.csv', d, fmt='%.3e')
    print('stop!')
    GPIO.cleanup()

"""
            if steer > 0.3 :
                togikai_drive.Steer(PWM_PARAM,pwm,time,RIGHT) 
                if accel2 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                elif accel1 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,0)  
            elif steer > -0.3:
                togikai_drive.Steer(PWM_PARAM,pwm,time,0) #original = "-"
                if accel2 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
                elif accel1 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,0) 
               
            elif steer > -2:
                togikai_drive.Steer(PWM_PARAM,pwm,time,LEFT)
                if accel2 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_S)
                elif accel1 > 0.5:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,FORWARD_C)
                else:
                    togikai_drive.Accel(PWM_PARAM,pwm,time,0) 
"""

