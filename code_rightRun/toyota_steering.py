import Adafruit_PCA9685
import time
from enum import Enum
import signal
import sys

# ラズパイから見たPCA9685の所在地の設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
# 通信の周波数の設定
pwm.set_pwm_freq(60)

# PCA9685とモーターの接続チャネル番号
CHANNEL_STEER = 0
# 390, 391を境にモーター回転が反転した。
# Leftへは最低でも440はないと効かないかも.530以上は試していない。
# Rightへは最低でも310はないと効かないかも.220以下は試していない。
PULSE_STRAIGHT = 387
PULSE_LEFT = 490
PULSE_LEFT_WEEKLY = 445
PULSE_RIGHT = 280
PULSE_RIGHT_WEEKLY = 310

# shared_dataのインデントとセンサーの関係性をわかりやすくする用
class SensorIndex(Enum):
    FL = 0
    F = 1
    FR = 2
    L = 3
    R = 4

# 1方向には2回連続しか曲がらないようにするためのカウンター
count_left = 0
count_right = 0
count_right_weekly = 0
count_left_weekly = 0

# PULSE_STRAIGHTの継続時間
STRAIGHT_TIME = 0.03
# PULSE_RIGHTの継続時間
RIGHT_TIME = 0.1
# PULSE_LEFTの継続時間
LEFT_TIME = 0.1
# Right, LeftとセットになるSTRAIGHTの継続時間
RESET_TIME = 0.1

# PULSE_RIGHT_WEEKLYの継続時間
RIGHT_WEEKLY_TIME = 0.08
# PULSE_LEFT_WEEKLYの継続時間
LEFT_WEEKLY_TIME = 0.08
# Week_Right, Week_LeftとセットになるSTRAIGHTの継続時間
RESET_WEEKLY_TIME = 0.08

def steer_straight(pulse, sleep_time):
    # print('steer_straight')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_left(pulse, sleep_time):
    # print('steer_left')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_right(pulse, sleep_time):
    # print('steer_right')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def setting(copy_data): #右壁に寄せて走るプログラム
    global count_left
    global count_right
    global count_right_weekly
    global count_left_weekly
    if (copy_data[SensorIndex.F.value] < 55): # 前が近すぎる場合の回避
        if (copy_data[SensorIndex.FR.value] < copy_data[SensorIndex.FL.value]): # 左がひらけている時
            print("Left")
            count_left += 1
            count_right = 0
            count_left_weekly = 0
            count_right_weekly = 0
            if (count_left > 2):
                print("Cancel Left")
                steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)
                count_left = 0
            else:
                steer_left(PULSE_LEFT, LEFT_TIME)
                steer_straight(PULSE_STRAIGHT, RESET_TIME)
        else: # 右がひらけている時
            print("Right")
            count_right += 1
            count_left = 0
            count_left_weekly = 0
            count_right_weekly = 0
            if (count_right > 2 and copy_data[SensorIndex.R.value] < 70):
                print("Cancel Right")
                steer_left(PULSE_LEFT_WEEKLY, 0.05)
                steer_straight(PULSE_STRAIGHT, 0.05)
                count_right = 0
            else:
                steer_right(PULSE_RIGHT, RIGHT_TIME)
                steer_straight(PULSE_STRAIGHT, RESET_TIME)
    elif (copy_data[SensorIndex.FL.value] < 25 or copy_data[SensorIndex.L.value] < 25): # 左壁に近すぎる
        count_left = 0
        count_left_weekly = 0
        if (copy_data[SensorIndex.FL.value] < 18 or copy_data[SensorIndex.L.value] < 18):
            print("Right")
            steer_right(PULSE_RIGHT, RIGHT_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_TIME)
        else:
            print("Right weekly")
            steer_right(PULSE_RIGHT_WEEKLY, RIGHT_WEEKLY_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_WEEKLY_TIME)
    elif (copy_data[SensorIndex.FR.value] < 22 or copy_data[SensorIndex.R.value] < 5): # 右壁に近すぎる
        print("Left")
        count_left += 1
        count_right = 0
        count_left_weekly = 0
        count_right_weekly = 0
        if (count_left > 2 and copy_data[SensorIndex.R.value] > 4):
            print("Cancel Left")
            steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)
            count_left = 0
        else:
            steer_left(PULSE_LEFT, LEFT_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_TIME)
    elif (copy_data[SensorIndex.R.value] < 15): # 右壁に近すぎる
        print("Left weekly")
        count_left_weekly += 1
        count_left = 0
        count_right = 0
        count_right_weekly = 0
        if (count_left_weekly > 2):
            print("Cancel Left weekly")
            steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)
            count_left_weekly = 0
        else:
            steer_left(PULSE_LEFT_WEEKLY, LEFT_WEEKLY_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_WEEKLY_TIME)
    elif (copy_data[SensorIndex.FR.value] > 40 and copy_data[SensorIndex.R.value] > 30): #右壁から離れている
        print("Right")
        count_right += 1
        count_left = 0
        count_left_weekly = 0
        count_right_weekly = 0
        if (count_right > 2 and copy_data[SensorIndex.R.value] < 70):
            print("Cancel Right")
            steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)
            count_right = 0
        else:
            steer_right(PULSE_RIGHT, RIGHT_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_TIME)
    elif (copy_data[SensorIndex.FR.value] > 30 and copy_data[SensorIndex.R.value] > 20): #右壁から離れている
        print("Right weekly")
        count_right_weekly += 1
        count_left = 0
        count_right = 0
        count_left_weekly = 0
        if (count_right_weekly > 2):
            print("Cancel Right weekly")
            steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)
            count_right_weekly = 0
        else:
            steer_right(PULSE_RIGHT_WEEKLY, RIGHT_WEEKLY_TIME)
            steer_straight(PULSE_STRAIGHT, RESET_WEEKLY_TIME)
    else:
        print("Straight")
        count_left = 0
        count_right = 0
        count_right_weekly = 0
        count_left_weekly = 0
        steer_straight(PULSE_STRAIGHT, STRAIGHT_TIME)

def steering(shared_data):
    def signal_handler(sig, frame):
        print("Stop steering")
        steer_straight(PULSE_STRAIGHT, 0.1)
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal_handler)

    time.sleep(2) # センサープロセスが先に開始するのを待つ
    copy_data = [0,0,0,0,0]

    try:
        while True:
            copy_data[SensorIndex.FL.value] = shared_data[0]
            copy_data[SensorIndex.F.value] = shared_data[1]
            copy_data[SensorIndex.FR.value] = shared_data[2]
            copy_data[SensorIndex.L.value] = shared_data[3]
            copy_data[SensorIndex.R.value] = shared_data[4]
            print(f"Steering: L:{copy_data[SensorIndex.L.value]}, \
FL:{copy_data[SensorIndex.FL.value]}, \
F:{copy_data[SensorIndex.F.value]}, \
FR:{copy_data[SensorIndex.FR.value]}, \
R:{copy_data[SensorIndex.R.value]}")
            setting(copy_data)

    except KeyboardInterrupt:
        steer_straight(PULSE_STRAIGHT, 0.1)

