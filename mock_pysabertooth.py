'''
Mock Sabertooth - for development on Macbook
Original author: MWS
'''
class Sabertooth:
    def __new__(cls, a, baudrate, address, timeout):
        print("__new__()")
        inst = object.__new__(cls)
        return inst
    
    def __init__(self, a, baudrate, address, timeout):
        print("__init__()")
        self.a = a
        self.baudrate = baudrate
        self.address = address
        self.timeout = timeout

    def drive(self, a, b):
        return
    def driveboth(self, a, b):
        return
    def stop(self):
        return
