import pygame
import OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import numpy as np
import math
from time import time,sleep
from scipy.spatial.transform import Rotation



class scene_displayer:
    def __init__(self,pos_and_orientation=[0,0,0,0],rudder=0,sail=0,cycle=0.01,pool_size=[6,9],boat_type="sailboat"):
        self.boat_type=boat_type
        self.boat = pywavefront.Wavefront('boat.obj', collect_faces=True)
        self.scaled_size   = 1
        self.boat_color=[0.5,0.5,0.5]
        self.sail_color=[0.8,0.9,1]
        self.rudder_color=[0.8,0.9,1]

        self.boat_scale,self.boat_trans=self.init_obj(self.boat,'boat')

        self.rudder_obj=pywavefront.Wavefront('rudder.obj', collect_faces=True)
        self.rudder_scale, self.rudder_trans =  self.init_obj(self.rudder_obj,'rudder')
        self.rudder_pos=+np.array([-130,0,0])

        self.sail_obj=pywavefront.Wavefront('sail.obj', collect_faces=True)
        self.sail_scale, self.sail_trans =  self.init_obj(self.sail_obj,'sail')
        self.sail_pos=np.array([0,0,0])
        self.pos=np.array([2,7,0])
        self.pos_and_orientation=np.array(pos_and_orientation)
        self.sail=sail
        self.rudder=rudder
        self.cycle=cycle
        self.stop_signal=False
        self.window_size=(1200,800)
        self.pool_size=pool_size
        
        

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

        return scale,trans
    
    def draw_pool(self,x,y):
        # glPushMatrix()
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


    def Draw_boat(self,x,y,roll,yaw,rudder,sail):
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
        glColor3f(*self.boat_color)  
        glScalef(*self.boat_scale)
        glTranslatef(*np.array([x,y,0.25*270]))
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*-self.boat_trans)

        
        for mesh in self.boat.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.boat.vertices[vertex_i]))
            glEnd()
        
        
        glPopMatrix()
        ############################################# Hull ##################################################


        if self.boat_type=="diffboat": return
        ############################################ Rudder #################################################
        glPushMatrix()
        glScalef(*self.rudder_scale)
        # rot_mat*
        glColor3f (*self.rudder_color)
        glTranslatef(*np.array([x,y,0.25*270])*self.boat_scale/self.rudder_scale)
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([-120,0,-60]))
        glRotatef(rudder,0,0,1)
        glTranslatef(*-self.rudder_trans)
        
        for mesh in self.rudder_obj.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.rudder_obj.vertices[vertex_i]))
            glEnd()
        glPopMatrix()
        ############################################ Rudder #################################################

        


        ############################################# Axis ##################################################
        glPushMatrix()
        glScalef(*self.boat_scale)
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
        if self.boat_type=="rudderboat": return
        
        ############################################# Sail ##################################################
        glPushMatrix()
        glColor3f(*self.sail_color)  
        glScalef(*self.sail_scale)
        glTranslatef(*np.array([x,y,0.25*270])*self.boat_scale/self.sail_scale)
        glRotatef(math.sqrt(np.sum(rot_vec**2))*57.32, rot_vec[1], rot_vec[0], rot_vec[2])
        glTranslatef(*np.array([1000,0,7000]))
        glRotatef(sail,0,0,1)
        glTranslatef(*-self.sail_trans)

        for mesh in self.sail_obj.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*np.array(self.sail_obj.vertices[vertex_i]))
            glEnd()


        
        glPopMatrix()
        ############################################# Sail ##################################################

    def main(self):
        pygame.init()
        # display = (1200, 800)
        pygame.display.set_mode(self.window_size, DOUBLEBUF | OPENGL)
        
        gluPerspective(45, (self.window_size[0] / self.window_size[1]), 1, 500.0)
        
        glTranslatef(-self.pool_size[0]/2, -self.pool_size[1]/2, -12)
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
            # self.Draw_boat(1000*math.sin(i),1000*math.cos(i),0,j,j,j*2,j*2)
            self.draw_pool(self.pool_size[0],self.pool_size[1])
            self.Draw_boat(*self.pos_and_orientation,self.rudder*57.32,self.sail*57.32)
            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            pygame.display.flip()
            # pygame.time.wait(10)
            sleep_time=self.cycle-(time()-start_time)
            if sleep_time>0:
                sleep(sleep_time)
        print("command stop")


    def update_pose(self,pos_and_orientation,rudder,sail,stop_signal):
        self.pos_and_orientation=np.array(pos_and_orientation)
        # print(self.pos_and_orientation)
        self.pos_and_orientation[0]*=270
        self.pos_and_orientation[1]*=270
        self.pos_and_orientation[2]*=57.32
        self.pos_and_orientation[3]*=57.32
        self.sail=sail
        self.rudder=rudder
        self.stop_signal=stop_signal
        # print(self.sail,self.rudder)
        

# a=scene_displayer()
# a.main()
