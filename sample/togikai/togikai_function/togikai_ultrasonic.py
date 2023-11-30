#障害物センサ測定関数
def Mesure(GPIO,time,trig,echo):
    dis = 0
    n = 1
    for i in range(n):
        sigoff = 0
        sigon = 0
        GPIO.output(trig,GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trig,GPIO.LOW)
        kijyun=time.time()
        while(GPIO.input(echo)==GPIO.LOW):
            sigoff=time.time()
            if sigoff - kijyun > 0.02:
            #     print("break1")
                 break
        while(GPIO.input(echo)==GPIO.HIGH):
            sigon=time.time()
            if sigon - sigoff > 0.02:
            #     print("break2")
                 break
        d = (sigon - sigoff)*34000/2
        if d > 200:
            dis += 200/n
        else:
            dis += d/n
    return dis
