'''
Updated on Tue JAN 2 14:41:22 2019

@author: Zeyuan Feng


The angle is the same as a typical polar coordinate.
The positive direction of axis is 0. The range is [-pi,pi] 
To use this program, you should import the code and create a sailboat object.
Firstly, call the method update_pos(), then update_state() to get new sail and rudder commands.
'''


import math
import random
import time
from controller.pid2 import PID
from controller.rudder_controller_v2 import rudder_controller
from controller.update_info import info_updator
from controller.sail_control_v2 import sailcontroller
import controller.get_desired_angle_v2 as get_desired_angle




class sailboat:


    def __init__(self,position=[2,2,0,0],sample_time=0.1,target=[3,6],area=[1.4,2.8],
    true_wind=[3,-math.pi/2],runtimes=3100):
    ####    all the units of angles are rad 
        self.velocity=[0,0,0,0] ###[v,u,p,r], where v is the heading angle of the sailboat 
        self.desired_angle=0 
        self.tacking_angle=None
        self.tacking_sign=None
        self.start_tacking_time=None
        self.force_turning_angle=None 
        self.position=position   ###[x,y,roll,yaw]
        
        self.rudder=0       ### the positive direction is counterclockwise
        self.sail=0           ### the positive direction is counterclockwise
        
        self.target_v=0
        self.dT=area[0]       ## radius of target area
        self.dM=area[1]       ## radius of pre arrive
        self.target=target    ###the center of target area[x,y]   self.dM=10,which is the radius of the pre-arrived area ,self.dT=5,which is r of target area          
        self.true_target=[target[0]+math.sin(true_wind[1]+math.pi/2)*self.dT/2,target[1]-math.cos(true_wind[1]+math.pi/2)*self.dT/2]
        self.frequency=1/sample_time
        
        self.keeping_state=0

        self.true_wind=true_wind       ##[wind speed, direction]

        self.rudder_controller=rudder_controller()
        self.velocity_updator=info_updator()
        self.sail_controller=sailcontroller()
        

        self.flag=False              ### whether it should stop
        self.time=0
        self.runtimes=runtimes

    ## predict the state for next moment and make decision  
    def update_state(self,true_wind,new_location):
        self.time+=1
        new_location[3]=self.regular_angle(new_location[3])
        boat_to_target_angle=math.atan2(self.target[1]-self.position[1],self.target[0]-self.position[0])

        if self.time>self.runtimes:
            self.flag=True  #Stop the program
        
        self.true_wind=true_wind
        self.get_app_wind()

        self.velocity,course_angle,self.position=self.velocity_updator.update_velocity(new_location,self.position)
        # print('vvvvv',self.velocity[0])
        [self.desired_angle,self.keeping_state,self.force_turning_angle,self.tacking_angle,
        self.tacking_sign,self.start_tacking_time]=get_desired_angle.run(self.velocity,
        self.position,self.target,self.true_wind,self.dT,self.dM,self.desired_angle,self.tacking_angle,self.tacking_sign,
        self.start_tacking_time,self.time,self.keeping_state,self.force_turning_angle,self.true_target)

        # self.desired_angle=0.6

        if self.time>self.runtimes-200:  ### it's time to go home
            self.desired_angle=-math.pi/2

        adoptive_angle=self.compare_heading_and_course(course_angle)
        # print(self.desired_angle,adoptive_angle,end=' ')
        
        self.rudder=self.rudder_controller.generate_command(self.desired_angle,adoptive_angle,self.keeping_state,
        self.velocity,self.tacking_angle,self.force_turning_angle,boat_to_target_angle,self.true_wind)    
        # print(self.rudder,self.velocity[0])
        self.sail,self.target_v=self.sail_controller.generate_command(self.velocity,self.position,self.target,
        self.true_wind,self.keeping_state,self.desired_angle,self.tacking_angle,self.force_turning_angle)
        
        
        
        return self.rudder,self.sail,self.desired_angle

    def compare_heading_and_course(self,course_angle):
        if abs(self.position[3]-course_angle)>0.4:
            return self.position[3]
        else:
            return course_angle




    
    
    
        

    def get_app_wind(self):
        
        ###this part is different from the paper since there might be something wrong in the paper
        ###get coordinates of true wind
        
        self.app_wind=[self.true_wind[0]*math.cos(self.true_wind[1]-self.position[3])-self.velocity[0],
                        self.true_wind[0]*math.sin(self.true_wind[1]-self.position[3])-self.velocity[1]]
        ###convert into polar system
        angle=math.atan2(self.app_wind[1],self.app_wind[0])
        self.app_wind=[math.sqrt(pow(self.app_wind[1],2)+pow(self.app_wind[0],2)),angle]
        return self.app_wind


## all angle should be modified into the range [0,2*pi)   
    def regular_angle(self,angle):
        
        while angle>math.pi:
            angle-=math.pi*2
        while angle<-math.pi:
            angle+=math.pi*2
        return angle


    def sign(self,p):
        
        if p>0:
            return 1
        elif p==0:
            return 0
        else:
            return -1