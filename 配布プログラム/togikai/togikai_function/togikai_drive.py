def ReadPWMPARAM(pwm):
    path = '/home/pi/togikai/alignment_parameter.txt'
    with open(path) as f:
        l = f.readlines()
        PWM_PARAM = ([int(l[2]),int(l[4]),int(l[6])],[int(l[9]),int(l[11]),int(l[13])])
        pwm.set_pwm(13, 0, PWM_PARAM[1][2])
        pwm.set_pwm(14, 0, PWM_PARAM[0][2])
        #print(PWM_PARAM)
    return PWM_PARAM


def Accel(PWM_PARAM,pwm,time,Duty):
    #Parameter
    THROTTLE_FORWARD_PWM = PWM_PARAM[1][0]
    THROTTLE_STOPPED_PWM = PWM_PARAM[1][1]
    THROTTLE_REVERSE_PWM = PWM_PARAM[1][2]
        
    if Duty >= 0:
        throttle_pwm = int(THROTTLE_STOPPED_PWM - (THROTTLE_STOPPED_PWM - THROTTLE_FORWARD_PWM)*Duty/100)
        pwm.set_pwm(13, 0, throttle_pwm)
    elif Duty == 0:
        pwm.set_pwm(13, 0, THROTTLE_STOPPED_PWM)
        time.sleep(0.01)
    else:
        #Need to Reverse -> Stop -> Reverse
        pwm.set_pwm(13, 0, THROTTLE_REVERSE_PWM)
        time.sleep(0.01)
        pwm.set_pwm(13, 0, THROTTLE_STOPPED_PWM)
        time.sleep(0.01)
        throttle_pwm = int(THROTTLE_STOPPED_PWM + (THROTTLE_REVERSE_PWM - THROTTLE_STOPPED_PWM)*abs(Duty)/100)
        pwm.set_pwm(13, 0, throttle_pwm)
    #print(throttle_pwm)


def Steer(PWM_PARAM,pwm,time,Duty):
    #Parameter
    STEERING_RIGHT_PWM  = PWM_PARAM[0][0]
    STEERING_CENTER_PWM = PWM_PARAM[0][1]
    STEERING_LEFT_PWM   = PWM_PARAM[0][2]
    
    #print(STEERING_RIGHT_PWM, STEERING_CENTER_PWM, STEERING_LEFT_PWM)
    
    if Duty >= 0:
        steer_pwm = int(STEERING_CENTER_PWM - (STEERING_CENTER_PWM - STEERING_RIGHT_PWM)*Duty/100)
    else:
        steer_pwm = int(STEERING_CENTER_PWM + (STEERING_LEFT_PWM - STEERING_CENTER_PWM)*abs(Duty)/100)
    pwm.set_pwm(14, 0, steer_pwm)
