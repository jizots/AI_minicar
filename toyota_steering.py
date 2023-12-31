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
PULSE_LEFT = 500
PULSE_LEFT_WEEKLY = 480
PULSE_RIGHT = 250
PULSE_RIGHT_WEEKLY = 275

# shared_dataのインデントとセンサーの関係性をわかりやすくする用
class SensorIndex(Enum):
    FL = 0
    F = 1
    FR = 2
    L = 3
    R = 4

def steer_straight(pulse, sleep_time):
    print('steer_straight')
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

def setting(copy_data):
    if (copy_data[SensorIndex.FR.value] < 20 or
        copy_data[SensorIndex.R.value] < 20):
        steer_left(PULSE_LEFT, 0.3)
    elif (copy_data[SensorIndex.FL.value] < 20 or
        copy_data[SensorIndex.L.value] < 20):
        steer_left(PULSE_RIGHT, 0.3)
    elif ((copy_data[SensorIndex.FL.value] >= 15)
        and (copy_data[SensorIndex.F.value] >= 60)
        and (copy_data[SensorIndex.F.value] > copy_data[SensorIndex.FR.value])): #前方が空いてる状態か？
            steer_straight(PULSE_STRAIGHT, 0.3)
    elif ((copy_data[SensorIndex.FL.value] < 15)
          and (copy_data[SensorIndex.F.value] < 30)
          and (copy_data[SensorIndex.FR.value] < 40)): #後ろに下がるしかない状態か？
        steer_straight(PULSE_STRAIGHT, 0.3)
    elif ((copy_data[SensorIndex.FL.value] >= 15)
          and (copy_data[SensorIndex.F.value] < copy_data[SensorIndex.FR.value])): #右カーブする時か？
        steer_right(PULSE_RIGHT, 0.3)
    else: # 左カーブする時か？
        steer_left(PULSE_LEFT, 0.3)

def steering(shared_data):
    time.sleep(2) # センサープロセスが先に開始するのを待つ
    copy_data = [0,0,0,0,0]
    while True:
        copy_data[0] = shared_data[0]  # front_left
        copy_data[1] = shared_data[1]  # front
        copy_data[2] = shared_data[2]  # front_right
        copy_data[3] = shared_data[3]  # left
        copy_data[4] = shared_data[4]  # right
        print(f"Steering:{copy_data[SensorIndex.FL.value]}, \
{copy_data[SensorIndex.F.value]}, \
{copy_data[SensorIndex.FR.value]}, \
{copy_data[SensorIndex.L.value]}, \
{copy_data[SensorIndex.R.value]}")

        time.sleep(0.05)
        setting(copy_data)
