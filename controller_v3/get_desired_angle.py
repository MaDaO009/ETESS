import math
from keep2 import position_keeper

position_keeper=position_keeper()

ref_point=[0,0]
points_list=[[0,0],[0,0],[0,0],[0,0]]

def run(velocity,position,target,true_wind,dT,dM,last_desired_angle,tacking_angle,tacking_sign,
start_tacking_time,counter,keeping_state,force_turning_angle,true_target):
    global points_list
    boat_to_target_angle=math.atan2(target[1]-position[1],target[0]-position[0])
    true_boat_to_target_angle=math.atan2(true_target[1]-position[1],true_target[0]-position[0])
    distance_st=math.sqrt(pow(target[1]-position[1],2)+pow(target[0]-position[0],2))
    true_distance_st=math.sqrt(pow(true_target[1]-position[1],2)+pow(true_target[0]-position[0],2))
    force_turning_angle=boundary_detector(position,tacking_angle,true_wind,force_turning_angle,boat_to_target_angle)
    
    

    if distance_st>dT:
        position_keeper.init()
        keeping_state=0
        ref_point=[-10,-10]
        # print('dt',true_wind[1])
        desired_angle=go_to_target_area(boat_to_target_angle,distance_st,dM,dT,true_wind)
        target_v=0
    else:
        keeping_state=1
        desired_angle,target_v,points_list=position_keeper.run(position[0],position[1],target,true_wind,position[3],velocity[0])
        # print('@!!!!',target,position)
        # desired_angle,keeping_state=keeping_in_target_area(position,velocity,distance_st,target,keeping_state,
        # true_wind,boat_to_target_angle,dT,last_desired_angle)
    # print('last1',last_desired_angle,desired_angle)
    tacking_angle,tacking_sign,start_tacking_time,desired_angle=tacking_detector(velocity[0],position[3],desired_angle,
    last_desired_angle,tacking_angle,tacking_sign,true_wind,start_tacking_time,counter,force_turning_angle,
    boat_to_target_angle)
    # print('last3',tacking_angle,force_turning_angle)
    if tacking_angle!=None:
        
        force_turning_angle=None

    elif force_turning_angle!=None:
        tacking_angle=None
        

    
    
    return [desired_angle,keeping_state,force_turning_angle,tacking_angle,tacking_sign,start_tacking_time,target_v,points_list]


def boundary_detector(position,tacking_angle,true_wind,force_turning_angle,boat_to_target_angle):
    if tacking_angle== None:
        if force_turning_angle == None:
            x=position[0]+math.cos(position[3]*1.3)
            y=position[1]+math.sin(position[3]*1.3)
            if x>0 and x<6 and y>1 and y<7.5:
                force_turning_angle=None
            elif sign(math.sin(position[3]-true_wind[1])) !=sign(math.sin(boat_to_target_angle-true_wind[1])):
                if x<0:
                    if y<7:
                        force_turning_angle=0.6
                    else:
                        force_turning_angle=-0.6
                elif x>6:
                    if y<7:
                        force_turning_angle=2.5
                    else:
                        force_turning_angle=-2.5
                else: 
                    force_turning_angle=None
        else:
            if sign(math.sin(position[3]-true_wind[1])) ==sign(math.sin(force_turning_angle-true_wind[1])):
                if abs (math.sin(position[3]-true_wind[1]))>0.5:
                    force_turning_angle=None
        return force_turning_angle
    else:
        return None
        

