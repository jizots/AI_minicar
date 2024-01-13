import Adafruit_PCA9685
import time
from enum import Enum

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
    print('steer_left')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_right(pulse, sleep_time):
    print('steer_right')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def setting(copy_data):
    # # Try2用
    # diff_FR_FL = copy_data[SensorIndex.FR.value] - copy_data[SensorIndex.FL.value] # 値がプラスなら左が近い
    # Try1用
    if (copy_data[SensorIndex.FL.value] < 35 or
        copy_data[SensorIndex.L.value] < 30): # 左が近すぎる場合の回避
        steer_right(PULSE_RIGHT, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.05) # 一気にハンドルを切ると車体が傾くので、少しだけまっすぐにする
    elif (copy_data[SensorIndex.FR.value] < 35 or
        copy_data[SensorIndex.R.value] < 30):# 右が近すぎる場合の回避
        steer_left(PULSE_LEFT, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.05)
    elif (copy_data[SensorIndex.F.value] <
          (copy_data[SensorIndex.FR.value] / 3 * 2)): # 右前がひらけている時 Try2の場合は以下コメントアウト
        steer_right(PULSE_RIGHT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.05)
    elif (copy_data[SensorIndex.F.value] <
          (copy_data[SensorIndex.FL.value] / 3 * 2)): # 左前がひらけている時
        steer_left(PULSE_LEFT_WEEKLY, 0.1)
        steer_straight(PULSE_STRAIGHT, 0.05)
    else:
        steer_straight(PULSE_STRAIGHT, 0.1)

    # # Try2用 
    # elif (-40 < diff_FR_FL and diff_FR_FL < 40):
    #     steer_straight(PULSE_STRAIGHT, 0.1)
    # elif (diff_FR_FL > 0):
        # steer_right(PULSE_RIGHT_WEEKLY, 0.1)
    #     steer_straight(PULSE_STRAIGHT, 0.05)
    # else:
    #     steer_left(PULSE_LEFT_WEEKLY, 0.1)
    #     steer_straight(PULSE_STRAIGHT, 0.05)

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
