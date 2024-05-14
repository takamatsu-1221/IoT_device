import time
import network
import socket
import _thread
from machine import Pin,PWM

led = Pin("LED", machine.Pin.OUT)
servo=PWM(Pin(0))
servo.freq(50)
sw = Pin(1, Pin.IN, Pin.PULL_DOWN)

heater_state = 'heater is off'

ssid = 'rt500m-8596f9-1'
password = 'bd69993feae8c'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
    <html lang='ja'>
    <head>
    <meta charset=\"utf-8\">
    
    <title>Heater control system</title>
    
    </head>
    <body>

    <center>
        <h1>Welcome to Myroom Heater control system!</h1>
    </center>

    <br>

    <center>
    <p>
        <a href=\"/?heater=on\">Heater ON</a>
    </p>
    </center>

    <center>
    <p>
        <a href=\"/?heater=off\">Heater OFF</a>
    </p>
    </center>

    <center>
    </form>
    <br><br><br>
    <p>%s<p>
    </center>
    
    </body>
    </html>
"""


def main():
    led.value(1)
    heatOff()
    server_connect()
    for n in range(10):
        led.value(1)
        time.sleep(0.05)
        led.value(0)
        time.sleep(0.05)
    server_control()

def server_connect():
    global s,stateis,heat_state
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('listening on', addr)


def server_control():
    global s,stateis,heat_state
    while True:
        try:
            cl, addr = s.accept()
            #print('client connected from', addr)
            request = cl.recv(1024)
            request = str(request)
            led_on = request.find('heater=on')
            led_off = request.find('heater=off')
        
            if led_on == 8:
                heatOn()
            if led_off == 8:
                heatOff()
        
            stateis = heat_state
            response = html % stateis
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
        
        except OSError as e:
            cl.close()
            print('connection closed')


def servo_value(degree):
    return int((degree * 9.5 / 180 + 2.5) * 65535 / 100)

#button control
def callback(p):
    global heat_state
    time.sleep(0.03)
    sw_state = sw.value()
    if sw_state==1:
        if heat_state =="heater is on":
            heatOff()
        else:
            heatOn()
        while True:
            time.sleep(0.01)
            sw_state = sw.value()
            if sw_state==0:
                break
            else:
                None
    else:
        None

def heatOn():
    global heat_state
    servo.duty_u16(servo_value(110))
    led.value(1)
    heat_state = "heater is on"
    
def heatOff():
    global heat_state
    servo.duty_u16(servo_value(50))
    led.value(0)
    heat_state = "heater is off"

      

sw.irq(trigger=Pin.IRQ_RISING , handler = callback)
if __name__=="__main__":
    main()






