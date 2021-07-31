from controller.pid import PID
import random
class easy_controller:
    def __init__(self,init_pose=[0,0,0,0],sample_time=0.1):
        self.pose=init_pose
        self.heading_controller=PID(P=0.5,I=0.1,D=0.2,sample_time=sample_time)
        
    
    def update_state(self,temp,new_pose):
        self.pose=new_pose    
        rudder_command=self.heading_controller.update(new_pose[3],1.57)
        return [rudder_command,0.3*random.random()]