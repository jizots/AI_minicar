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
    TRIG_LF = 37
    ECHO_LF = 40
    TRIG_LB = 33
    ECHO_LB = 36

# 一応残してるけど消すかも
D = 0
CHANNEL_SENSOR_TRIG_FL = 15
CHANNEL_SENSOR_ECHO_FL = 26
CHANNEL_SENSOR_TRIG_F = 13
CHANNEL_SENSOR_ECHO_F = 24
CHANNEL_SENSOR_TRIG_FR = 32
CHANNEL_SENSOR_ECHO_FR = 31
CHANNEL_SENSOR_TRIG_LF = 37
CHANNEL_SENSOR_ECHO_LF = 40
CHANNEL_SENSOR_TRIG_LB = 33
CHANNEL_SENSOR_ECHO_LB = 36

def init_sensor(trig, echo):
    # GPIOピン番号の指示方法
	GPIO.setmode(GPIO.BOARD)
	# 超音波センサ初期設定
	# print(trig)
	# print(echo)
	GPIO.setup(trig,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(echo,GPIO.IN)

### ここからプログラム単体テスト用
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
    elif echo == CHANNEL_SENSOR_ECHO_LF:
        print("LF")
    elif echo == CHANNEL_SENSOR_ECHO_LB:
        print("LB")
    print(D)
#       if d > 200:
#               print("forward_sensor:ok!\n")
    time.sleep(1)

def main():
    print("Test mode")
    init_sensor(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
    init_sensor(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
    init_sensor(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
    init_sensor(CHANNEL_SENSOR_TRIG_LF, CHANNEL_SENSOR_ECHO_LF)
    init_sensor(CHANNEL_SENSOR_TRIG_LB, CHANNEL_SENSOR_ECHO_LB)
    while True:
        measure_the_distance(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
        measure_the_distance(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
        measure_the_distance(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
        measure_the_distance(CHANNEL_SENSOR_TRIG_LF, CHANNEL_SENSOR_ECHO_LF)
        measure_the_distance(CHANNEL_SENSOR_TRIG_LB, CHANNEL_SENSOR_ECHO_LB)
    GPIO.cleanup()

if __name__ == "__main__":
    main()
### ここまでプログラム単体テスト用

def measure_distance(trig, echo, shared_data, sensor_id):
    while True:
        try:
            with lock:
                GPIO.output(trig, GPIO.HIGH) #ultrasonicを発信
                time.sleep(0.00001)
                GPIO.output(trig, GPIO.LOW) #ultrasonicを停止
                sigon = time.time()
                while GPIO.input(echo) == GPIO.LOW: #反射したultrasonicを受信するまで待機
                    if time.time() - sigon > 0.01:  # 10msを超えたらタイムアウト
                        raise RuntimeError("Echo signal timeout (LOW)")
                sigoff = time.time()
                while GPIO.input(echo) == GPIO.HIGH: #反射したultrasonicの末端が来るのを待つ
                    if time.time() - sigoff > 0.01:  # 10msを超えたらタイムアウト
                        raise RuntimeError("Echo signal timeout (HIGH)")
                distance = (sigoff - sigon) * 34000 / 2
                shared_data[sensor_id] = round(distance)
        except RuntimeError as e:
            print(f"Error with sensor {sensor_id}: {e}")
            # エラーがあった場合は値を変更しない
            time.sleep(0.1)  # 一定時間待ってから再試行
        except Exception as e:
            print(f"Unexpected error with sensor {sensor_id}: {e}")
            break  # 予期せぬエラーが発生した場合、ループを終了

        time.sleep(0.1)  # 正常な測定の間隔


# main.pyから呼び出される関数
def sensor(shared_data):
    # センサーの初期設定
    init_sensor(SensorChannel.TRIG_FL.value, SensorChannel.ECHO_FL.value)
    init_sensor(SensorChannel.TRIG_F.value, SensorChannel.ECHO_F.value)
    init_sensor(SensorChannel.TRIG_FR.value, SensorChannel.ECHO_FR.value)
    init_sensor(SensorChannel.TRIG_LF.value, SensorChannel.ECHO_LF.value)
    init_sensor(SensorChannel.TRIG_LB.value, SensorChannel.ECHO_LB.value)

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
                texec.submit(measure_distance, SensorChannel.TRIG_LF.value, SensorChannel.ECHO_LF.value, shared_data, sensor_id)
            elif sensor_id == 4:
                texec.submit(measure_distance, SensorChannel.TRIG_LB.value, SensorChannel.ECHO_LB.value, shared_data, sensor_id)
