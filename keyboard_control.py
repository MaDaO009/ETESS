import pygame
import sys
import time
import globalvar as gl



def main():
    pygame.init()
    pygame.display.set_caption("Hello world")
    pygame.event.set_allowed([pygame.KEYDOWN,pygame.KEYUP])
    pygame.key.set_repeat(1000,200)
    pygame.display.set_mode([50,50])
    rudder = 0
    sail = 0

    move_rudder,move_sail = 0,0
    sail_type='up'
    rudder_type='up'
    while True:
        if gl.get_value('flag'):
            break
        last_rudder=rudder
        last_sail=sail
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.erudderit()
            elif event.type == pygame.KEYDOWN: #键被按下
                if event.key == pygame.K_g:
                    gl.set_value('keyboard_flag',True)
                if event.key == pygame.K_s:
                    gl.set_value('keyboard_flag',False)
                if event.key == pygame.K_t:
                    gl.set_value('flag',True)
                keyboard_flag=gl.get_value('keyboard_flag')
                if keyboard_flag:
                    if event.key == pygame.K_LEFT:
                        move_rudder = -0.15
                        rudder_type='down'
                    elif event.key == pygame.K_RIGHT:
                        move_rudder = 0.15
                        rudder_type='down'
                # else:
                #     move_rudder=sign(rudder-320)*15
                    
                    if event.key == pygame.K_UP:
                        sail_type='down'
                        move_sail = 0.1
                    elif event.key == pygame.K_DOWN:
                        sail_type='down'
                        move_sail = -0.1
                # else:
                #     move_sail=-sign(y)
            elif event.type == pygame.KEYUP and keyboard_flag:
                
                if event.key==pygame.K_LEFT or event.key==pygame.K_RIGHT:
                    move_rudder=-sign(rudder)*0.15
                    rudder_type='up'
                if event.key==pygame.K_UP or event.key==pygame.K_DOWN:
                    move_sail=-sign(sail-0.5)*0.1
                    sail_type='up'
                # print(move_rudder,move_sail)
        # print(move_rudder)
        
        
        rudder = rudder + move_rudder
        sail = sail + move_sail           
        
        if abs(rudder)<0.05 and last_rudder != 0 and rudder_type=='up':
            move_rudder=0
            rudder=0
            # print('!!')
        if abs(sail-0.5)<0.05 and last_sail !=0.5 and sail_type=='up':
            move_sail=0
            sail=0.5
        if rudder>0.78:
            rudder=0.78
        elif rudder<-0.78:
            rudder=-0.78
        if sail>1.3:
            sail=1.3
        elif sail<0:
            sail=0
        # print(rudder,sail)
        # pygame.display.update()
        if gl.get_value('keyboard_flag'):
            # print(gl.get_value('keyboard_flag'))
            gl.set_value('rudder',rudder)
            gl.set_value('sail',sail)
        time.sleep(0.1)

def sign(x):
    if x>0:
        return 1
    elif x==0:
        return 0
    else:
        return -1

if __name__ == '__main__':
    main()