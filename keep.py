

import math
import copy



class position_keeper():
    def __init__(self,accelerating_x_distance=0.9,wearing_y_distance=0.7,dT=1.3):
        self.alternative_points_list=[[None,None],[None,None],[None,None],[None,None]] 
        #[upper_left_point,upper_right_point,lower_left_point,lower_right_point]
        
        self.reference_point=None
        self.accelerating_x_distance=accelerating_x_distance
        self.wearing_y_distance=wearing_y_distance

        # self.state='to_point'
        self.target_angle=0
        self.initial_wear_angle=None
        self.initial_tack_angle=None
        

        self.start_wear_y=None
        self.start_acc_x=None

    def init(self):
        self.initial_wear_angle=None
        self.initial_tack_angle=None
        self.start_wear_y=None
        self.start_acc_x=None

    def get_alternative_point(self,target,true_wind):
        upper_dx=(self.accelerating_x_distance-self.wearing_y_distance/2+0.4)/2
        
        self.alternative_points_list[0][0]=target[0]-upper_dx*math.cos(true_wind[1]+math.pi/2)-self.wearing_y_distance/2*math.cos(true_wind[1])
        self.alternative_points_list[0][1]=target[1]-upper_dx*math.sin(true_wind[1]+math.pi/2)-self.wearing_y_distance/2*math.sin(true_wind[1])
        ##-    +   
        ##+    +

        self.alternative_points_list[1][0]=target[0]+upper_dx*math.cos(true_wind[1]+math.pi/2)-self.wearing_y_distance/2*math.cos(true_wind[1])
        self.alternative_points_list[1][1]=target[1]+upper_dx*math.sin(true_wind[1]+math.pi/2)-self.wearing_y_distance/2*math.sin(true_wind[1])
        ##+    +  
        ##-    -
        lower_dx=(self.accelerating_x_distance+self.wearing_y_distance/2-0.4)/2
        point_dy=max(0,self.wearing_y_distance/2-self.accelerating_x_distance*math.tan(math.pi/6.5))
        self.alternative_points_list[2][0]=target[0]-lower_dx*math.cos(true_wind[1]+math.pi/2)+point_dy*math.cos(true_wind[1])
        self.alternative_points_list[2][1]=target[1]-lower_dx*math.sin(true_wind[1]+math.pi/2)+point_dy*math.sin(true_wind[1])
        ##-    -  
        ##+    -
        self.alternative_points_list[3][0]=target[0]+lower_dx*math.cos(true_wind[1]+math.pi/2)+point_dy*math.cos(true_wind[1])
        self.alternative_points_list[3][1]=target[1]+lower_dx*math.sin(true_wind[1]+math.pi/2)+point_dy*math.sin(true_wind[1])
        ##+    - 
        ##-    -
        # print('list!!!!!!',self.alternative_points_list)
        
    def determine_current_area(self,sailboat_x,sailboat_y,true_wind,target,heading_angle):
        dx=target[0]-sailboat_x
        dy=target[1]-sailboat_y
        d_wind_x=-dx*math.cos(true_wind[1])-dy*math.sin(true_wind[1])
        d_wind_y=dx*math.sin(true_wind[1])-dy*math.cos(true_wind[1])
        if d_wind_x<-d_wind_y*self.sign(math.sin(heading_angle-true_wind[1]))*math.sin(math.pi/6.3):
            ## Up wind area:
            return "upper_area",d_wind_y,d_wind_x
        else:
            return "lower_area",d_wind_y,d_wind_x

    
    def select_reference_point(self,current_area,sailboat_x,sailboat_y,heading_angle,true_wind):
        if current_area=='upper_area':
            ## select the farther one
            boat_to_point_angle1=math.atan2(self.alternative_points_list[0][1]-sailboat_y,self.alternative_points_list[0][0]-sailboat_x)
            boat_to_point_angle2=math.atan2(self.alternative_points_list[1][1]-sailboat_y,self.alternative_points_list[1][0]-sailboat_x)
            distance1=math.sqrt((self.alternative_points_list[0][0]-sailboat_x)**2+(self.alternative_points_list[0][1]-sailboat_y)**2)
            distance2=math.sqrt((self.alternative_points_list[1][0]-sailboat_x)**2+(self.alternative_points_list[1][1]-sailboat_y)**2)
            
            if math.sin(boat_to_point_angle1-true_wind[1])*math.sin(heading_angle-true_wind[1])<0:
                distance1=-1
            if math.sin(boat_to_point_angle2-true_wind[1])*math.sin(heading_angle-true_wind[1])<0:
                distance2=-1

            if distance1>distance2:
                self.reference_point=self.alternative_points_list[0]
            else:
                self.reference_point=self.alternative_points_list[1]
            return max(distance1,distance2)
        
        else:
            boat_to_point_angle3=math.atan2(self.alternative_points_list[2][1]-sailboat_y,self.alternative_points_list[2][0]-sailboat_x)
            boat_to_point_angle4=math.atan2(self.alternative_points_list[3][1]-sailboat_y,self.alternative_points_list[3][0]-sailboat_x)
            distance3=math.sqrt((self.alternative_points_list[2][0]-sailboat_x)**2+(self.alternative_points_list[2][1]-sailboat_y)**2)
            distance4=math.sqrt((self.alternative_points_list[3][0]-sailboat_x)**2+(self.alternative_points_list[3][1]-sailboat_y)**2)
            
            if math.sin(boat_to_point_angle3-true_wind[1])*math.sin(heading_angle-true_wind[1])<0:
                distance3=-1
            if math.sin(boat_to_point_angle4-true_wind[1])*math.sin(heading_angle-true_wind[1])<0:
                distance4=-1
            
            
            if distance3>distance4:
                self.reference_point=self.alternative_points_list[2]
            else:
                self.reference_point=self.alternative_points_list[3]
            # print([distance3,distance4])
            return max(distance3,distance4)


    def go_to_reference_point(self,sailboat_x,sailboat_y,current_area,distance,true_wind,heading_angle,target):
        # print(current_area,self.reference_point)
        if current_area=='upper_area':
            self.target_v=0.2
            # point_on_circle=[target[0]-*self.dT,target[1]-math.sin(true_wind)*self.dT]
            
            # ref_angle=self.sign(math.sin(heading_angle-true_wind[1]))*math.pi/5*3.5+true_wind[1]
            # ref_angle=self.regular_angle(ref_angle)
            # if math.cos(math.pi/5*3.5+true_wind[1]) !=0:
            #     reference_k=self.sign(math.sin(heading_angle-true_wind[1]))*math.tan(math.pi/5*3.5+true_wind[1])
            #     reference_b=self.reference_point[1]-reference_k*self.reference_point[0]

            #     point_to_line_distance=self.sign(math.sin(math.pi/5-true_wind[1]))*(-sailboat_y+reference_k*sailboat_x+reference_b)/math.sqrt(1+reference_k**2)
            #     #如果点在线下面，则point_to_line_distance>0

            #     ##得到目标角度
                
            #     if distance<self.accelerating_x_distance/2:
            #         self.target_angle=ref_angle+point_to_line_distance*(distance/self.accelerating_x_distance)**2
            #     else:
            #         self.target_angle=ref_angle+point_to_line_distance*(0.5-(1-distance/self.accelerating_x_distance))**2
            #     print('ref_angle',ref_angle,'target_angle',self.target_angle,'pl_distance',point_to_line_distance)
            self.target_angle=math.atan2(self.reference_point[1]-sailboat_y,self.reference_point[0]-sailboat_x)
            if  math.cos(true_wind[1]-self.target_angle)>0.4: ##该角度下难以减速
                self.target_angle=self.sign(math.sin(self.target_angle-true_wind[1]))*0.4*math.pi+true_wind[1]

            # else:
            #     point_to_line_distance=self.reference_point[0]-sailboat_x
            #     ####可能有错############
                
            #     if distance<self.accelerating_x_distance/2:
            #         self.target_angle=ref_angle+point_to_line_distance*(distance/self.accelerating_x_distance)**2*3
            #     else:
            #         self.target_angle=ref_angle+point_to_line_distance*(0.5-(1-distance/self.accelerating_x_distance)**2)*3
            



            
        else:
            self.target_v=0.7
            ref_angle=self.sign(math.sin(heading_angle-true_wind[1]))*math.pi/6.5*4.25+true_wind[1]
            ref_angle=self.regular_angle(ref_angle)
            if math.cos(math.pi/6.5*4.25+true_wind[1]) !=0:
                reference_k=self.sign(math.sin(heading_angle-true_wind[1]))*math.tan(math.pi/6.5*4.25+true_wind[1])
                reference_b=self.reference_point[1]-reference_k*self.reference_point[0]
                
                point_to_line_distance=self.sign(math.sin(math.pi/6.5-true_wind[1]))*(-sailboat_y+reference_k*sailboat_x+reference_b)/math.sqrt(1+reference_k**2)
                #如果点在线下面，则point_to_line_distance>0
                
                if distance<self.accelerating_x_distance/2:
                    self.target_angle=ref_angle+point_to_line_distance*(distance/self.accelerating_x_distance)**2
                else:
                    self.target_angle=ref_angle+point_to_line_distance*(0.5-(1-distance/self.accelerating_x_distance)**2)
            else:
                point_to_line_distance=self.reference_point[0]-sailboat_x
                
                if distance<self.accelerating_x_distance/2:
                    self.target_angle=ref_angle+point_to_line_distance*(distance/self.accelerating_x_distance)**2
                else:
                    self.target_angle=ref_angle+point_to_line_distance*(0.5-(1-distance/self.accelerating_x_distance)**2)
                ##得到目标角度
        
        if math.cos(true_wind[1]-self.target_angle)<-0.6: ##exceed dead angle
        # print('in dead zone')
            self.target_angle=self.sign(math.sin(true_wind[1]-self.target_angle))*0.88+true_wind[1]+math.pi
        self.target_angle=self.regular_angle(self.target_angle)
        return self.target_angle,self.target_v

    def run(self,sailboat_x,sailboat_y,target,true_wind,heading_angle,sailboat_v):
        self.get_alternative_point(target,true_wind)
        current_area,d_wind_y,d_wind_x=self.determine_current_area(sailboat_x,sailboat_y,true_wind,target,heading_angle)
        distance=self.select_reference_point(current_area,sailboat_x,sailboat_y,heading_angle,true_wind)
        # print('list',self.alternative_points_list,'ref_point',self.reference_point,current_area)
        if distance != -1:
            self.target_angle,self.target_v=self.go_to_reference_point(sailboat_x,sailboat_y,current_area,distance,true_wind,heading_angle,target)
        

        elif self.initial_wear_angle==None and self.initial_tack_angle==None:
            if current_area=='upper_area' and self.initial_wear_angle==None:
                self.start_wear_y=d_wind_x
                
                self.initial_wear_angle=heading_angle
                self.target_v=0
            elif current_area=='lower_area':
                if sailboat_v<0.35: 
                    if self.initial_wear_angle==None:
                        self.start_wear_y=d_wind_x
                        self.start_acc_x=None
                        print('start_wear',self.start_wear_y,sailboat_v)
                        self.initial_wear_angle=heading_angle
                        self.target_v=0
                else:
                    # print('SSSSSSSSSSSSSS')
                    if sailboat_v>0.42:
                        print('CANNNNNNNN',sailboat_v)
                        if self.initial_tack_angle==None:
                            self.initial_tack_angle=heading_angle
                            # print('Tack!!!!!!!!')
                            self.target_v=0.8
                    else:
                        self.target_angle=self.sign(math.sin(heading_angle-true_wind[1]))*math.pi*0.65+true_wind[1]
                        self.target_angle=self.regular_angle(self.target_angle)
                        self.target_v=0.8

        if self.start_acc_x != None and current_area=='lower_area':
            if sailboat_v>0.42:
                self.accelerating_x_distance=0.1*(abs(d_wind_y-self.start_acc_x)-self.accelerating_x_distance)+self.accelerating_x_distance
                self.start_acc_x=None
                print('accerating distance',self.accelerating_x_distance)
            else:
                print('v',sailboat_v)
        
            
        self.target_angle,self.target_v=self.wear(true_wind,heading_angle,d_wind_x,d_wind_y)
        self.target_angle,self.target_v=self.tack(sailboat_v,true_wind,heading_angle)

        return self.target_angle,self.target_v,self.alternative_points_list

    def wear(self,true_wind,heading_angle,d_wind_x,d_wind_y):
        if self.initial_wear_angle != None:
            if d_wind_x<self.start_wear_y:
                self.start_wear_y=d_wind_x
            self.target_angle=heading_angle+self.sign(math.sin(true_wind[1]-self.initial_wear_angle))*2.5
            self.target_angle=self.regular_angle(self.target_angle)
            self.target_v=(1-math.cos(heading_angle-self.initial_wear_angle))/2.5
            # print(self.target_v,math.cos(heading_angle-self.initial_wear_angle))
            if self.sign(math.sin(true_wind[1]-heading_angle)) !=self.sign(math.sin(true_wind[1]-self.initial_wear_angle)):
                if math.cos(true_wind[1]-heading_angle)<-0.3:
                    self.initial_wear_angle=None
                    self.wearing_y_distance=(abs(self.start_wear_y-d_wind_x)-self.wearing_y_distance)*0.1+self.wearing_y_distance
                    print('wearing_y',self.wearing_y_distance)
                    self.start_wear_y=None
                    self.start_acc_x=d_wind_y
        return self.target_angle,self.target_v
        

    
    def tack(self,sailboat_v,true_wind,heading_angle):
        if self.initial_tack_angle != None:

            self.target_v=0.8
            # print(self.initial_tack_angle)
            self.target_angle=heading_angle-self.sign(math.sin(true_wind[1]-self.initial_tack_angle))*2.5
            self.target_angle=self.regular_angle(self.target_angle)

            if self.sign(math.sin(true_wind[1]-heading_angle)) !=self.sign(math.sin(true_wind[1]-self.initial_tack_angle)):
                if math.cos(true_wind[1]-heading_angle)>-0.8:
                    self.initial_tack_angle=None
        
        return self.target_angle,self.target_v
        

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

# reference_point=reference_point()
# reference_point.get_ref_point([3,5],[1,-math.pi/2])
# reference_point.if_there_exist_points_according_to_heading_angle([1,-math.pi/2],4,5,0.5)


# def keep_in_target_area():

#     if there_exists_points_according_to_heading_angle():
#         if in_up_wind_area(heading_angle,true_wind,position):
#             reference_point=select_farther_upper_point()
#         else:
#             reference_point=select_farther_lower_point()
    
#     else:
#         if in_up_wind_area(heading_angle,true_wind,position):
#             wear(initial_angle)
#         else:
#             if velocity[0]<0.35:
#                 wear(initial_angle)
#             else:
#                 tack_if_is_able_to(initial_angle)


