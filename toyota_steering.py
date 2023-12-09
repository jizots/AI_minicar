import Adafruit_PCA9685
import time

CHANNEL_STEER = 14
PULSE_STRAIGHT = 1
PULSE_LEFT = 1
PULSE_RIGHT = 1

def steer_straight(pulse, sleep_time):
    print('steer_straight')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_left(pulse, sleep_time):
    print('steer_left')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def steer_right(pulse, sleep_time):
    print('steer_right')
    pwm.set_pwm(CHANNEL_STEER, 0, pulse)
    time.sleep(sleep_time)

def	main():
    steer_straight(PULSE_STRAIGHT, 0)
    steer_left(PULSE_LEFT, 0)
    steer_straight(PULSE_STRAIGHT, 0)
    steer_right(PULSE_RIGHT, 0)
    steer_left(PULSE_LEFT, 0)
    steer_right(PULSE_RIGHT, 0)
    steer_straight(PULSE_STRAIGHT, 0)

if __name__ == "__main__":
    main()