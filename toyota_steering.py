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
PULSE_STRAIGHT = 390
PULSE_LEFT = 490
PULSE_LEFT_WEEKLY = 445
PULSE_RIGHT = 285
PULSE_RIGHT_WEEKLY = 320

# shared_dataのインデントとセンサーの関係性をわかりやすくする用
class SensorIndex(Enum):
    FL = 0
    F = 1
    FR = 2
    L = 3
    R = 4

def steer_straight(pulse, sleep_time):
    # print('steer_straight')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_left(pulse, sleep_time):
    print('steer_left')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_right(pulse, sleep_time):
    print('steer_right')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def setting(copy_data): #右壁に寄せて走るプログラム
    if (copy_data[SensorIndex.F.value] < 68): # 前が近すぎる場合の回避
        if (copy_data[SensorIndex.FR.value] < copy_data[SensorIndex.FL.value]): # 左がひらけている時
            steer_left(PULSE_LEFT, 0.12)
            steer_straight(PULSE_STRAIGHT, 0.1)
        else: # 右がひらけている時
            steer_right(PULSE_RIGHT, 0.12)
            steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.L.value] < 15 or copy_data[SensorIndex.FL.value] < 15): # 左壁に近すぎる
        steer_left(PULSE_RIGHT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.R.value] < 10 or copy_data[SensorIndex.FR.value] < 10): # 右壁に近すぎる
        steer_left(PULSE_LEFT, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.R.value] < 17 or copy_data[SensorIndex.FR.value] < 17): # 右壁に近すぎる
        steer_left(PULSE_LEFT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.F.value] >= 65):
        if (copy_data[SensorIndex.FR.value] > 50 or copy_data[SensorIndex.R.value] > 50): #右壁から離れている
            steer_right(PULSE_RIGHT, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
        elif (copy_data[SensorIndex.FR.value] > 30 or copy_data[SensorIndex.R.value] > 30): #右壁から離れている
            steer_right(PULSE_RIGHT_WEEKLY, 0.1)
            steer_straight(PULSE_STRAIGHT, 0.1)
    elif (copy_data[SensorIndex.FR.value] > copy_data[SensorIndex.R.value]): # 車体が左前に傾いている
        steer_right(PULSE_RIGHT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.1)
    else:
        steer_left(PULSE_LEFT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.1)

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

