import math
from controller.pid2 import PID
class sailcontroller():
    def __init__(self,p_term=1,i_term=0.3,d_term=0.06,Dv_constant=0.4,ideal_angle=0.9):
        self.pid_adjustment=PID(P=p_term,I=i_term,D=d_term)
        self.sail=0
        self.maxsail=math.pi/12*5
        
        self.Dv_constant=Dv_constant
        self.ideal_angle=ideal_angle
    
    def generate_command(self,velocity,position,target,target_v,true_wind,keeping_state,desired_angle,
    tacking_angle,force_turning_angle):
        app_wind=self.get_app_wind(true_wind,position[3],velocity)
        if target_v==0.8:
            self.pid_adjustment.clear()
        if keeping_state==0:
            # print(3333333)
            target_v=self.get_desire_v(velocity,position,target,true_wind,keeping_state,desired_angle)
        # print(target_v,11111111)
        optimal_sail =self.get_optimal_sail(position[3],app_wind)
        final_sail=self.get_final_sail(target_v,optimal_sail,velocity[0],position[3],app_wind,tacking_angle)
        if force_turning_angle != None:
            final_sail=1
        
        return final_sail,target_v

    def get_desire_v(self,velocity,position,target,true_wind,keeping_state,desired_angle):
        distance_st=math.sqrt(pow(target[1]-position[1],2)+pow(target[0]-position[0],2))
        if keeping_state==0:
            target_v=distance_st*self.Dv_constant
            if math.cos(true_wind[1]-position[3])>0.3:
                target_v=0.2
        # elif keeping_state==1:
        #     target_v=1.0
        #     # if math.cos(true_wind[1]-position[3])>math.cos(math.pi-self.ideal_angle):
        #     #     target_v=0.15+0.01*math.asin(math.sin(abs(true_wind[1]-position[3])-(math.pi-self.ideal_angle)))
        #     # else:
        #     #     target_v=0.15
        # elif keeping_state==2:
        #     target_v=0.5
        # elif keeping_state==3:
        #     target_v=0.2
        # elif keeping_state==4:
        #     target_v=0.1
        return target_v


    def get_optimal_sail(self,heading_angle,app_wind):
        # angle_diff=self.get_abs_angle_difference(heading_angle,app_wind[1]+math.pi)
        # print('angle_diff',angle_diff,'heading',heading_angle,app_wind[1])
        if math.cos(app_wind[1]) <= math.cos(3*math.pi/4):
            optimal_sail=0.3+(-3*math.pi/4+abs(app_wind[1]))*0.3
            # print(optimal_sail,'3')
        else:
            optimal_sail=0.3+(3/4*math.pi-abs(app_wind[1]))*1.2
            # print(optimal_sail,'4')
        if optimal_sail>self.maxsail:
            optimal_sail=self.maxsail
        return optimal_sail

    def get_app_wind(self,true_wind,heading_angle,velocity):
        
        ###this part is different from the paper since there might be something wrong in the paper
        ###get coordinates of true wind
        
        app_wind=[true_wind[0]*math.cos(true_wind[1]-heading_angle)-velocity[0],
                        true_wind[0]*math.sin(true_wind[1]-heading_angle)-velocity[1]]
        ###convert into polar system
        angle=math.atan2(app_wind[1],app_wind[0])
        app_wind=[math.sqrt(pow(app_wind[1],2)+pow(app_wind[0],2)),angle]
        return app_wind

    def regular_angle(self,angle):
        
        while angle>math.pi:
            angle-=math.pi*2
        while angle<-math.pi:
            angle+=math.pi*2
        return angle

    ## return abs(angle1-angle2) which must < pi
    def get_abs_angle_difference(self,angle1,angle2):
        return math.acos(math.cos(angle1-angle2))
    
    def get_final_sail(self,target_v,optimal_sail,v,heading_angle,app_wind,tacking_angle):
        ### get maxsail (considering the influence of wind)
        maxsail=min(self.maxsail,abs(app_wind[1]))
        offset=-self.pid_adjustment.update(v,target_v)
        
        if self.maxsail-optimal_sail>0.2:
            final_sail=(maxsail+optimal_sail)/2+offset
            # print('!!!!!!!!!',(maxsail+optimal_sail)/2)
            if final_sail>maxsail:
                final_sail=maxsail
            elif final_sail<optimal_sail:
                final_sail=optimal_sail
            
        else:
            final_sail=optimal_sail-0.35-offset
            
            if final_sail>optimal_sail:
                final_sail=optimal_sail
                # print(optimal_sail)
            elif final_sail<0.4:
                final_sail=0.4
        # print('offset',offset,'opt_sail',optimal_sail,'final sail',final_sail)
        # print(self.pid_adjustment.PTerm,self.pid_adjustment.ITerm)
        # print(optimal_sail,target_v,offset,final_sail,'22222222')

        # if tacking_angle != None :
        #     # print('!!!!!!!!!!!!!!!!!!')
        #     final_sail=optimal_sail
        return final_sail   
        
        ### get abs(offset)
        

# a=sailcontroller()
# b=a.generate_command([0,0,0,0],[1,1,0,0],[3,5],[3,-1.57],0,0.6)
# print(b)
