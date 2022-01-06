'''
Original author: MWS
Creation date: 2021-10-20
Purpose: Serve a web page, control GPIO (Serial0)
Note: execute using "sudo python app.py", NOT "sudo flask run"!
Changes: 
Jan 04, 2022 Tidy up source code and add some diagnostic output	@michaelstreeter101
Dec 30, 2021 Implement AJAX instead of HTTP GET  @michaelstreeter101
Dec  9, 2021 Add caching   @michaelstreeter101
Dec  8, 2021 Add multiprocessing   @michaelstreeter101 
Dec  7, 2021 Add WiFi camera video as an iframe on the home page.    @michaelstreeter101
Dec  7, 2021 Initial commit  @michaelstreeter101
'''
import datetime
import time
from pysabertooth import Sabertooth
from flask import Flask, render_template, jsonify, request
import os
from multiprocessing import Process, Pipe
from flask_caching import Cache

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
See Sabertooth documentation.
'''

saber = Sabertooth('/dev/serial0', baudrate=9600, address=128, timeout=0.1)
saber.stop()

config = {
    'DEBUG': True,
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 28800 # 8 hours 
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

@app.route('/')
def index():
    now = datetime.datetime.now()
    timeString = now.strftime('%Y-%m-%d %H:%M')
    templateData = {
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
    print("Starting reader_proc()")
    p_output, p_input = pipe
    p_input.close()
    while True:
        msg = p_output.recv()
        print(f'reader_proc: {msg}')
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
    '''
    Original author: MWS
    Creation date: 20211207
    Purpose: process movement requests from the Internet. 
    Assume the input is invalid; only permit well-formed messages; 
    write a message on the pipe to call the appropriate function;
    do not simply write the input from the Internet!
    '''
    print('action(', end='')
    msg = 'invalid'
    if deviceName == 'motor':
        print('motor, ', end='')
        match action:
            case 'stop':
                # NB: stop right now, do not put a message on the pipe.
                saber.stop()
                msg = 'stop'
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
                # NB: shutdown immediately
                shutdown() # exit point
        if msg != 'invalid':
            print(f'{msg})')
            p_input.send(msg)
        return jsonify(result='OK')

def forward():
    print('forward()')
    saber.driveBoth(-16, -16)
    time.sleep(1)
    saber.stop()

def backward():
    print('backward()')
    saber.driveBoth(16, 16)
    time.sleep(1)
    saber.stop()

def clockwise():
    print('clockwise()')
    saber.drive(1, 16)
    saber.drive(2, -16)
    time.sleep(1)
    saber.stop()

def anticlockwise():
    print('anticlockwise()')
    saber.drive(1, -16)
    saber.drive(2, 16)
    time.sleep(1)
    saber.stop()

def right():
    print("right()")
    saber.drive(1, -16)
    saber.drive(2, -36)
    time.sleep(3)
    saber.stop()

def left():
    print('left()')
    saber.drive(1, -36)
    saber.drive(2, -16)
    time.sleep(3)
    saber.stop()

def shutdown():
    print('Shutting down...')
    saber.stop()
    os.system('sudo shutdown -P now')

if __name__ == '__main__' or __name__ == 'app':
    print(f'Starting {__name__=}')

    # Create a separate process to drive the robot.
    p_output, p_input = Pipe()
    reader_p = Process(target=reader_proc, args=((p_output,p_input),))
    reader_p.daemon = True
    reader_p.start()

    # this process serves the web page.
    if __name__ == '__main__':
        app.run(host='192.168.0.45', port=80, debug=True)
