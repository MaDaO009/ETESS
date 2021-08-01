import pygame
import sys
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.GLU import *
# set pygame screen
class scene_displayer:
    def __init__(self,N=1,poses=[[0,0,0,0]],components=[[0,0]],cycle=0.01,pool_size=[6,20],boat_type=["sailboat"]):
        pygame.init()
        pygame.display.set_mode((500, 500), OPENGL | DOUBLEBUF)
        pygame.display.init()
        info = pygame.display.Info()

        #colours
        self.MIDNIGHT = (  200,   200, 200 )
        self.BUTTER   = ( 255, 245, 100 )

        # basic opengl configuration
        glViewport(0, 0, info.current_w, info.current_h)
        glDepthRange(0, 1)
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_BLEND)

        self.texID = glGenTextures(1)
        # create pygame clock
        self.clock = pygame.time.Clock()

        # make an offscreen surface for drawing PyGame to
        self.offscreen_surface = pygame.Surface((400, 400))
        self.text_font = pygame.font.Font( None, 30 ) # some default font

    def surfaceToTexture(self, pygame_surface ):
        rgb_surface = pygame.image.tostring( pygame_surface, 'RGB')
        glBindTexture(GL_TEXTURE_2D, self.texID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        surface_rect = pygame_surface.get_rect()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)




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
    
    def main(self):
        done = False
        gluPerspective(45, (500 / 500), 1, 500.0)
                
        glTranslatef(0, 0, -25)

        while not done:
            # get quit event
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

            # Do all the PyGame operations to the offscreen surface
            # So any backgrounds, sprites, etc. will get drawn to the offscreen
            # rather than to the default window/screen.
            self.offscreen_surface.fill( self.MIDNIGHT )
            # write some nonsense to put something changing on the screen
            words = self.text_font.render( "β-Moé-Moé count: "+str( pygame.time.get_ticks() ), True, self.BUTTER )
            self.offscreen_surface.blit( words, (50, 250) )


            # prepare to render the texture-mapped rectangle
            glClear(GL_COLOR_BUFFER_BIT)
            # glLoadIdentity()
            glDisable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            #glClearColor(0, 0, 0, 1.0)

            # draw texture openGL Texture
            self.surfaceToTexture( self.offscreen_surface )
            glBindTexture(GL_TEXTURE_2D, self.texID)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(-1, 1)
            glTexCoord2f(0, 1); glVertex2f(-1, -1)
            glTexCoord2f(1, 1); glVertex2f(1, -1)
            glTexCoord2f(1, 0); glVertex2f(1, 1)
            glEnd()

            self.draw_pool(6,20)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
a=scene_displayer()
a.main()