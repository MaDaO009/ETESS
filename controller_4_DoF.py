"""
Updated on FRI DEC 29 13:56:39 2018

@author: Zeyuan Feng

@contributor: fahah & Lianxin Zhang

*Get the command from sailboat object.
*Execute the command
*Update the global values
"""

import time
import globalvar as gl
from sailboat_v3 import sailboat
import math
import serial 
import re



def send(ser,rudder,sail,heading_angle):
    rudder_output=75-rudder*69
    # print(rudder_output)
    sail_output=int(sail*50+20)
    # if math.sin(heading_angle-math.pi/2)>0:
    #     sail_output=35+(sail_output-35)*9/8
    command=rudder_output//1*100+sail_output
    # print(sail_output,command)
    command=(',,'+str(command)+',').encode(encoding='utf-8')
    # ser.write(command)

#-------------Receiving Commands-----------------
def run(ser):
    # print('!')
    #-----------ESC Configuration----------------------
    
    # ser=gl.get_value('ser')
    # gl.set_value('x',2)
    # gl.set_value('y',2)
    gl.set_value('flag',False)
    rudder=0
    sail=0

    
    
    my_boat=sailboat(runtimes=3000,target=[3.2,5.5],area=[1.4,2.6],position=[0.5,1.5,0,0])
    target=my_boat.target
    gl.set_value('target',target)
    times=0
    last_rudder_value=0
    last_sail_value=0
    while True:
        times=(times+1)%10
        # get_message(ser)
        if my_boat.flag==True:
            gl.set_value('flag',True)
            print('Program stops!')
            break

        ## change the frequency of communication when the sailboat arrives at its target area
        # if my_boat.if_keeping==True:
        #     gl.set_value('frequency',20)
        # else:
        #     gl.set_value('frequency',10)

        # frequency=gl.get_value('frequency')
        frequency=10
        ##get information of sailboat
        x=gl.get_value('ob_x')
        y=gl.get_value('ob_y')
        heading_angle=gl.get_value('heading_angle')
        roll=gl.get_value('roll')
        my_boat.frequency=frequency
        # print(gl.get_value('true_wind'))
        rudder,sail,desired_angle,point_list=my_boat.update_state(gl.get_value('true_wind'),[x,y,roll,heading_angle])
        # print('sail',sail)
        
        if gl.get_value('keyboard_flag'):
            rudder=gl.get_value('rudder')
            sail=gl.get_value('sail')
        v=my_boat.velocity[0]
        u=my_boat.velocity[1]
        p=my_boat.velocity[2]
        w=my_boat.velocity[3]
        # tacking_angle=my_boat.tacking_angle
        keeping_state=my_boat.keeping_state
        
        ##control the rudder and sail
        
        rudder= float('{0:.2f}'.format(rudder))
        sail= float('{0:.2f}'.format(sail))
        send(ser,rudder,sail,heading_angle)

        # print(rudder)
        last_rudder_value=rudder
        last_sail_value=sail

        #change the global variables
        gl.set_value('tacking_angle',my_boat.tacking_angle)
        # gl.set_value('v',v)
        # gl.set_value('u',u)
        # gl.set_value('p',p)
        # gl.set_value('w',w)
        gl.set_value('target_v',my_boat.target_v)
        # print(my_boat.target_v)
        # print(rudder,sail)
        # print(u,v,w)
        if gl.get_value('keyboard_flag')==False:
            gl.set_value('rudder',rudder) 
            gl.set_value('sail',sail) 
            # print(rudder,sail,'2')
        gl.set_value('desired_angle',desired_angle)
        gl.set_value('keeping_state',keeping_state)
        gl.set_value('point_list',point_list)
        
        time.sleep(1/frequency)
    
    # End the program        
    
    # send(ser,0,0,heading_angle)
    print('Motors Stopped \n')
    time.sleep(0.1)
   
 

def sign(x):
    if x>0:
        return 1
    elif x==0:
        return 0
    else:
        return -1

def get_message(ser):
    mess=0
    
    mess=ser.readline()
    mess=bytes.decode(mess)
    mess=str(mess)
    # print(mess)
    if mess!=0:
        
        mess=mess.split(',')
        # print(mess)
        a=mess[0]
        a=re.sub('\D','',a)
        voltage=mess[1]
        current=mess[2]

        
        try:    
            b=int(a)
        except:
            b=b
    
    heading_angle=b/57.32
    if heading_angle>math.pi:
        heading_angle-=math.pi*2
    
    gl.set_value('heading_angle',heading_angle)
    gl.set_value('current',current)
    gl.set_value('voltage',voltage)

    frequency=gl.get_value('frequency')
    ser.flushInput()
#    conn.close()
#    time.sleep(1)
#    print('Connection closed!')

#------------------------------------------------
