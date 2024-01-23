import time
import RPi.GPIO as GPIO  # ラズパイのGPIOピンを操作するためのモジュール
import Adafruit_PCA9685
import toyota_steering as steer
import signal
import sys

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

# 前進最高速、停止、後進最高速のPWM値
# moving forward ~371
# moving backward 390~
# stop 372~389
pwm_forward = 313
pwm_back = 460
pwm_stop = 380

# 前進、後進の1回の継続時間
exec_time = 0.2

CHANNEL_ACCEL = 1
CHANNEL_SENSOR_TRIG = 32
CHANNEL_SENSOR_ECHO = 31

def moving_forward(sleeptime, power):
    # print('moving_forward')
    # タイヤを前進方向に回転させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, power)
    # a_sleep秒間続ける
    time.sleep(sleeptime)

def moving_backward(sleeptime, power):
    print('moving_backward')
    # タイヤを前進方向に回転させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, power)
    # a_sleep秒間続ける
    time.sleep(sleeptime)

def stop():
    print('stop')
    # タイヤを停止させる
    pwm.set_pwm(CHANNEL_ACCEL, 0, pwm_stop)

def setting(copy_data):
    if (copy_data[1] < 25):
        moving_backward(1.0, pwm_back)
    elif (copy_data[1] >= 25):
        moving_forward(exec_time, pwm_forward)

def accel(shared_data):
    def signal_handler(sig, frame):
        print("Stop accel")
        stop()
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal_handler)

    time.sleep(2)  # センサープロセスが先に開始するのを待つ
    copy_data = [0, 0, 0, 0, 0]

    try:
        while True:
            copy_data[0] = shared_data[0]  # front_left
            copy_data[1] = shared_data[1]  # front
            copy_data[2] = shared_data[2]  # front_right
            copy_data[3] = shared_data[3]  # left_front
            copy_data[4] = shared_data[4]  # left_back
            setting(copy_data)
    except KeyboardInterrupt:
        stop()
        GPIO.cleanup()
