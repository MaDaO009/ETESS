import math

def get_sail_lift_coefficient(angle_of_attack):

    if angle_of_attack>=0 and angle_of_attack<0.7:
        lift_coefficient=1.85*angle_of_attack
    elif angle_of_attack>=0.7 and angle_of_attack<2.79:
        lift_coefficient=0.4475*angle_of_attack**3-2.501*angle_of_attack**2+3.002*angle_of_attack+0.27
    elif angle_of_attack>=2.79:
        lift_coefficient=57.88*angle_of_attack**3-500*angle_of_attack**2+1440*angle_of_attack-1383.7
    else:
        lift_coefficient=-get_sail_lift_coefficient(-angle_of_attack)
    
    return lift_coefficient

def get_rudder_lift_coefficient(angle_of_attack):
    while angle_of_attack>math.pi:
        angle_of_attack-=math.pi*2
        # print(angle_of_attack)
    while angle_of_attack<-math.pi:
        angle_of_attack+=math.pi*2
        # print(angle_of_attack)
    if angle_of_attack>=0:
        if angle_of_attack<1.58:
            lift_coefficient=1.2*math.sin(math.pi*(angle_of_attack/math.pi*2)**(5/8.6))
        else:
            # print(angle_of_attack,'aaa')
            lift_coefficient=-get_rudder_lift_coefficient(math.pi-angle_of_attack)
    else:
        lift_coefficient=-get_rudder_lift_coefficient(-angle_of_attack)
    return lift_coefficient

def get_sail_drag_coefficient(angle_of_attack):
    drag_coefficient=0.73-0.67*math.cos(2*angle_of_attack)
    return drag_coefficient

def get_rudder_drag_coefficient(angle_of_attack):
    drag_coefficient=1.05-1.05*math.cos(2*angle_of_attack)
    return drag_coefficient

if __name__=="__main__":
    for i in range(21):
        print(get_rudder_lift_coefficient(i*0.3-3))
    print(get_rudder_lift_coefficient(3.14))