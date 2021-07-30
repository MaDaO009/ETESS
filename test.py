import numpy as np
from four_DOF_simulator import single_sailboat_4DOF_simulator
import four_DOF_simulator_v2
import random
from time import time
true_wind=[2,0]
my_boat1=single_sailboat_4DOF_simulator(true_wind=true_wind)

v=0
u=0
p=0
r=0
y=0
x=0
roll=0
yaw=0
true_sail=0
rudder=0
location_and_orientation=[0,0,0,0]
v_and_angular_v=[0,0,0,0]
start_time=time()
for i in range(10000):
    
    true_sail=random.random()
    rudder=random.random()/2
    
    v_and_angular_v,location_and_orientation=my_boat1.step(location_and_orientation,v_and_angular_v,true_sail,rudder, true_wind)
    

    # print([x,y,roll,yaw])
    # print(location_and_orientation)
    # print("")

print(time()-start_time)