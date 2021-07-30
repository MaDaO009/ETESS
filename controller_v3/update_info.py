import math
from pykalman import KalmanFilter
import numpy as np
class info_updator():
    def __init__(self,list_lens=5,frequency=10):
        self.v_list=[0]*list_lens
        self.u_list=[0]*list_lens
        self.p_list=[0]*2
        self.r_list=[0]*2  #heading
        self.list_lens=list_lens
        self.course_angle_list=[0]*list_lens
        self.position=[0,0,0,0]
        self.frequency=10
        self.init_filter()

    def init_filter(self):
        random_state = np.random.RandomState(0)
        transition_matrix = [[1, 0.1], [0, 1]]
        transition_offset = [-0.1, 0.1]
        observation_matrix = np.eye(2) + random_state.randn(2, 2) * 0.1
        observation_offset = [1.0, -1.0]
        transition_covariance = np.eye(2)
        observation_covariance = np.eye(2) + random_state.randn(2, 2) * 0.1
        initial_state_mean = [5, -5]
        initial_state_covariance = [[1, 0.1], [-0.1, 1]]
        # sample from model
        self.kf = KalmanFilter(
            transition_matrix, observation_matrix, transition_covariance,
            observation_covariance, transition_offset, observation_offset,
            initial_state_mean, initial_state_covariance,
            random_state=random_state
        )


    def update_velocity(self,new_location,position):
            [x,y,roll,heading_angle]=new_location
            [last_x,last_y,last_roll,last_heading]=self.position

            velocity=self.get_velocity(x,last_x,y,last_y,heading_angle,last_heading,roll,last_roll)
            
            course_angle=math.atan2(self.position[1]-last_y,self.position[0]-last_x)
            
            self.position=new_location

            

            return velocity,course_angle,self.position
            
    def get_velocity(self,x,last_x,y,last_y,heading_angle,last_heading,roll,last_roll):
        del_x=x-last_x
        del_y=y-last_y
        

        v=(del_x*math.cos(self.position[3])+del_y*math.sin(self.position[3]))*self.frequency
        
        u=(-del_x*math.sin(self.position[3])+del_y*math.cos(self.position[3]))*self.frequency
        r=(heading_angle-last_heading)*self.frequency
        p=(roll-last_roll)*self.frequency
        
        ### due to the noise, the velocity we choose is the mean value of the velocities in 0.7 second.
        self.v_list.pop(0)
        if abs(v)>3:
            v=self.v_list[self.list_lens-2]
        self.v_list.append(v)

        self.u_list.pop(0)
        if abs(u)>1:
            u=self.u_list[self.list_lens-2]
        self.u_list.append(u)

        self.r_list.pop(0)
        if abs(r)>3.5:
            r=self.r_list[0]
        self.r_list.append(r)

        self.p_list.pop(0)
        if abs(p)>2:
            p=self.p_list[0]
        self.p_list.append(p)

        v=0
        u=0
        p=0
        r=0
        # [v,u]=self.smoothing_curve()
        for i in range (0,self.list_lens):
            v+=self.v_list[i]/self.list_lens
            u+=self.u_list[i]/self.list_lens
        for i in range (0,2):
            r+=self.r_list[i]/2
            p+=self.p_list[i]/2
        # print('aaaaa',v)
        return [v,u,p,r]

    def smoothing_curve(self):
        observations=np.array([[0,0]])
        for i in range(0,self.list_lens):
            # observations=np.delete(observations,0,0)
            observations=np.append(observations,[[self.v_list[i],self.u_list[i]]],axis=0)
        observations=np.delete(observations,0,axis=0)
        smoothed_state_estimates = self.kf.smooth(observations)[0]
        return smoothed_state_estimates[self.list_lens-1]
