import os
import sys
sys.path.append('/home/pi/togikai/togikai_function/')
import togikai_ultrasonic
import signal
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np#障害物センサ測定関数

GPIO.setmode(GPIO.BOARD)
#初期設定
t_list=[15,13,35,32,36]
GPIO.setup(t_list,GPIO.OUT,initial=GPIO.LOW)
e_list=[26,24,37,31,38]
GPIO.setup(e_list,GPIO.IN)

#データ記録用配列作成
d = np.zeros(2)
# print('Input test name')
# test = input()
# print('Input No.')
# testno = input()
# filename = '/home/pi/code/record_data/'+str(test)+str(testno)+'.csv'
start_time = time.time()

if __name__ == "__main__":
    try:
        for i in range(100):
            dis = togikai_ultrasonic.Mesure(GPIO,time,15,26)
            #距離データを配列に記録
            d = np.vstack([d,[time.time()-start_time, dis]])
            print('{0:.2f}'.format(dis))
            time.sleep(0.1)
        GPIO.cleanup()
        # np.savetxt(filename, d, fmt='%.3e')
        print('average = ', np.mean(d[:,1]))

    except KeyboardInterrupt:
        # np.savetxt(filename, d, fmt='%.3e')
        print('stop!')
        GPIO.cleanup()
