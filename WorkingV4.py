from machine import Pin, ADC, PWM
import network
import usocket as socket
import time
import Systems
import math

# Pin configuration
led1 = machine.Pin(22, machine.Pin.OUT) # Living Room Light
led2 = machine.Pin(12, machine.Pin.OUT) # Bedroom Light
led3 = machine.Pin(16, machine.Pin.OUT) # Kitchen Light
led4 = Pin(15, Pin.OUT)					# Toilet Light
ledAlrm = Pin(4, Pin.OUT)
pir = machine.Pin(18, machine.Pin.IN)
vib = Pin(17,Pin.IN)
buzzer = PWM(Pin(1,Pin.OUT))
btn = Pin(19, Pin.IN)
ldr = ADC(Pin(28, Pin.IN))



# Declaration of State Global Variables
state = 0
led1State = 0
stateStr = "Unarm"
interrupt = 0
start_time = 0

#System interrupt handler
def callback(pin):
    global interrupt, start_time
    interrupt = 1
    start_time = time.time()

# To read HTML file
def get_html(html_name):
    # open html_name (index.html), 'r' = read-only as variable 'file'
    with open(html_name, 'r') as file:
        html = file.read()
    return html
        
def toggle_led(led, state):
    led.value(state)
    
def allOn():
    led1.value(1)
    led2.value(1)
    led3.value(1)
    led4.value(1)

def allOff():
    led2.value(0)
    led3.value(0)
    led4.value(0)

def handle_client(client_socket):
    request = client_socket.recv(1024)
    request_str = str(request)
    global stateStr
    global state
    global interrupt
    global led1State
    
    # To check the alarm arm state
    if "GET /arm/on" in request_str:
        state = 1
        stateStr = "Arm"
    elif "GET /arm/off" in request_str:
        state = 0
        interrupt = 0
        stateStr = "Unarm"
    elif "GET /panic" in request_str:
        state = 2
        stateStr = "Panic"
    elif "GET /kill" in request_str:
        state = 0
        interrupt = 0
        stateStr = "Unarm"
    
    # To check the light state
    if "GET /led1/on" in request_str:
        led1State = 1
        led1.value(led1State)
    elif"GET /led1/off" in request_str:
        if ldr.read_u16()>50000:
            led1State = 0
            led1.value(led1State)
        led1State = 0
    elif "GET /led2/on" in request_str:
        led2.value(1)
    elif"GET /led2/off" in request_str:
        led2.value(0)
    elif "GET /led3/on" in request_str:
        led3.value(1)
    elif"GET /led3/off" in request_str:
        led3.value(0)
    elif "GET /led4/on" in request_str:
        led4.value(1)
    elif"GET /led4/off" in request_str:
        led4.value(0)
    elif "GET /all/on" in request_str:
        led1State = 1
        allOn()
    elif"GET /all/off" in request_str:
        if ldr.read_u16()>50000:
            led1State = 0
            led1.value(led1State)
        led1State = 0
        allOff()
        
    html = get_html("index.html")

    response = html % stateStr
    client_socket.send(response)
    client_socket.close()

def alarmTriggered(client_socket):
    request = client_socket.recv(1024)
    request_str = str(request)
    global stateStr
    global state
    global interrupt
    global led1State
    
    if "GET /arm/on" in request_str:
        state = 1
        stateStr = "Arm"
    elif "GET /arm/off" in request_str:
        state = 0
        interrupt = 0
        stateStr = "Unarm"
    elif "GET /panic" in request_str:
        state = 2
        stateStr = "Panic"
    elif "GET /kill" in request_str:
        state = 0
        interrupt = 0
        stateStr = "Unarm"
        
    html = get_html("triggered.html")

    response = html
    client_socket.send(response)
    client_socket.close()
    
ssid = "Ngoo Wifi"
password = "zmwifi888"

# To set up the Wifi connection
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid,password)

while not wifi.isconnected():
    pass

ipAddress = wifi.ifconfig()[0]
if ipAddress:
    print("Web server is running at http://{}".format(ipAddress))
else:
    print("failed to retrieve the IP address. Check your Wi-Fi settings and connection.")

server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ipAddress, 80))
server.listen(5)

pir.irq(trigger=Pin.IRQ_RISING, handler=callback)
vib.irq(trigger=Pin.IRQ_RISING, handler = callback)
while True:
    if (time.time() - start_time > 2 and interrupt == 1):
        buzzer.duty_u16(int(65536*0))
        interrupt=0
        state = 0
        stateStr = "Unarm"
        print("alarm off")
    print("7")
    client_socket, addr = server.accept()
    print("8")
    if state == 1 and interrupt == 1:
        alarmTriggered(client_socket)
    else:
        handle_client(client_socket)
    print("State = " , state)
    print("PIR VAL: " + str(pir.value()))
    if state == 0:
        buzzer.duty_u16(int(65536*0))
        ledAlrm.value(0)
    elif state == 1 and interrupt == 1:
        Systems.Motion_Detection()
        ledAlrm.value(1)
    elif state == 2:
        buzzer.duty_u16(int(65536*0.2))
        buzzer.freq(784)
        ledAlrm.value(1)
    if led1State == 0:
        led1.value(Systems.Light_Sys(ldr.read_u16()))
    print("last")