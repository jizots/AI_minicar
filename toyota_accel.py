import time
import RPi.GPIO as GPIO  # ラズパイのGPIOピンを操作するためのモジュール
import Adafruit_PCA9685
import toyota_steering as steer
from enum import Enum

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

# 前進最高速、停止、後進最高速のPWM値
# moving forward ~371
# moving backward 390~
# stop 372~389
pwm_forward = 325
pwm_back = 430
pwm_stop = 380
strong = 60
medium = 40
weak = 20

PULSE_STRAIGHT = 390
PULSE_RIGHT = 440
PULSE_LEFT = 310

D = 0
sleeping = 0.01
exec_time = 0.2

CHANNEL_ACCEL = 1
CHANNEL_SENSOR_TRIG = 32
CHANNEL_SENSOR_ECHO = 31


class SensorIndex(Enum):
    FL = 0
    F = 1
    FR = 2
    LF = 3
    LB = 4


def init_sensor(trig, echo):
    # GPIOピン番号の指示方法
    GPIO.setmode(GPIO.BOARD)
    # 超音波センサ初期設定
    print(trig)
    print(echo)
    GPIO.setup(trig,GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(echo,GPIO.IN)


def measure_the_distance(trig, echo):
    global D
    sigon = 0  # Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0  # Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig, GPIO.HIGH)  # Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) # 10μs待つ
    GPIO.output(trig, GPIO.LOW)  # Trigピンの電圧をLOW(0V)にする
    while (GPIO.input(echo) == GPIO.LOW):
        sigon = time.time()  # Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
    while (GPIO.input(echo) == GPIO.HIGH):
        sigoff = time.time()  # Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
    D = (sigoff - sigon)*34000/2  # 距離を計算(単位はcm)
    # if d > 200:
    #     print("forward_sensor:ok!\n")


def moving_forward(sleeptime, power):
    print('moving_forward')
    # ====  １秒間まっすぐ進む  ====
    # タイヤを前進方向に回転させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, power)
    # a_sleep秒間続ける
    time.sleep(sleeptime)


def moving_backward(sleeptime, power):
    print('moving_backward')
    # ====  １秒間まっすぐ進む  ====
    # タイヤを前進方向に回転させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, power)
    # a_sleep秒間続ける
    time.sleep(sleeptime)


def stop():
    print('stop')
    # タイヤを停止させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, pwm_stop)


# テスト用メイン関数
def main():
    steer.steer_straight(PULSE_STRAIGHT, sleeping)
    init_sensor(CHANNEL_SENSOR_TRIG, CHANNEL_SENSOR_ECHO)
    while True:
        measure_the_distance(CHANNEL_SENSOR_TRIG, CHANNEL_SENSOR_ECHO)
        print(D)
        if D > 15:
            steer.steer_left(PULSE_LEFT, sleeping)
            moving_forward(exec_time, pwm_forward)
        else:
            break
    # moving_forward(exec_time, pwm_forward)
    moving_backward(1, pwm_back)
    stop()
    steer.steer_straight(PULSE_STRAIGHT, sleeping)
    GPIO.cleanup()


if __name__ == "__main__":
    main()


def setting(copy_data):
    if (
        copy_data[SensorIndex.F.value] >= 15 and
        copy_data[SensorIndex.FL.value] >= 15 and
        copy_data[SensorIndex.FR.value] >= 15
    ):
        moving_forward(exec_time, pwm_forward)
    elif (
        copy_data[SensorIndex.F.value] >= 15 and
        (
            copy_data[SensorIndex.FL.value] < 15 or
            copy_data[SensorIndex.FL.value] >= 5
        ) and
        (
            copy_data[SensorIndex.FR.value] < 15 or
            copy_data[SensorIndex.FR.value] >= 5
        )
    ):
        moving_forward(exec_time, pwm_forward)
    else:
        moving_backward(exec_time, pwm_back)


def accel(shared_data):
    time.sleep(2)  # センサープロセスが先に開始するのを待つ
    copy_data = [0, 0, 0, 0, 0]
    while True:
        copy_data[0] = shared_data[0]  # front_left
        copy_data[1] = shared_data[1]  # front
        copy_data[2] = shared_data[2]  # front_right
        copy_data[3] = shared_data[3]  # left_front
        copy_data[4] = shared_data[4]  # left_back
        # print(f"Accel:{copy_data[0]},\
        #     {copy_data[1]},\
        #     {copy_data[2]},\
        #     {copy_data[3]},\
        #     {copy_data[4]}")
        setting(copy_data)