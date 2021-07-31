import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from time import time,sleep
from scipy.spatial.transform import Rotation
from GUI_boat import boat


class scene_displayer:
    def __init__(self,N=1,poses=[[0,0,0,0]],components=[[0,0]],cycle=0.01,pool_size=[6,20],boat_type=["sailboat"]):
        self.boats=[boat(poses[i],components[i],boat_type[i]) for i in range(N)]
        self.N=N

        self.cycle=cycle
        self.stop_signal=False
        self.window_size=(900,600)
        self.pool_size=pool_size
            
    
    def draw_pool(self,x,y):
        glPushName(1)
        glBegin(GL_QUADS)
        # glColor4f(0.05, 0.05, 0.95, 0.3)
        glColor3f(0.2,0.2,0.2)
        glNormal3f(0.0, 0.0, 1.0) # Allows for light to reflect off certain parts of surface
        glVertex3f(x, 0.0, 0.0)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, y, -1.0)
        glVertex3f(x, 0.0, -1.0)


        # Back face 
        glNormal3f(0.0, 0.0,-1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, y, 0.0)
        glVertex3f(0.0, y, -1.0)
        glVertex3f(0.0, 0.0, -1.0)


        # Left face 
        glNormal3f(-1.0,0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(x, 0.0, 0.0)
        glVertex3f(x, 0.0, -1.0)
        glVertex3f(0.0, 0.0, -1.0)

        # Right face 
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, y, -1.0)
        glVertex3f(0.0, y, -1.0)
        glVertex3f(0.0, y, 0.0)

        # Bottom face
        glColor3f(0.2,0.2,0.2)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, -1.0)
        glVertex3f(x, 0.0, -1.0)
        glVertex3f(x,y, -1.0)
        glVertex3f(0.0, y, -1.0)

        # Top face 
        glColor4f(0.2, 0.2, 0.95, 0.5)
        glNormal3f(0.0,-1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, y, 0.0)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, 0.0, 0.0)
        glEnd()


    def Draw_boat(self,x,y,roll,yaw,rudder,sail,boat_number):
        st=time()
        rot = Rotation.from_euler('zyx', [yaw, roll, 0], degrees=True)
        rot_vec = rot.as_rotvec()
        rot_vec=np.array(rot_vec)
        rot_mat=np.array(rot.as_matrix())

        rot_rudder = Rotation.from_euler('zyz', [yaw, roll, rudder], degrees=True)
        rot_vec_rudder = rot_rudder.as_rotvec()
        rot_vec_rudder=np.array(rot_vec_rudder)

        rot_sail = Rotation.from_euler('zyz', [yaw, roll, sail], degrees=True)
        rot_vec_sail = rot_sail.as_rotvec()
        rot_vec_sail=np.array(rot_vec_sail)
        
        rot_roll = Rotation.from_euler('zyz', [0, roll, 0], degrees=True)
        roll_mat=np.array(rot_roll.as_matrix())
        ############################################# Hull ##################################################
        glPushMatrix()
        glColor3f(*self.boats[boat_number].boat_color)  
        glScalef(*self.boats[boat_number].boat_scale)
        glTranslatef(*np.array([x,y,0.25*270]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*-self.boats[boat_number].boat_trans)

        for mesh in self.boats[boat_number].boat.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.boats[boat_number].boat.vertices[vertex_i]))
            glEnd()
        
        
        glPopMatrix()
        ############################################# Hull ##################################################


        if self.boats[boat_number].boat_type=="diffboat": return
        ############################################ Rudder #################################################
        glPushMatrix()
        glScalef(*self.boats[boat_number].rudder_scale)
        # rot_mat*
        glColor3f (*self.boats[boat_number].rudder_color)
        glTranslatef(*np.array([x,y,0.25*270])*self.boats[boat_number].boat_scale/self.boats[boat_number].rudder_scale)
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([-120,0,-60]))
        glRotatef(rudder,0,0,1)
        glTranslatef(*-self.boats[boat_number].rudder_trans)
        
        for mesh in self.boats[boat_number].rudder_obj.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.boats[boat_number].rudder_obj.vertices[vertex_i]))
            glEnd()
        glPopMatrix()
        ############################################ Rudder #################################################

    
        if self.boats[boat_number].boat_type=="rudderboat": return
        
        ############################################# Sail ##################################################
        glPushMatrix()
        glColor3f(*self.boats[boat_number].sail_color)  
        glScalef(*self.boats[boat_number].sail_scale)
        glTranslatef(*np.array([x,y,0.25*270])*self.boats[boat_number].boat_scale/self.boats[boat_number].sail_scale)
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([1000,0,7000]))
        glRotatef(sail,0,0,1)
        glTranslatef(*-self.boats[boat_number].sail_trans)

        for mesh in self.boats[boat_number].sail_obj.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.boats[boat_number].sail_obj.vertices[vertex_i]))
            glEnd()


        
        glPopMatrix()
        ############################################# Sail ##################################################

    def main(self):
        pygame.init()
        # display = (1200, 800)
        pygame.display.set_mode(self.window_size, DOUBLEBUF | OPENGL)
        
        gluPerspective(45, (self.window_size[0] / self.window_size[1]), 1, 500.0)
        
        glTranslatef(-self.pool_size[0]/2, -self.pool_size[1]/2, -25)
        i=0
        k=0
        j=0
        d=1
        
        while (not self.stop_signal):
            start_time=time()
            k=(k+1)%360
            i+=0.01
            j+=d
            if abs(j)>=50:
                d*=-1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        glTranslatef(0.5,0,0)
                    if event.key == pygame.K_RIGHT:
                        glTranslatef(-0.5,0,0)
                    if event.key == pygame.K_UP:
                        glTranslatef(0,-1,0)
                    if event.key == pygame.K_DOWN:
                        glTranslatef(0,1,0)
                    if event.key == pygame.K_w:
                        glRotatef(10, 1, 0, 0)
                    if event.key == pygame.K_s:
                        glRotatef(-10, 1, 0, 0)
                    if event.key == pygame.K_q:
                        glTranslatef(0,0,1)
                    if event.key == pygame.K_e:
                        glTranslatef(0,0,-1)

            # glEnable(GL_CULL_FACE)
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            self.draw_pool(self.pool_size[0],self.pool_size[1])
            for i in range(self.N): self.Draw_boat(*self.boats[i].pose,self.boats[i].components[0]*57.32,self.boats[i].components[1]*57.32,i)

            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            pygame.display.flip()
            # pygame.time.wait(10)
            sleep_time=self.cycle-(time()-start_time)
            # print(time()-start_time)
            if sleep_time>0:
                sleep(sleep_time)
            # print(sleep_time)
        print("command stop")


    def update_pose(self,poses,components,stop_signal):
        for i in range(self.N):
            self.boats[i].pose=np.array(poses[i])
            # print(self.boats[i].poses)
            self.boats[i].pose[0]*=270
            self.boats[i].pose[1]*=270
            self.boats[i].pose[2]*=57.32
            self.boats[i].pose[3]*=57.32
            self.boats[i].components=components[i]
        self.stop_signal=stop_signal

        