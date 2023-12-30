from machine import Pin, ADC, PWM
from time import sleep
import math

# Pin Configuration
LDR = ADC(Pin(26,Pin.IN))
# led1 = Pin(1,Pin.OUT)
Btn = Pin(19,Pin.IN)
PIR = Pin(10,Pin.IN)
buzzer = PWM(Pin(1,Pin.OUT))
ppm = ADC(Pin(27))


# Variable Configuration
PPMStartValue = 0
PPMValue = 0
PPMRange = 0
i = 0
interrupt_flag=0

# Function Configuration
def callback(pin):
    global interrupt_flag
    interrupt_flag=1
    buzzer.duty_u16(int(65536*0.2))
    buzzer.freq(784)
    print("Interrupt has occured") # CHANGE THIS TO SEND NOTIFICATION ON HTTP
    sleep(2)
    buzzer.duty_u16(int(65536*0))
    interrupt_flag=0
    
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def Light_Sys(ldrVal):
    LDR_Thres = 50000 # confLDR is the configuration done by user on http (if possible) # 65535 is the max value of analog pin
    if ((ldrVal < LDR_Thres) or Btn.value() == 1):
        return 1
    else:
        return 0

def Time_Sys():
    global PPMValue
    if (PPMValue < 432):
        PPMValue = 432
    if (PPMValue > 65375):
        PPMValue = 65375
    mappedValue = _map(PPMValue, 432, 65375, 0, 1440)
    Hr = math.floor(mappedValue/60)
    Min = math.floor(((mappedValue/60) % 1) *60)
    return Hr, Min

def Motion_Detection():
    buzzer.duty_u16(int(65536*0.2))
    buzzer.freq(784)
    print("Interrupt has occured") # CHANGE THIS TO SEND NOTIFICATION ON HTTP
    sleep(0.5)
    buzzer.duty_u16(int(65536*0))
    interrupt_flag=0
    
#PIR.irq(trigger=Pin.IRQ_RISING, handler=callback)
#while True:
    #Time = Time_Sys()
    #if interrupt_flag is 1:
        #Motion_Detection()
        #break
    #Light_Sys(500)
#     Light_Sys(# if possible to add configuration on http then add here)
