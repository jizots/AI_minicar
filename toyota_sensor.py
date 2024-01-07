from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import time
import threading
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール

# Lockオブジェクトの初期化
lock = threading.Lock()

# GPIOピン番号を指定。ラズパイのピン番号。列挙体を使ってみた。
class SensorChannel(Enum):
    TRIG_FL = 15
    ECHO_FL = 26
    TRIG_F = 13
    ECHO_F = 24
    TRIG_FR = 32
    ECHO_FR = 31
    TRIG_L = 37
    ECHO_L = 40
    TRIG_R = 33
    ECHO_R = 36

def init_sensor(trig, echo):
    # GPIOピン番号の指示方法
	GPIO.setmode(GPIO.BOARD)
	# 超音波センサ初期設定
	# print(trig)
	# print(echo)
	GPIO.setup(trig,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(echo,GPIO.IN)


def measure_distance(trig, echo, shared_data, sensor_id):
    sigon = 0
    sigoff = 0
    distance = 0
    while True:
        GPIO.output(trig, GPIO.HIGH)  # ultrasonicの発信
        time.sleep(0.00001)
        GPIO.output(trig, GPIO.LOW)  # ultrasonicの発信を停止
        while GPIO.input(echo) == GPIO.LOW:
            sigon = time.time()
        while GPIO.input(echo) == GPIO.HIGH:
            sigoff = time.time()
        # 距離の計算で大きすぎる数値は無視するVer
        distance = round((sigoff - sigon) * 34000 / 2)
        if distance <= 900:
            shared_data[sensor_id] = distance
        # else:
        #     shared_data[sensor_id] = 60 # 距離の計算で大きすぎる数値は置き換えるVer
        time.sleep(0.05)  # 測定の間隔


# main.pyから呼び出される関数
def sensor(shared_data):
    # センサーの初期設定
    init_sensor(SensorChannel.TRIG_FL.value, SensorChannel.ECHO_FL.value)
    init_sensor(SensorChannel.TRIG_F.value, SensorChannel.ECHO_F.value)
    init_sensor(SensorChannel.TRIG_FR.value, SensorChannel.ECHO_FR.value)
    init_sensor(SensorChannel.TRIG_L.value, SensorChannel.ECHO_L.value)
    init_sensor(SensorChannel.TRIG_R.value, SensorChannel.ECHO_R.value)

    # スレッド化して実行
    with ThreadPoolExecutor() as texec:
        for sensor_id in range(5):
            if sensor_id == 0:
                texec.submit(measure_distance, SensorChannel.TRIG_FL.value, SensorChannel.ECHO_FL.value, shared_data, sensor_id)
            elif sensor_id == 1:
                texec.submit(measure_distance, SensorChannel.TRIG_F.value, SensorChannel.ECHO_F.value, shared_data, sensor_id)
            elif sensor_id == 2:
                texec.submit(measure_distance, SensorChannel.TRIG_FR.value, SensorChannel.ECHO_FR.value, shared_data, sensor_id)
            elif sensor_id == 3:
                texec.submit(measure_distance, SensorChannel.TRIG_L.value, SensorChannel.ECHO_L.value, shared_data, sensor_id)
            elif sensor_id == 4:
                texec.submit(measure_distance, SensorChannel.TRIG_R.value, SensorChannel.ECHO_R.value, shared_data, sensor_id)


### ここからプログラム単体テスト用
D = 0
CHANNEL_SENSOR_TRIG_FL = 15
CHANNEL_SENSOR_ECHO_FL = 26
CHANNEL_SENSOR_TRIG_F = 13
CHANNEL_SENSOR_ECHO_F = 24
CHANNEL_SENSOR_TRIG_FR = 32
CHANNEL_SENSOR_ECHO_FR = 31
CHANNEL_SENSOR_TRIG_L = 37
CHANNEL_SENSOR_ECHO_L = 40
CHANNEL_SENSOR_TRIG_R = 33
CHANNEL_SENSOR_ECHO_R = 36

def measure_the_distance(trig, echo):
    global D
    sigon = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig, GPIO.HIGH) #Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) #10μs待つ
    GPIO.output(trig, GPIO.LOW) #Trigピンの電圧をLOW(0V)にする
    while(GPIO.input(echo) == GPIO.LOW):
            sigon=time.time() #Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
    while(GPIO.input(echo) == GPIO.HIGH):
            sigoff=time.time() #Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
    D = (sigoff - sigon)*34000/2 #距離を計算(単位はcm)
    if echo == CHANNEL_SENSOR_ECHO_FL:
        print("FL")
    elif echo == CHANNEL_SENSOR_ECHO_F:
        print("F")
    elif echo == CHANNEL_SENSOR_ECHO_FR:
        print("FR")
    elif echo == CHANNEL_SENSOR_ECHO_L:
        print("L")
    elif echo == CHANNEL_SENSOR_ECHO_R:
        print("R")
    print(D)
#       if d > 200:
#               print("forward_sensor:ok!\n")
    time.sleep(1)

def main():
    print("Test mode")
    init_sensor(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
    init_sensor(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
    init_sensor(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
    init_sensor(CHANNEL_SENSOR_TRIG_L, CHANNEL_SENSOR_ECHO_L)
    init_sensor(CHANNEL_SENSOR_TRIG_R, CHANNEL_SENSOR_ECHO_R)
    while True:
        measure_the_distance(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
        measure_the_distance(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
        measure_the_distance(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
        measure_the_distance(CHANNEL_SENSOR_TRIG_L, CHANNEL_SENSOR_ECHO_L)
        measure_the_distance(CHANNEL_SENSOR_TRIG_R, CHANNEL_SENSOR_ECHO_R)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
### ここまでプログラム単体テスト用
