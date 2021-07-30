"""
Created on FRI DEC 28 14:29:21 2018

@author: Zeyuan Feng

@contributor: fahah & Lianxin Zhang

Main program for station keeping. 
"""


import time
import math
import globalvar as gl
import threading
import controller_4_DoF

import data_writer
import simulator
# import plot
import serial
import visualization
import keyboard_control
# import matplotlib.pyplot as plt


if __name__ == "__main__":
    # ser=serial.Serial('COM3',57600)
    ser=0

    gl.set_value('flag',False) # Stop sign
    gl.set_value('ob_x',0)
    gl.set_value('ob_y',0)
     # initial heading angle zero
    gl.set_value('desired_angle',0)
    gl.set_value('sail',0) 
    gl.set_value('rudder',0)
    gl.set_value('frequency',10)
    gl.set_value('true_wind',[7.5,-math.pi/2])
    gl.set_value('target',[0,0]) 
    gl.set_value('x',0.5)
    gl.set_value('y',1.5)
    gl.set_value('roll',0)
    gl.set_value('heading_angle',0)
    gl.set_value('keeping_state',1)
    gl.set_value('tacking_angle',None)
    gl.set_value('current',0)
    gl.set_value('voltage',0)
    gl.set_value('keyboard_flag',False)
    gl.set_value('target_v',0.1)
    gl.set_value('current_sail',0)
    gl.set_value('v',0)
    gl.set_value('u',0)
    gl.set_value('p',0)
    gl.set_value('w',0)


    
    t1 = threading.Thread(target= controller_4_DoF.run,kwargs={'ser':ser}) # Receiving Commands
    t3 = threading.Thread(target= data_writer.run)
    t4 = threading.Thread(target= simulator.run)
    t5 = threading.Thread(target= keyboard_control.main)
    
    
    t1.start() # start thread 1
    t3.start() # start thread 3
    t4.start()
    t5.start()
    my_plot=visualization.visualazation()
    my_plot.plot()

    t1.join() # wait for the t1 thread to complete
    
    t3.join() # wait for the t3 thread to complete
    t4.join()
    t5.join()
    # ser.close()
    # conn.close()
    time.sleep(1)
    print('Connection closed!')
    
 