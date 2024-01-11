import Adafruit_PCA9685
import time
from enum import Enum

# ラズパイから見たPCA9685の所在地の設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
# 通信の周波数の設定。どこからどこへの？60がいいの？
pwm.set_pwm_freq(60)

# PCA9685とモーターの接続チャネル番号
CHANNEL_STEER = 0
# 元に戻す、のようなものがあるのかわからなかった。荷重してからが本番か。
# 390, 391を境にモーター回転が反転した。
# Leftへは最低でも440はないと効かないかも.530以上は試していない。
# Rightへは最低でも310はないと効かないかも.220以下は試していない。
PULSE_STRAIGHT = 390
PULSE_LEFT = 490
PULSE_LEFT_WEEKLY = 460
PULSE_RIGHT = 290
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
    # print('steer_left')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_right(pulse, sleep_time):
    # print('steer_right')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def setting(copy_data):
    if (copy_data[SensorIndex.F.value] < 25): #前に近い時の緊急の回避行動
        if (copy_data[SensorIndex.FR.value] > copy_data[SensorIndex.FL.value]):
            steer_right(PULSE_RIGHT, 0.1)
            print("                                                  F!! turn R")
        else:
            steer_left(PULSE_LEFT, 0.1)
            print("                                                  F!! turn L")
    elif (((copy_data[SensorIndex.FL.value] < copy_data[SensorIndex.L.value]) and
            copy_data[SensorIndex.L.value] < 30) or 
            (copy_data[SensorIndex.FL.value] < 15)): #壁に近く and 車体が左に傾いている <- 傾いている時の精度は当てに全くならないが大小なら比較できる
        steer_right(PULSE_RIGHT, 0.1)  #FLが近い時には強制的に曲がる
        steer_straight(PULSE_STRAIGHT, 0.02)
        print("                                                  R")
    elif (((copy_data[SensorIndex.FR.value] < copy_data[SensorIndex.R.value]) and
            copy_data[SensorIndex.R.value] < 30) or 
            (copy_data[SensorIndex.FR.value] < 15)): #壁に近く and 車体が右に傾いている
        steer_left(PULSE_LEFT, 0.1)  #FRが近い時には強制的に曲がる
        steer_straight(PULSE_STRAIGHT, 0.02)
        print("                                                  L")
    elif (copy_data[SensorIndex.R.value] > 35 and
        (copy_data[SensorIndex.FR.value] > copy_data[SensorIndex.R.value])): #右壁から遠ざかりすぎているので近づくように右に曲がる
        steer_right(PULSE_RIGHT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.02)
        print("                                                  weak R")
    elif (copy_data[SensorIndex.R.value] < 10 and
        (copy_data[SensorIndex.FR.value] > copy_data[SensorIndex.R.value])): #右壁から近すぎているので近づくように左に曲がる
        steer_left(PULSE_LEFT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.02)
        print("                                                  weak L")
    else:
        steer_straight(PULSE_STRAIGHT, 0.1)
        print("                                                  GO")

def steering(shared_data):
    time.sleep(2) # センサープロセスが先に開始するのを待つ
    copy_data = [0,0,0,0,0]
    while True:
        copy_data[SensorIndex.FL.value] = shared_data[0]  # front_left
        copy_data[SensorIndex.F.value] = shared_data[1]  # front
        copy_data[SensorIndex.FR.value] = shared_data[2]  # front_right
        copy_data[SensorIndex.L.value] = shared_data[3]  # left
        copy_data[SensorIndex.R.value] = shared_data[4]  # right
        print(f"Steering: L:{copy_data[SensorIndex.L.value]}, \
FL:{copy_data[SensorIndex.FL.value]}, \
F:{copy_data[SensorIndex.F.value]}, \
FR:{copy_data[SensorIndex.FR.value]}, \
R:{copy_data[SensorIndex.R.value]}")

        setting(copy_data)
