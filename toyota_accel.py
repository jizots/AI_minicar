import time
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import Adafruit_PCA9685
import toyota_steering as steer
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

# 前進最高速、停止、後進最高速のPWM値
pwm_forward = 310
pwm_back = 420
pwm_stop = 380

PULSE_STRAIGHT = 390
PULSE_RIGHT = 440
PULSE_LEFT = 310
sleeping = 0.01
D = 0

# moving forward ~371
# moving backward 390~
# stop 372~389

CHANNEL_ACCEL = 1
CHANNEL_SENSOR_TRIG = 32
CHANNEL_SENSOR_ECHO = 31

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

def moving_forward(a_time):
	print('moving_forward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(CHANNEL_ACCEL, 0, pwm_forward)
	# a_sleep秒間続ける
	time.sleep(a_time)

def moving_backward(a_time):
	print('moving_backward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(CHANNEL_ACCEL, 0, pwm_back)
	# a_sleep秒間続ける
	time.sleep(a_time)

def stop():
	print('stop')
	# タイヤを停止させる
	pwm.set_pwm(CHANNEL_ACCEL, 0, pwm_stop)

def	main():
	steer.steer_straight(PULSE_STRAIGHT, sleeping)
	init_sensor(CHANNEL_SENSOR_TRIG, CHANNEL_SENSOR_ECHO)
	while True:
		measure_the_distance(CHANNEL_SENSOR_TRIG, CHANNEL_SENSOR_ECHO)
		print(D)
		if D > 15:
			steer.steer_left(PULSE_LEFT, sleeping)
			moving_forward(0.01)
		else:
			break
	 #moving_forward(2)
	moving_backward(0.01)
	stop()
	steer.steer_straight(PULSE_STRAIGHT, sleeping)
	GPIO.cleanup()

if __name__ == "__main__":
    main()
