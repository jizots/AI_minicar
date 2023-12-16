import time
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

# 前進最高速、停止、後進最高速のPWM値
pwm_forward = 360
pwm_back = 420
pwm_stop = 372

# moving forward ~371
# moving backward 390~
# stop 372~389

accel_pin = 1
forward_sensor_trig_pin = 3
forward_sensor_echo_pin = 4

def init_sensor(trig_pin, echo_pin):
    # GPIOピン番号の指示方法
	GPIO.setmode(GPIO.BOARD)
	#超音波センサ初期設定
	GPIO.setup(trig_pin,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(echo_pin,GPIO.IN)

def measure_the_distance(trig_pin, echo_pin):
	sigon = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
	sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
	GPIO.output(trig_pin,GPIO.HIGH) #Trigピンの電圧をHIGH(3.3V)にする
	time.sleep(0.00001) #10μs待つ
	GPIO.output(trig_pin,GPIO.LOW) #Trigピンの電圧をLOW(0V)にする
	while(GPIO.input(echo_pin)==GPIO.LOW):
		sigon=time.time() #Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
	while(GPIO.input(echo_pin)==GPIO.HIGH):
		sigoff=time.time() #Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
	d = (sigoff - sigon)*34000/2 #距離を計算(単位はcm)
	if d > 200:
		return (True)
	print(d) #距離を表示する

def moving_forward(a_time):
	print('moving_forward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(accel_pin, 0, pwm_forward)
	# a_sleep秒間続ける
	time.sleep(a_time)

def moving_backward(a_time):
	print('moving_backward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(accel_pin, 0, pwm_back)
	# a_sleep秒間続ける
	time.sleep(a_time)

def stop():
	print('stop')
	# タイヤを停止させる
	pwm.set_pwm(accel_pin, 0, pwm_stop)

def	main():
	init_sensor(forward_sensor_trig_pin, forward_sensor_echo_pin)
	if (measure_the_distance(forward_sensor_trig_pin, forward_sensor_echo_pin)):
		moving_forward(1)
	# moving_forward(2)
	# moving_backward(2)
	stop()

if __name__ == "__main__":
    main()
