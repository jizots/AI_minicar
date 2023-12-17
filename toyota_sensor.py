import time
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

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
#	if d > 200:
#		print("forward_sensor:ok!\n")