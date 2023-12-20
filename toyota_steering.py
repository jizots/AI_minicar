import Adafruit_PCA9685
import time

# ラズパイから見たPCA9685の所在地の設定
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
# 通信の周波数の設定。どこからどこへの？60がいいの？
pwm.set_pwm_freq(60)

# PCA9685とモーターの接続チャネル番号
CHANNEL_STEER = 0
# 元に戻す、のようなものがあるのかわからなかった。荷重してからが本番か。
PULSE_STRAIGHT = 390
# 390, 391を境にモーター回転が反転した。
# Leftへは最低でも440はないと効かないかも.530以上は試していない。
# Leftへは最低でも310はないと効かないかも.220以下は試していない。
PULSE_LEFT = 500
PULSE_RIGHT = 250
# テスト用の稼働時間設定
sleeping = 1

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

# Straightを仲介しなくても、ハンドルを切ることはできる。
def	main():
    steer_straight(PULSE_STRAIGHT, sleeping)
    steer_left(PULSE_LEFT, sleeping)
    steer_straight(PULSE_STRAIGHT, sleeping)
    steer_right(PULSE_RIGHT, sleeping)
    steer_left(PULSE_LEFT, sleeping)
    steer_right(PULSE_RIGHT, sleeping)
    steer_straight(PULSE_STRAIGHT, sleeping)

if __name__ == "__main__":
    main()

def steering(shared_data):
    print("Steering")