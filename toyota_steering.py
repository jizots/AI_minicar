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
PULSE_RIGHT = 250

# shared_dataのインデントとセンサーの関係性をわかりやすくする用
class SensorIndex(Enum):
    FL = 0
    F = 1
    FR = 2
    LF = 3
    LB = 4

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

# shared_dataをローカル変数にコピーするか？何度もアクセスするので、今のままでいいのかわからない。
def setting(shared_data):
    if (shared_data[SensorIndex.FL.value] >= 20
        & shared_data[SensorIndex.F.value]
        & shared_data[SensorIndex.F.value] > shared_data[SensorIndex.FR.value]): #前方が空いてる状態か？
        if (abs(shared_data[SensorIndex.LF] - shared_data[SensorIndex.LB.value]) < 4): #車体は壁に水平か？
            steer_straight(PULSE_STRAIGHT, 0.05)
        elif ((shared_data[SensorIndex.LB] - shared_data[SensorIndex.LF.value] > 4)): #車体が左に傾いている？
            steer_right(PULSE_RIGHT, 0.05)
        else: #車体が右に傾いている？
            steer_left(PULSE_LEFT, 0.05)
    elif (shared_data[SensorIndex.FL.value] < 20
          & shared_data[SensorIndex.F.value] < 30
          & shared_data[SensorIndex.FR.value] < 40): #後ろに下がるしかない状態か？
        steer_straight(PULSE_STRAIGHT, 0.4)
    elif (shared_data[SensorIndex.FL.value] >= 20
          & shared_data[SensorIndex.F.value] < shared_data[SensorIndex.FR.value]): #右カーブする時か？
        steer_right(PULSE_RIGHT, 0.1)
    else: # 左カーブする時か？
        steer_left(PULSE_LEFT, 0.1)

def steering(shared_data):
    time.sleep(1) # センサープロセスが先に開始するのを待つ
    while True:
        print(f"Steering:{shared_data[0]},\
            {shared_data[1]},\
            {shared_data[2]},\
            {shared_data[3]},\
            {shared_data[4]}")
        time.sleep(1)
        setting(shared_data)
