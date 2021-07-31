from controller2.pid import PID
import random
from controller2.FFDL_DCC_controller_class import FFDLcController
class FFDL_controller:
    def __init__(self,init_poses=[0,0,0,0],sample_time=0.1):
        self.poses=init_poses
        self.N=1
        self.sample_time=sample_time
    def init(self):
        self.heading_controllers=[PID(P=0.5,I=0.1,D=0.2,sample_time=self.sample_time) for i in range(self.N)]
        self.v_controller=FFDLcController(Nt=500,le=1,lu=2,yd_init=2,ys_init=[0,0,0,0])

    def update_state(self,temp,new_poses,twists):
        self.poses=new_poses    
        rudder_commands=[self.heading_controllers[i].update(new_poses[i][3],1.57) for i in range(self.N)]
        thruster_commands=self.v_controller.compute_u(twists[0][0],[float(twists[i][0]) for i in range(1,self.N)])
        thruster_commands=[float('{0:.3f}'.format(i[0])) for i in thruster_commands]
        thruster_commands=[0.3]+thruster_commands
        # print(twists,thruster_commands)
        # print([[rudder_commands[i],thruster_commands[i]] for i in range(self.N)])
        return [[rudder_commands[i],thruster_commands[i]] for i in range(self.N)]