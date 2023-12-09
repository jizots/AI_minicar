import time
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(60)

# 前進最高速、停止、後進最高速のPWM値
pwm_forward = 360
pwm_back = 420
pwm_stop = 372

# moving forward ~ 371
# moving backward 390 ~
# stop 372~389

def moving_forward(a_time):
	print('moving_forward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(1, 0, pwm_forward)
	# １秒間続ける
	time.sleep(a_time)

def moving_backward(a_time):
	print('moving_backward')
	# ====  １秒間まっすぐ進む  ====
	# タイヤを前進方向に回転させる
	pwm.set_pwm(1, 0, pwm_back)
	# １秒間続ける
	time.sleep(a_time)

def stop(a_time):
	print('stop')
	# タイヤを停止させる
	pwm.set_pwm(1, 0, pwm_stop)

def	main():
    moving_forward(2)
    moving_backward(2)
    stop(2)

if __name__ == "__main__":
    main()
