from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import time
import threading
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール

# Lockオブジェクトの初期化
lock = threading.Lock()

# タイムアウトまでの時間（秒）
timeout_duration = 0.05

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
	GPIO.setup(trig,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(echo,GPIO.IN)

def measure_distance(trig, echo, shared_data, sensor_id):
    sigon = 0
    sigoff = 0
    distance = 0
    while True:
        with lock:
            GPIO.output(trig, GPIO.HIGH)  # ultrasonicの発信
            time.sleep(0.00001)
            GPIO.output(trig, GPIO.LOW)  # ultrasonicの発信を停止
            start_time = time.time()
            while GPIO.input(echo) == GPIO.LOW:
                sigon = time.time()
                if (time.time() - start_time) > timeout_duration:
                    print("sensor_id: " + str(sensor_id) + " sigon over limit")
                    start_time = 0
                    break
            if start_time != 0:
                while GPIO.input(echo) == GPIO.HIGH:
                    sigoff = time.time()
        if start_time != 0:
            distance = round((sigoff - sigon) * 34000 / 2)
            if distance <= 900:
                shared_data[sensor_id] = distance
            else:
                shared_data[sensor_id] = 200 # 距離の計算で大きすぎる数値は置き換える
            time.sleep(0.05)  # 測定の間隔


# main.pyから呼び出される関数
def sensor(shared_data):
    # センサーの初期設定
    init_sensor(SensorChannel.TRIG_FL.value, SensorChannel.ECHO_FL.value)
    init_sensor(SensorChannel.TRIG_F.value, SensorChannel.ECHO_F.value)
    init_sensor(SensorChannel.TRIG_FR.value, SensorChannel.ECHO_FR.value)
    init_sensor(SensorChannel.TRIG_L.value, SensorChannel.ECHO_L.value)
    init_sensor(SensorChannel.TRIG_R.value, SensorChannel.ECHO_R.value)
    # 共有データの初期化
    shared_data[0] = 60
    shared_data[1] = 60
    shared_data[2] = 60
    shared_data[3] = 60
    shared_data[4] = 60

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

