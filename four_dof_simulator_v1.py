import math
import numpy as np 
import numpy.linalg as lg
from lift_and_drag import *

''' zs=0.4,sail length=0.3, distance from sail to the center=0.05 
    m=2
'''
class single_sailboat_4DOF_simulator:
    def __init__(self,sample_time=0.001,v_and_angular_v=[0,0,0,0],
        location_and_orientation=[0,0,0,0],com_sail=0,true_sail=0,rudder=0,true_wind=[0,0]):
        self.sample_time=sample_time

        self.v_and_angular_v=np.array(v_and_angular_v).T  #[u,v,p,r]
        self.location_and_orientation=np.array(location_and_orientation).T #[x,y,roll,yaw]

        self.com_sail=com_sail
        self.true_sail=true_sail
        self.rudder=rudder
        self.true_wind=np.array(true_wind)
        self.M=np.array([[2.5,0.0,0.0,0.0],
                [0.0,2.5,0.0,0.0],
                [0.0,0.0,0.3,0.0],
                [0.0,0.0,0.0,0.1]])   #Mass_and_inertia_matrix
        self.M_inv=lg.inv(self.M)
        self.counter=0



    def step(self,location_and_orientation,v_and_angular_v,com_sail,rudder,true_wind): 
        
        self.update_parameters(location_and_orientation,v_and_angular_v,com_sail,rudder,true_wind)
        app_wind_speed,angle_app_wind,wind_angle_of_attack=self.get_app_wind()

        self.get_true_sail(angle_app_wind)
        self.move_sail()
        sail_torque=self.get_sail_torque(wind_angle_of_attack,app_wind_speed,angle_app_wind)
        rudder_torque=self.get_rudder_torque()
        Coriolis_v=self.get_C_v()
        D_vn=self.get_D_vn(app_wind_speed,angle_app_wind)
        g_n=self.get_g_n()
        j_n=self.get_j_n()
        all_other_terms=-Coriolis_v.dot(self.v_and_angular_v)-D_vn-g_n+sail_torque+rudder_torque
        
        self.v_and_angular_v+=self.M_inv.dot(all_other_terms)*self.sample_time
        self.location_and_orientation+=j_n.dot(self.v_and_angular_v)*self.sample_time

        self.counter+=1
        # if self.counter%5==0: print(sail_torque,[app_wind_speed,angle_app_wind,wind_angle_of_attack,self.true_sail])
        # print(sail_torque,[app_wind_speed,angle_app_wind,wind_angle_of_attack,self.true_sail])
        return self.v_and_angular_v,self.location_and_orientation,self.true_sail


    def move_sail(self):
        if abs(self.com_sail-self.true_sail)>self.sample_time*3:
            self.true_sail+=self.sign(self.com_sail-self.true_sail)*self.sample_time*3

    def get_true_sail(self,angle_app_wind):  
        if math.sin(angle_app_wind)>0:
            self.com_sail=-self.com_sail
        if math.cos(angle_app_wind+math.pi)>math.cos(self.com_sail) or abs(angle_app_wind-self.sign(angle_app_wind)*math.pi-self.com_sail)<0.02:
            self.com_sail=angle_app_wind-self.sign(angle_app_wind)*math.pi
    

    def update_parameters(self,location_and_orientation,v_and_angular_v,com_sail,rudder,true_wind):
        self.v_and_angular_v=np.array(v_and_angular_v).T
        self.location_and_orientation=np.array(location_and_orientation).T

        self.com_sail=com_sail
        self.rudder=rudder
        self.true_wind=np.array(true_wind)

        self.v_and_angular_v=self.v_and_angular_v.astype(np.float64)
        self.location_and_orientation=self.location_and_orientation.astype(np.float64)
    
    def get_app_wind(self):
        ys=0.1
        u,v,p,r=self.v_and_angular_v
        roll,yaw=self.location_and_orientation[2:]
        
        app_wind_on_u=self.true_wind[0]*math.cos(self.true_wind[1]-yaw)-u+r*(0.15*math.cos(self.true_sail)-0.05)
        app_wind_on_v=self.true_wind[0]*math.sin(self.true_wind[1]-yaw)*math.cos(roll)-v-r*0.15*math.sin(self.true_sail)+p*0.4
        
        v_app_wind=math.sqrt(app_wind_on_v**2+app_wind_on_u**2)
        angle_app_wind=math.atan2(app_wind_on_v,-app_wind_on_u)
        
        wind_angle_of_attack=angle_app_wind+self.true_sail
        return v_app_wind,angle_app_wind,wind_angle_of_attack
    
    def get_sail_torque(self,wind_angle_of_attack,app_wind_speed,angle_app_wind):
        sail_lift=2*0.5*1.29*0.21*app_wind_speed**2*get_sail_lift_coefficient(wind_angle_of_attack)  ##0.5*density*A*v^2*4=2.5
        sail_drag=2*0.5*1.29*0.21*app_wind_speed**2*get_sail_drag_coefficient(wind_angle_of_attack)  #Ds
        
        sail_torque=np.array([sail_lift*math.sin(angle_app_wind)-sail_drag*math.cos(angle_app_wind),
                            sail_lift*math.cos(angle_app_wind)+sail_drag*math.sin(angle_app_wind),
                            (-sail_lift*math.cos(angle_app_wind)-sail_drag*math.sin(angle_app_wind))*0.4,
                            -(sail_lift*math.sin(angle_app_wind)-sail_drag*math.cos(angle_app_wind))*0.03*math.sin(self.true_sail)
                            +(sail_lift*math.cos(angle_app_wind)+sail_drag*math.sin(angle_app_wind))*(0.2-0.12*math.cos(self.true_sail))])
        sail_torque=sail_torque.T
        return sail_torque

    def get_rudder_torque(self):
        u,v,p,r=self.v_and_angular_v
        u_rudder=-u+r*0 #yr=0
        v_rudder=-v+r*0.25+p*0.08 #xr=0.3,zr=-0.15

        
        rudder_speed=math.sqrt(v_rudder**2+u_rudder**2)
        angle_app_rudder=-math.atan2(-v_rudder,-u_rudder)
        rudder_angle_of_attack=angle_app_rudder+self.rudder
        
        rudder_lift=7.2*rudder_speed**2*get_rudder_lift_coefficient(rudder_angle_of_attack)
        rudder_drag=7.2*rudder_speed**2*get_rudder_drag_coefficient(rudder_angle_of_attack)
        rudder_torque=np.array([rudder_lift*math.sin(angle_app_rudder)-rudder_drag*math.cos(angle_app_rudder),
                                rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder),
                                -(rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder))*0.1,
                                -(rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder))*0.4])
        
        rudder_torque=rudder_torque.T
        return rudder_torque

    def get_C_v(self):
        u,v,p,r=self.v_and_angular_v
        C_v=np.array([[0,-2*r,0,2*v],
                    [2*r,0,0,-2*u],
                    [0,0,0,0],
                    [-2*v,2*u,0,0]])
        return C_v

    def get_D_vn(self,app_wind_speed,angle_app_wind):
        u,v,p,r=self.v_and_angular_v
        roll,yaw=self.location_and_orientation[2:]
        D_heel_and_yaw=np.array([0,0,2*abs(p)*p,0.13*r+0.25*abs(r)*r*math.cos(roll)]).T
        D_k=self.get_D_k(u,v,p,r,roll,yaw)
        D_h=self.get_D_h(u,v,p,r,roll,yaw,app_wind_speed,angle_app_wind)
        D_vn=D_heel_and_yaw+D_h+D_k
        return D_vn

    def get_D_k(self,u,v,p,r,roll,yaw):
        keel_u=-u
        keel_v=-v+p*0.1-r*0.05
        keel_speed=math.sqrt(keel_u**2+keel_v**2)
        keel_angle_of_attack=math.atan2(keel_v,-keel_u)
        keel_lift=11*keel_speed**2*get_rudder_lift_coefficient(keel_angle_of_attack)
        keel_drag=11*keel_speed**2*get_rudder_drag_coefficient(keel_angle_of_attack)
        D_k=np.array([-keel_lift*math.sin(keel_angle_of_attack)+keel_drag*math.cos(keel_angle_of_attack),
                    -keel_lift*math.cos(keel_angle_of_attack)-keel_drag*math.sin(keel_angle_of_attack),
                    (keel_lift*math.cos(keel_angle_of_attack)+keel_drag*math.sin(keel_angle_of_attack))*0.06,
                    -(keel_lift*math.cos(keel_angle_of_attack)+keel_drag*math.sin(keel_angle_of_attack))*0.06])
        D_k=D_k.T 

        return D_k

    def get_D_h(self,u,v,p,r,roll,yaw,app_wind_speed,angle_app_wind):
        hull_u=-u
        try:
            hull_v=-v-0.15*r/math.cos(roll)
        except:
            print('error! abnormal roll')
        hull_speed=math.sqrt(hull_u**2+hull_v**2)
        hull_angle_of_attack=math.atan2(hull_v,-hull_u)
        
        if hull_speed<0.5:
            F_rh=hull_speed*0.1
        else:
            F_rh=hull_speed*0.1+(hull_speed-0.5)**2*10
        if hull_u>0:
            F_rh=F_rh*3

        h_lift=0
        D_h=np.array([-h_lift*math.sin(hull_angle_of_attack)+F_rh*math.cos(hull_angle_of_attack),
                    -h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack)*math.cos(roll),
                    (-h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack))*math.cos(roll)*0.03,
                    (-h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack))*math.cos(roll)*(0.15-0.15*abs(math.sin(hull_angle_of_attack)))])
        return D_h.T
    
    def get_g_n(self):
        roll=self.location_and_orientation[2]
        g_n=np.array([0,0,(0.8*roll**2+0.5*abs(roll))*self.sign(roll),0]).T
        return g_n

    def get_j_n(self):
        roll,yaw=self.location_and_orientation[2:]
        j_n=np.array([[math.cos(yaw),-math.sin(yaw)*math.cos(roll),0,0],
                    [math.sin(yaw),math.cos(yaw)*math.cos(roll),0,0],
                    [0,0,1,0],
                    [0,0,0,math.cos(roll)]])
        return j_n

    def sign(self,p):
        if p>0:
            return 1
        elif p<0:
            return -1
        else:
            return 0