def tacking_detector(v,heading_angle,desired_angle,last_desired_angle,tacking_angle,tacking_sign,true_wind,
start_tacking_time,counter,force_turning_angle,boat_to_target_angle):
    if tacking_angle ==None:
        if math.cos(heading_angle-true_wind[1])+math.cos(desired_angle-true_wind[1])<0 and math.cos(heading_angle-true_wind[1])<0:
            
            if sign(math.sin(desired_angle-true_wind[1])) != sign(math.sin(heading_angle-true_wind[1])) and force_turning_angle==None:
                ###Yes, it's a tacking
                if v>0.3 and (math.cos(true_wind[1]-boat_to_target_angle)>-0.8 or force_turning_angle !=None):
                    
                    start_tacking_time=counter
                    tacking_sign=sign(math.sin(heading_angle-true_wind[1]))
                    tacking_angle=desired_angle
                else:
                    desired_angle=last_desired_angle

    else:
    ### is tacking
        is_success=(tacking_sign !=sign(math.sin(heading_angle-true_wind[1])))
        if is_success or counter-start_tacking_time>35 or v<0:
            start_tacking_time=None
            tacking_sign=None
            tacking_angle=None
    return tacking_angle,tacking_sign,start_tacking_time,desired_angle

def go_to_target_area(boat_to_target_angle,distance_st,dM,dT,true_wind):
    next_desired_angle=boat_to_target_angle
    # print('go',true_wind[1])
    if distance_st<dM and distance_st>dT:
        if math.cos(boat_to_target_angle-true_wind[1])>0: ##not able to slow down
            # print('cant slow down',boat_to_target_angle,true_wind[1])
            if math.cos(boat_to_target_angle-(true_wind[1]+math.pi/2))>math.cos(boat_to_target_angle-(true_wind[1]-math.pi/2)):
                next_desired_angle=-math.pi/2+boat_to_target_angle
            else:
                next_desired_angle=math.pi/2+boat_to_target_angle

    if math.cos(true_wind[1]-next_desired_angle)<-0.6: ##exceed dead angle
        # print('in dead zone')
        next_desired_angle=sign(math.sin(true_wind[1]-next_desired_angle))*0.88+true_wind[1]+math.pi
    next_desired_angle=regular_angle(next_desired_angle)
    return next_desired_angle


        
