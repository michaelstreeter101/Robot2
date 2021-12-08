'''
Original author: MWS
Creation date: 2021-10-20
Purpose: Serve a web page, control GPIO (Serial0)
'''
import datetime
import time
from pysabertooth import Sabertooth
from flask import Flask, render_template
import os
from multiprocessing import Process, Pipe

'''
Packetized Serial (Down, Down, Up, Up, Up, Up) uses TTL level 
multi-byte serial commands to set the motor speed and direction. 
Packetized serial is a one-direction only interface. The transmit line 
from the host is connected to S1. The host's receive line is not 
connected to the Sabertooth. 
If using a true RS-232 device like a Raspberry Pi GPIO14 UART_TXD0, 
it is necessary to use a level converter to shift the -3V Raspberry Pi 
levels to the 0v-5v TTL levels the Sabertooth is expecting. 
Packetized serial uses an address byte to select the target device. 
See documentation.
'''

#import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# LED = 2
# GPIO.setup(LED, GPIO.OUT)
# GPIO.output(LED, GPIO.LOW)
# import serial

saber = Sabertooth('/dev/serial0', baudrate=9600, address=128, timeout=0.1)
saber.stop()

app = Flask(__name__)
@app.route('/')

def hello():
    now = datetime.datetime.now()
    timeString = now.strftime('%Y-%m-%d %H:%M')
    templateData = {
        'title' : 'Patrol Robot',
        'time': timeString
    }
    return render_template('index.html', **templateData)

def reader_proc(pipe):
    '''
    Original author: MWS
    Creation date: 20211207
    Purpose: to improve performance, the reader_proc will spawn in 
    a different process and read messages off a pipe. 
    Commands will be sent to the Sabertooth asyncronously and 
    independently from the process running the flask web page front end.
    '''
    p_output, p_input = pipe
    p_input.close()
    while True:
        msg = p_output.recv()
        print(msg)
        match msg:
            case 'forward':
                forward()
            case 'anticlockwise':
                anticlockwise()
            case 'clockwise':
                clockwise()
            case 'left':
                left()
            case 'right':
                right()
            case 'backward':
                backward()
            case 'shutdown':
                break
    
@app.route('/<deviceName>/<action>')
def action(deviceName, action):
    msg = 'DONE'
    if deviceName == 'motor':
        match action:
            case 'stop':
                print('saber.stop()')
                saber.stop()
            case 'forward':
                msg = 'forward'
            case 'anticlockwise':
                msg = 'anticlockwise'
            case 'clockwise':
                msg = 'clockwise'
            case 'left':
                msg = 'left'
            case 'right':
                msg = 'right'
            case 'backward':
                msg = 'backward'
            case 'shutdown':
                shutdown()
        p_input.send(msg)
           
               
#      actuator = LED
#      print(f'{actuator}')
#   else:
#      actuator = 2
   
#   if action == 'on':
#      GPIO.output(actuator, GPIO.HIGH)
#   if action == 'off':
#      GPIO.output(actuator, GPIO.LOW)

    now = datetime.datetime.now()
    timeString = now.strftime('%Y-%m-%d %H:%M')

    templateData = {
        'title' : 'Patrol Robot',
        'time': timeString
    }
    return render_template('index.html', **templateData)

def forward():
    print("function forward")
    saber.driveBoth(-16, -16)
    time.sleep(1)
    saber.stop()


def backward():
    print("function backward")
    saber.driveBoth(16, 16)
    time.sleep(1)
    saber.stop()


def clockwise():
    print("function clockwise")
    saber.drive(1, 16);
    saber.drive(2, -16);
    time.sleep(1)
    saber.stop()

def anticlockwise():
    print("function anticlockwise")
    saber.drive(1, -16);
    saber.drive(2, 16);
    time.sleep(1)
    saber.stop()

def right():
    print("function right")
    saber.drive(1, -16);
    saber.drive(2, -36);
    time.sleep(3)
    saber.stop()

def left():
    print("function left")
    saber.drive(1, -36);
    saber.drive(2, -16);
    time.sleep(3)
    saber.stop()

def shutdown():
    print('Shutting down...')
    os.system("sudo shutdown -P now")
    
# /*
# stop
# forward
# back
# clockwise rotation
# anticlockwise rotation
# right corner
# left corner
# */
  
if __name__ == '__main__':
    print('__main__')
    p_output, p_input = Pipe()
    reader_p = Process(target=reader_proc, args=((p_output,p_input),))
    reader_p.daemon = True
    reader_p.start()
    app.run(host='0.0.0.0', port=80, debug=True)
