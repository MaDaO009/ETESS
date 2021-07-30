from controller.pid2 import PID 
import math

class rudder_controller():
    def __init__(self):
        self.command_generator=PID(P=0.5,I=0.2,D=0.5)
        self.rudder=0
        self.maxrudder=math.pi/4  ##max angle of rudder
        self.command_generator.setBoundary(self.maxrudder,-self.maxrudder)
        self.sign_signal=1

    def generate_command(self,desired_angle,current_angle,keeping_state,velocity,tacking_angle,
    force_turning_angle,boat_to_target_angle,true_wind):
        
        if keeping_state==2:
            self.rudder=-self.maxrudder*self.sign(math.sin(boat_to_target_angle-true_wind[1]))
        
        else:  
            
            if math.cos(current_angle-desired_angle)>0:##防止坐标在-pi到pi时跳跃
                if current_angle-desired_angle>math.pi/2:
                    current_angle=current_angle-math.pi*2
                elif current_angle-desired_angle<-math.pi/2:
                    current_angle=current_angle+math.pi*2
                else:
                    current_angle=current_angle
                
                self.rudder=-self.command_generator.update(current_angle,desired_angle)
                current_angle=self.regular_angle(current_angle)

            else:
                self.rudder=self.maxrudder*self.sign(math.sin(current_angle-desired_angle))

            if tacking_angle != None:
                self.rudder== self.maxrudder*self.sign(math.sin(tacking_angle-true_wind[1]))
            elif force_turning_angle != None:
                if self.sign(self.rudder) == self.sign(math.sin(force_turning_angle-true_wind[1])):
                    self.rudder=-self.rudder
        
        if keeping_state==4:
            self.rudder=self.maxrudder*self.sign(self.rudder)

        if velocity[0]<0 and self.sign_signal>-0.8:
            self.sign_signal-=0.2
        elif velocity[0]>0 and self.sign_signal<0.8:
            self.sign_signal+=0.2
            
        if self.sign_signal<0:    
            self.rudder=-self.maxrudder*self.sign(math.sin(desired_angle-true_wind[1]))/2
        
        return self.rudder
  
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