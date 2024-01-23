import Adafruit_PCA9685
import time
from enum import Enum
import signal
import sys

# ラズパイから見たPCA9685の所在地の設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
# 通信の周波数の設定。どこからどこへの？60がいいの？
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

# Leftには2回連続しか曲がらないようにするためのカウンター
count_left = 0
# Rightには2回連続しか曲がらないようにするためのカウンター
count_right = 0
# Right_weeklyには2回連続しか曲がらないようにするためのカウンター
count_right_weekly = 0
# Left_weeklyには2回連続しか曲がらないようにするためのカウンター
count_left_weekly = 0

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
                steer_straight(PULSE_STRAIGHT, 0.5)
                count_left = 0
            else:
                steer_left(PULSE_LEFT, 0.1)
                steer_straight(PULSE_STRAIGHT, 0.1)
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
                steer_right(PULSE_RIGHT, 0.1)
                steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.FL.value] < 20 or copy_data[SensorIndex.L.value] < 20): # 左壁に近すぎる
        count_left = 0
        count_right = 0
        if (copy_data[SensorIndex.FL.value] < 15 or copy_data[SensorIndex.L.value] < 15):
            print("Right")
            steer_right(PULSE_RIGHT, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
        else:
            print("Right weekly")
            steer_right(PULSE_RIGHT_WEEKLY, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.FR.value] < 22 or copy_data[SensorIndex.R.value] < 5): # 右壁に近すぎる
        print("Left")
        count_left += 1
        count_right = 0
        if (count_left > 2):
            print("Cancel Left")
            steer_straight(PULSE_STRAIGHT, 0.05)
            count_left = 0
        else:
            steer_left(PULSE_LEFT, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.R.value] < 15): # 右壁に近すぎる
        print("Left weekly")
        count_left_weekly += 1
        count_left = 0
        count_right = 0
        count_right_weekly = 0
        if (count_left_weekly > 2):
            print("Cancel Left weekly")
            steer_straight(PULSE_STRAIGHT, 0.05)
            count_left_weekly = 0
        else:
            steer_left(PULSE_LEFT_WEEKLY, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.FR.value] > 40 and copy_data[SensorIndex.R.value] > 30): #右壁から離れている
        print("Right")
        count_right += 1
        count_left = 0
        if (count_right > 2 and copy_data[SensorIndex.R.value] < 70):
            print("Cancel Right")
            steer_straight(PULSE_STRAIGHT, 0.05)
            count_right = 0
        else:
            steer_right(PULSE_RIGHT, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.08)
    elif (copy_data[SensorIndex.FR.value] > 30 and copy_data[SensorIndex.R.value] > 20): #右壁から離れている
        print("Right weekly")
        count_left = 0
        count_right = 0
        count_right_weekly += 1
        if (count_right_weekly > 2):
            print("Cancel Right weekly")
            steer_right(PULSE_RIGHT_WEEKLY, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
            count_right_weekly = 0
        else:
            steer_straight(PULSE_STRAIGHT, 0.05)
    else:
        print("Straight")
        count_left = 0
        count_right = 0
        count_right_weekly = 0
        count_left_weekly = 0
        steer_straight(PULSE_STRAIGHT, 0.05)
    # elif (copy_data[SensorIndex.FR.value] > copy_data[SensorIndex.R.value]): # 車体が左前に傾いている
    #     print("Right weekly")
    #     steer_right(PULSE_RIGHT_WEEKLY, 0.1)
    #     steer_straight(PULSE_STRAIGHT, 0.1)

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

