import time
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール

D = 0

CHANNEL_SENSOR_TRIG_FL = 15
CHANNEL_SENSOR_ECHO_FL = 26
CHANNEL_SENSOR_TRIG_F = 13
CHANNEL_SENSOR_ECHO_F = 24
CHANNEL_SENSOR_TRIG_FR = 32
CHANNEL_SENSOR_ECHO_FR = 3

def init_sensor(trig, echo):
    # GPIOピン番号の指示方法
	GPIO.setmode(GPIO.BOARD)
	#超音波センサ初期設定
	print(trig)
	print(echo)
	GPIO.setup(trig,GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(echo,GPIO.IN)

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
    print(D)
#       if d > 200:
#               print("forward_sensor:ok!\n")

def main():
    init_sensor(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
    init_sensor(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
    init_sensor(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
    while True:
        measure_the_distance(CHANNEL_SENSOR_TRIG_FL, CHANNEL_SENSOR_ECHO_FL)
        measure_the_distance(CHANNEL_SENSOR_TRIG_F, CHANNEL_SENSOR_ECHO_F)
        measure_the_distance(CHANNEL_SENSOR_TRIG_FR, CHANNEL_SENSOR_ECHO_FR)
    GPIO.cleanup()