def keeping_in_target_area(position,velocity,distance_st,target,keeping_state,true_wind,boat_to_target_angle,dT,last_desired_angle):
    global ref_point
    # del_x=distance_st*math.sin(true_wind[1]-boat_to_target_angle)
    # del_y=distance_st*math.cos(true_wind[1]-boat_to_target_angle)
    
    dx=target[0]-position[0]
    dy=target[1]-position[1]
    d_wind_x=dx*math.cos(true_wind[1])+dy*math.sin(true_wind[1])
    d_wind_y=-dx*math.sin(true_wind[1])+dy*math.cos(true_wind[1])
    boat_to_ref_angle=math.atan2(ref_point[1]-position[1],ref_point[0]-position[0])
    if keeping_state==0:
        ##判断船头是否朝里
        h_x=position[0]+dT*math.cos(position[3])
        h_y=position[1]+dT*math.sin(position[3])
        if math.sqrt((h_x-target[0])**2+(h_y-target[1])**2)<dT:
            
            
            if d_wind_x>0:  ##风向相反/靠上位置
                ##生成参考点
                ref_point[0]=target[0]+dT/2*math.cos(true_wind[1]+math.pi/2*sign(d_wind_y))-dT/2.5*math.cos(true_wind[1])
                ref_point[1]=target[1]+dT/2*math.sin(true_wind[1]+math.pi/2*sign(d_wind_y))-dT/2.5*math.sin(true_wind[1])
                # print('ref point2',ref_point)
                keeping_state=3
            else:##与风向同向/靠下位置
                ##生成参考点
                ref_point[0]=target[0]+dT/1.5*math.cos(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.cos(true_wind[1])
                ref_point[1]=target[1]+dT/1.5*math.sin(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.sin(true_wind[1])
                # print('ref point1',ref_point)
                keeping_state=1
            desired_angle=math.atan2(ref_point[1]-position[1],ref_point[0]-position[0])
            
        else:
            desired_angle=last_desired_angle

    if keeping_state==1:
        print('1',[d_wind_x,d_wind_y])
        # print(sign(d_wind_y))
        desired_angle=math.atan2(ref_point[1]-position[1],ref_point[0]-position[0])
        desired_angle=true_wind[1]+sign(math.sin(desired_angle-true_wind[1]))*math.pi*0.65
        distance_b_r=math.sqrt((ref_point[1]-position[1])**2+(ref_point[0]-position[0])**2)
        # if math.cos(desired_angle-true_wind[1])<-0.6:
        #     # print('a')
        #     desired_angle=true_wind[1]+sign(math.sin(desired_angle-true_wind[1]))*math.pi*0.7
        # elif math.cos(desired_angle-true_wind[1])>-0.2:
        #     # print('b')
        #     desired_angle=true_wind[1]+sign(math.sin(desired_angle-true_wind[1]))*math.pi*0.6
        if velocity[0]>0.45 and (math.sin(boat_to_ref_angle-true_wind[1])*math.sin(position[3]-true_wind[1])<0 or distance_b_r<0.2 or d_wind_x>0.1):
            keeping_state=2
            desired_angle=true_wind[1]+math.pi*0.65*sign(d_wind_y)
            desired_angle=regular_angle(desired_angle)
            print('State  2',desired_angle,velocity[0],sign(d_wind_y))
    if keeping_state==2:## tack
        # print('2')

        desired_angle=true_wind[1]+math.pi*0.65*sign(d_wind_y)
        desired_angle=regular_angle(desired_angle)
        if math.cos(position[3]-desired_angle)>0.8:
            keeping_state=3
            ref_point[0]=target[0]+dT/2*math.cos(true_wind[1]+math.pi/2*sign(d_wind_y))-dT/2.5*math.cos(true_wind[1])
            ref_point[1]=target[1]+dT/2*math.sin(true_wind[1]+math.pi/2*sign(d_wind_y))-dT/2.5*math.sin(true_wind[1])
            print('ref point 2',ref_point,'State 3')
        

    elif keeping_state==3:
        
        distance_b_r=math.sqrt((ref_point[1]-position[1])**2+(ref_point[0]-position[0])**2)
        if position[1]<5.1:
            keeping_state=1
            ref_point[0]=target[0]+dT/1.5*math.cos(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.cos(true_wind[1])
            ref_point[1]=target[1]+dT/1.5*math.sin(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.sin(true_wind[1])
        desired_angle=math.atan2(ref_point[1]-position[1],ref_point[0]-position[0])
        
        ## if in dead zone:
        if math.cos(desired_angle-true_wind[1])<math.cos(math.pi/4.5+math.pi/2):
            # print("!!")
            desired_angle=true_wind[1]+sign(desired_angle-true_wind[1])*math.pi*3.5/4.5

        if math.sin(boat_to_ref_angle-true_wind[1])*math.sin(position[3]-true_wind[1])<0 or distance_b_r<0.1:
            
            print([d_wind_x,d_wind_y],position,boat_to_ref_angle,distance_b_r)
            desired_angle=true_wind[1]
            keeping_state=4
        desired_angle=regular_angle(desired_angle)

    elif keeping_state==4:
        print(4)
        desired_angle=true_wind[1]+math.pi*0.25*sign(d_wind_y)
        if math.cos(position[3]-desired_angle)>0.9:
            keeping_state=1
            ref_point[0]=target[0]+dT/1.5*math.cos(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.cos(true_wind[1])
            ref_point[1]=target[1]+dT/1.5*math.sin(true_wind[1]+math.pi/2*sign(d_wind_y))+dT/5*math.sin(true_wind[1])
            print('ref point1,4',ref_point)
        
    return desired_angle,keeping_state
    
    



def sign(p):
        
    if p>0:
        return 1
    elif p==0:
        return 0
    else:
        return -1

def regular_angle(angle):
        
    while angle>math.pi:
        angle-=math.pi*2
    while angle<-math.pi:
        angle+=math.pi*2
    return angle


# run([0,0,0,0],[1,1,0,0],[1,1.5],[1,1.5],1,2,False,None)