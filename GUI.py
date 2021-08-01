import pygame
from pygame import display
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
        self.refresh_rate=3
        self.counter=0
        self.boat_index=0
        self.display_index=0
        self.display_order=['v','u','r','p','roll','yaw']
        
    def drawText(self, font, x, y, text):                                                
        textSurface = font.render(text, True, (255,255,255,255),(0,0,0,255))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x-textSurface.get_width()/2, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)        
    
    def drawLines(self,offscreen_surface):
        pygame.draw.line(offscreen_surface, (255,255,255), (0,0), (0, 100),3)
        pygame.draw.line(offscreen_surface, (255,255,255), (0,0), ( 100,0),3)
        pygame.draw.line(offscreen_surface, (255,255,255), (100,0), ( 100,100),3)
        pygame.draw.line(offscreen_surface, (255,255,255), (0,100), ( 100,100),3)
        if self.display_index<4:
            for i in range(99):
                pygame.draw.line(offscreen_surface, (255,255,255), (i, 95-95*self.boats[self.boat_index].twists_buffer[i][self.display_index]),
                                                        (i+1, 95-95*self.boats[self.boat_index].twists_buffer[i+1][self.display_index]),3)
        else:
            temp=self.display_index-2
            for i in range(99):
                pygame.draw.line(offscreen_surface, (255,255,255), (i, 95-30*self.boats[self.boat_index].twists_buffer[i][temp]),
                                                        (i+1, 95-30*self.boats[self.boat_index].twists_buffer[i+1][temp]),3)

    def draw_surface(self,surface):
        textData = pygame.image.tostring(surface, "RGBA", True)
        glWindowPos2d(0, 0)
        glDrawPixels(100, 100, GL_RGBA, GL_UNSIGNED_BYTE, textData)

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

    def surfaceToTexture(self,texID, pygame_surface ): 
        rgb_surface = pygame.image.tostring( pygame_surface, 'RGB')
        glBindTexture(GL_TEXTURE_2D, texID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        surface_rect = pygame_surface.get_rect()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def main(self):
        pygame.init()
        # display = (1200, 800)
        win=pygame.display.set_mode(self.window_size, DOUBLEBUF | OPENGL)
        font = pygame.font.SysFont('arial', 15, True)

        gluPerspective(45, (self.window_size[0] / self.window_size[1]), 1, 500.0)
        
        glTranslatef(-self.pool_size[0]/2, -self.pool_size[1]/2, -25)
        
        while (not self.stop_signal):
            start_time=time()
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
                    if event.key == pygame.K_j:
                        self.boat_index=(self.boat_index+1)%self.N
                    if event.key == pygame.K_l:
                        self.boat_index=(self.boat_index-1)%self.N
                    if event.key == pygame.K_i:
                        self.display_index=(self.display_index+1)%6
                    if event.key == pygame.K_k:
                        self.display_index=(self.display_index-1)%6
            # prepare to render the texture-mapped rectangle
            
            
    
            # glEnable(GL_CULL_FACE)
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            # # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            self.draw_pool(self.pool_size[0],self.pool_size[1])
            for i in range(self.N): self.Draw_boat(*self.boats[i].pose,self.boats[i].components[0]*57.32,self.boats[i].components[1]*57.32,i)
            
            # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            self.drawText(font,800,500,"123")
            self.drawText(font,50,105,self.display_order[self.display_index])
            self.drawText(font,50,155,"Boat: %d"%self.boat_index)
            # self.drawLine(((-100,2),(3,4000)),(1,1,1))
            offscreen_surface = pygame.Surface((100, 100))
            self.drawLines(offscreen_surface)
            self.draw_surface(offscreen_surface)
            pygame.display.flip()
            

            # pygame.time.wait(10)
            sleep_time=self.cycle-(time()-start_time)
            # print(time()-start_time)
            if sleep_time>0:
                sleep(sleep_time)
            # print(sleep_time)
        print("command stop")


    def update_pose(self,poses,twists,components,stop_signal):
        self.counter=(self.counter+1)%self.refresh_rate
        for i in range(self.N):
            self.boats[i].pose=np.array(poses[i])
            # print(self.boats[i].poses)
            self.boats[i].pose[0]*=270
            self.boats[i].pose[1]*=270
            self.boats[i].pose[2]*=57.32
            self.boats[i].pose[3]*=57.32
            self.boats[i].components=components[i]
            if self.counter==0:
                self.boats[i].poses_buffer.append(list(poses[i]))
                self.boats[i].twists_buffer.append(list(twists[i]))
                del self.boats[i].poses_buffer[0]
                del self.boats[i].twists_buffer[0]
                # if i ==0: print(self.boats[1].twists_buffer)
        self.stop_signal=stop_signal

        