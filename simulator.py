import four_DOF_simulator_v2
import globalvar as gl
import math
import time
import random

simulation_frequency=100

def sign(p):
    
    if p>0:
        return 1
    elif p==0:
        return 0
    else:
        return -1

def moving_sail(sail,current_sail):
        
    try:
        if abs(sail-current_sail)>1/simulation_frequency:
            current_sail+=sign(sail-current_sail)*1/simulation_frequency
            # print('moving sail')
    except:
        print('an exception occurred when moving sail')
    return current_sail

def get_true_sail(sail,app_wind):
    
    if math.sin(app_wind[1])>0:
        sail=-sail
    # print([app_wind,sail])
    if math.cos(app_wind[1]+math.pi)>math.cos(sail) or abs(app_wind[1]-sign(app_wind[1])*math.pi-sail)<0.02:
        sail=app_wind[1]-sign(app_wind[1])*math.pi

    return sail

def get_app_wind(true_wind,v,u,heading_angle):
        
        ###this part is different from the paper since there might be something wrong in the paper
        ###get coordinates of true wind
        
        app_wind=[true_wind[0]*math.cos(true_wind[1]-heading_angle)-v,
                        true_wind[0]*math.sin(true_wind[1]-heading_angle)-u]
        ###convert into polar system
        angle=math.atan2(app_wind[1],app_wind[0])
        app_wind=[math.sqrt(pow(app_wind[1],2)+pow(app_wind[0],2)),angle]
        return app_wind

s_frame_true_wind=[1.5,math.pi]
def run():
    counter=0
    while True:
        counter+=1
        if gl.get_value('flag'):
            break
        sail=gl.get_value("sail")
        rudder=gl.get_value("rudder")
        v=gl.get_value("v")
        u=gl.get_value("u")
        p=gl.get_value("p")
        w=gl.get_value("w")
        x=gl.get_value("x")
        y=gl.get_value("y")
        roll=gl.get_value("roll")
        heading_angle=gl.get_value('heading_angle')
        true_wind=gl.get_value("true_wind")
        # true_wind[1]+=0.001
        gl.set_value('true_wind',true_wind)
        

        current_sail=gl.get_value('current_sail')
        current_sail=moving_sail(sail,current_sail)

        app_wind=get_app_wind(true_wind,v,u,heading_angle)
        true_sail=get_true_sail(current_sail,app_wind)
        # print(true_sail,app_wind[1],"ttttssss")
        # print([u,v,p,w],[x,y,roll,heading_angle],111)
        s_frame_true_wind[1]=math.pi/2-true_wind[1]
        a,b,app_wind[1]=four_DOF_simulator_v2.to_next_moment(1/simulation_frequency,v,-u,-p,-w,y,x,-roll,math.pi/2-heading_angle,true_sail,rudder,s_frame_true_wind,counter)
        [v,u,p,w]=-a
        
        # print(app_wind)
        app_wind[1]=-app_wind[1]
        v*=-1

        [y,x,roll,heading_angle]=b
        roll=-roll
        heading_angle=math.pi/2-heading_angle
        
        gl.set_value("current_sail",current_sail)
        gl.set_value("v",v)
        gl.set_value("u",u)
        gl.set_value("p",p)
        gl.set_value("w",w)
        gl.set_value("x",x)
        gl.set_value('ob_x',x+random.random()*0.03)
        gl.set_value("y",y)
        gl.set_value('ob_y',y+random.random()*0.03)
        gl.set_value("roll",roll)
        gl.set_value("heading_angle",heading_angle)
        gl.set_value("app_wind",app_wind)
        # print('simulating')
        time.sleep(0.01)
   