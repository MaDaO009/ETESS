import pygame
import OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import numpy as np
import math
from time import time
from scipy.spatial.transform import Rotation



class scene_displayer:
    def __init__(self):
            
        self.boat = pywavefront.Wavefront('boat.obj', collect_faces=True)
        self.scaled_size   = 1
        self.color=np.random.random(3)
        self.color2=np.random.random(3)
        self.boat_scale,self.boat_trans=self.init_obj(self.boat,'boat')

        self.rudder=pywavefront.Wavefront('rudder.obj', collect_faces=True)
        self.rudder_scale, self.rudder_trans =  self.init_obj(self.rudder,'rudder')
        self.rudder_pos=+np.array([-130,0,0])

        self.sail=pywavefront.Wavefront('sail.obj', collect_faces=True)
        self.sail_scale, self.sail_trans =  self.init_obj(self.sail,'sail')
        self.sail_pos=np.array([0,0,0])
        # print(self.boat_trans)
        # print(self.boat_scale/self.sail_scale)
    def init_obj(self,obj,name):
        box = (obj.vertices[0], obj.vertices[0])
        for vertex in obj.vertices:
            min_v = [min(box[0][i], vertex[i]) for i in range(3)]
            max_v = [max(box[1][i], vertex[i]) for i in range(3)]
            box = (min_v, max_v)
        # if name=='boat' or 'sail':
        box[0][2]-=box[1][2]
        box[1][2]=0

        boat_size     = [box[1][i]-box[0][i] for i in range(3)]
        max_boat_size = max(boat_size)
        
        scale    = np.array([self.scaled_size/max_boat_size for i in range(3)])
        
        trans    = np.array([-(box[1][i]+box[0][i])/2 for i in range(3)])
        if name=='rudder':
            scale    = np.array([self.scaled_size/max_boat_size/2 for i in range(3)])
            trans[0]=box[1][0]
        if name=='sail':
            trans[0]=box[1][0]
        print(name,trans,box,scale)
        return scale,trans
    def Draw_boat(self,x,y,z,yaw,roll,rudder,sail):
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

        glScalef(*self.boat_scale)
        glTranslatef(*np.array([x,y,z]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*-self.boat_trans)

        
        for mesh in self.boat.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.boat.vertices[vertex_i]))
            glEnd()
        
        glColor3f(*self.color)  # 设定颜色RGB
        glPopMatrix()
        ############################################# Hull ##################################################




        ############################################# Axis ##################################################
        glPushMatrix()
        glScalef(*self.boat_scale)
        glTranslatef(*np.array([x,y,z]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*-self.boat_trans)

        glBegin(GL_LINES)

        glColor3f (1.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(200.0, 0.0, 0.0)

        glColor3f (1.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 200.0, 0.0)

        glColor3f (1.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 200.0)
        glEnd()

        glPopMatrix()
        ############################################# Axis ##################################################



        ############################################ Rudder #################################################
        glPushMatrix()
        glScalef(*self.rudder_scale)
        # rot_mat*
        glColor3f (0.0, 1.0, 1.0)
        glTranslatef(*np.array([x,y,z]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([-120,0,-60]))
        glRotatef(rudder,0,0,1)
        glTranslatef(*-self.rudder_trans)
        
        for mesh in self.rudder.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.rudder.vertices[vertex_i]))
            glEnd()
        
        glColor3f(*self.color2)  # 设定颜色RGB
        glPopMatrix()
        ############################################ Rudder #################################################

        ############################################# Axis ##################################################
        glPushMatrix()
        glScalef(*self.rudder_scale)
        # rot_mat*
        glTranslatef(*np.array([x,y,z]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([-120,0,-60]))
        glRotatef(rudder,0,0,1)
        glTranslatef(*-self.rudder_trans)


        glBegin(GL_LINES)

        glColor3f (1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(200.0, 0.0, 0.0)

        glColor3f (1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 200.0, 0.0)

        glColor3f (1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 200.0)
        glEnd()

        glPopMatrix()
        ############################################# Axis ##################################################



        ############################################# Axis ##################################################
        glPushMatrix()
        glScalef(*self.rudder_scale)
        # rot_mat*
        # glTranslatef(*np.array([x,y,z]))
        glBegin(GL_LINES)

        glColor3f (0.0, 1.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(200.0, 0.0, 0.0)

        glColor3f (0.0, 1.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 200.0, 0.0)

        glColor3f (0.0, 1.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 200.0)
        glEnd()

        glPopMatrix()
        ############################################# Axis ##################################################


        ############################################# Sail ##################################################
        glPushMatrix()
        
        glScalef(*self.sail_scale)
        glTranslatef(*np.array([x,y,z])*self.boat_scale/self.sail_scale)
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([1000,0,7000]))
        glRotatef(sail,0,0,1)
        glTranslatef(*-self.sail_trans)

        for mesh in self.sail.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.sail.vertices[vertex_i]))
            glEnd()


        glColor3f(*self.color)  # 设定颜色RGB
        glPopMatrix()
        ############################################# Sail ##################################################



    def main(self):
            pygame.init()
            display = (1200, 800)
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
            gluPerspective(45, (display[0] / display[1]), 1, 500.0)
            glTranslatef(0.0, 0.0, -10)
            i=0
            k=0
            j=0
            d=1
            while True:
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

                # glRotatef(1, 5, 1, 1)
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                # self.Draw_boat(10000*math.sin(i),2000*math.cos(i),0,k,j)
                # self.Draw_boat(2000*math.sin(i),10000*math.cos(i),0,k,j)
                self.Draw_boat(1000*math.sin(i),1000*math.cos(i),0,j,j,0,0)
                self.Draw_boat(0,0,0,j,j,j*3,j*3)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

                pygame.display.flip()
                pygame.time.wait(10)

a=scene_displayer()
a.main()
