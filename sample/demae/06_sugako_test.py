
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
#Straight
RH_s =  30
LH_s =  30
ACCEL_s    =   60 #<=100

#Turn
Fr_t = 100
RH_t =  20
LH_t =  20
ACCEL_t    =   40 #<=100
STEER_RH_t = -100 #<=100
STEER_LH_t =  100 #<=100

#Reverse
Fr_r = 20
ACCEL_r    =  -60 #<=100

#PD制御パラメータ
Kp = 3
Kd = 1

#データ記録用配列作成
d = np.zeros(6)

#操舵、駆動モーターの初期化
togikai_drive.Accel(PWM_PARAM,pwm,time,0)
togikai_drive.Steer(PWM_PARAM,pwm,time,0)

#一時停止（Enterを押すとプログラム実行開始）
print('Press any key to continue')
input()

#変数初期化
t0 = time.time()
t1 = t0
Fr    = togikai_ultrasonic.Mesure(GPIO,time,15,26)
RH_Fr = togikai_ultrasonic.Mesure(GPIO,time,32,31)
RH_Rr = togikai_ultrasonic.Mesure(GPIO,time,36,38)
LH_Fr = togikai_ultrasonic.Mesure(GPIO,time,13,24)
LH_Rr = togikai_ultrasonic.Mesure(GPIO,time,35,37)

RH_min  = min(RH_Fr,RH_Rr)
RH_min1 = RH_min
LH_min  = min(LH_Fr,LH_Rr)
LH_min1 = LH_min

#走行用プログラム
try:
    while True:
        t = time.time() - t0
        Fr    = togikai_ultrasonic.Mesure(GPIO,time,15,26)
        RH_Fr = togikai_ultrasonic.Mesure(GPIO,time,32,31)
        RH_Rr = togikai_ultrasonic.Mesure(GPIO,time,36,38)
        LH_Fr = togikai_ultrasonic.Mesure(GPIO,time,13,24)
        LH_Rr = togikai_ultrasonic.Mesure(GPIO,time,35,37)

        RH_max = max(RH_Fr,RH_Rr)        
        RH_min = min(RH_Fr,RH_Rr)
        LH_max = max(LH_Fr,LH_Rr)
        LH_min = min(LH_Fr,LH_Rr)

        if Fr < Fr_r:
            MODE  = "REVERSE       "
            ACCEL = ACCEL_r
            STEER = 0
            dt = 1

        elif Fr < Fr_t:
            ACCEL = ACCEL_t
            dt = 0
	    if  RH_max > LH_max and RH_min > RH_t or LH_min < LH_t:
                MODE  = "TURN     RIGHT"
                STEER = STEER_RH_t
                #STEER = - Kp * (RH_min - RH_t) - Kd * (RH_min - RH_min1) / (t - t1) #右手法PD制御
            else:
                MODE  = "TURN     LEFT "
                STEER = STEER_LH_t
                #STEER =   Kp * (LH_min - LH_t) + Kd * (LH_min - LH_min1) / (t - t1) #左手法PD制御
            #if STEER < 0:
            #    MODE  = "STRAIGHT RIGHT"
            #else:
            #    MODE  = "STRAIGHT LEFT "

        else:
            ACCEL = ACCEL_s
            STEER = Kp * (LH_min - LH_s) + Kd * (LH_min - LH_min1) / (t - t1) #左手法PD制御
            dt = 0
            if STEER < 0:
                MODE  = "STRAIGHT RIGHT"
            else:
                MODE  = "STRAIGHT LEFT "

        ACCEL = min(ACCEL, 100)
        ACCEL = max(ACCEL,-100)
        STEER = min(STEER, 100)
        STEER = max(STEER,-100)

        togikai_drive.Accel(PWM_PARAM,pwm,time,ACCEL)
        togikai_drive.Steer(PWM_PARAM,pwm,time,STEER)
        time.sleep(dt)

        #距離データを配列に記録
        d = np.vstack([d,[t, LH_Rr, LH_Fr, Fr, RH_Fr, RH_Rr]])
        #距離を表示
        print('LH Rr:{1:.1f} , LH Fr:{2:.1f}, Fr:{3:.1f} , RH Fr:{4:.1f} , RH Rr:{5:.1f}'.format(LH_Rr,LH_Fr,Fr,RH_Fr,RH_Rr))
        print(MODE,'STEER:%.1f' %STEER)
        t1 = t
        RH_min1 = RH_min
        LH_min1 = LH_min

except KeyboardInterrupt:
    print('stop!')
    np.savetxt('/home/pi/code/record_data.csv', d, fmt='%.3e')
    togikai_drive.Accel(PWM_PARAM,pwm,time,0)
    togikai_drive.Steer(PWM_PARAM,pwm,time,0)
    GPIO.cleanup()
