import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import time
import math
import threading
import random
import globalvar as gl


class visualazation():
    def __init__(self):
        self.initialize_parameters()
        self.create_window()
        self.init_subwindows_data()
        self.init_boat_data()
        self.init_window_data()
        
    def initialize_parameters(self):
        self.start_time=time.time()
        
        self.x=0
        self.y=0
        self.heading_angle=0
        self.desired_angle=0
        self.rudder=0
        self.sail=0
        self.target_v=0
        self.true_wind=[2,-math.pi/2]
        self.v=0
        self.u=0
        self.w=0
        self.target=[3.2,5.5]
        self.boat_size=0.25
        self.sample_time=0.01
        self.dT=1.3
        self.dM=2.6
    def create_window(self):
        self.figure = plt.figure()
        self.gs1 = gridspec.GridSpec(1, 1)
        self.gs2 = gridspec.GridSpec(3, 1)

        self.main_window=self.figure.add_subplot(self.gs1[0])
        ##this part is for target area and pre-arrive area.
        theta = np.linspace(0, 2*np.pi,100)
        x_t,y_t = np.cos(theta)*self.dT+np.linspace(self.target[0],self.target[0],100), np.sin(theta)*self.dT+np.linspace(self.target[1],self.target[1],100)
        self.main_window.plot(x_t, y_t, color='red', linewidth=1.0)
        
        x_p,y_p = np.cos(theta)*self.dM+np.linspace(self.target[0],self.target[0],100), np.sin(theta)*self.dM+np.linspace(self.target[1],self.target[1],100)
        self.main_window.plot(x_p, y_p, color='orange', linewidth=1.0)


        self.main_window.axis('equal')

        plt.xlim(0,8)
        plt.ylim(-2,10)
        self.gs1.tight_layout(self.figure, rect=[0, 0, 0.7, 1])

        self.forward_velocity_window = self.figure.add_subplot(self.gs2[0])
        plt.xlabel('forward velocity')
        plt.ylim(-0.2,1)
        self.side_velocity_window = self.figure.add_subplot(self.gs2[1])
        plt.xlabel('side velocity')
        plt.ylim(-0.2,0.2)
        self.angular_velocity_window = self.figure.add_subplot(self.gs2[2])
        plt.xlabel('angular velocity')
        plt.ylim(-3.14,3.14)
        self.gs2.tight_layout(self.figure, rect=[0.7, 0, 1, 1], h_pad=0.5)



        top = min(self.gs1.top, self.gs2.top)
        bottom = max(self.gs1.bottom, self.gs2.bottom)

        self.gs1.update(top=top, bottom=bottom)
        self.gs2.update(top=top, bottom=bottom)

    def init_subwindows_data(self):
        self.location_x_data = np.linspace(self.x,self.x,300)
        self.location_y_data=np.linspace(self.y,self.y,300)
        self.trajectory_line, = self.main_window.plot(self.location_x_data,self.location_y_data)
        self.v_x_data = np.linspace(0, 5, 100)
        self.v_data=np.linspace(self.v,self.v,100)
        self.line_forward_velocity, = self.forward_velocity_window.plot(self.v_x_data, self.v_data)

        self.points_x=np.linspace(0, 0, 4)
        self.points_y=np.linspace(0, 0, 4)
        self.line_points,=self.main_window.plot(self.points_x,self.points_y,color='gray')
        
        
        self.target_v_data=np.linspace(self.v,self.v,100)
        self.line_target_velocity, = self.forward_velocity_window.plot(self.v_x_data, self.target_v_data,color='gray')
        # x2_data = np.linspace(0, 5, 100)
        self.u_data=np.linspace(self.u,self.u,100)
        self.line_side_velocity, = self.side_velocity_window.plot(self.v_x_data, self.u_data)
        # x3_data = np.linspace(0, 5, 100)
        self.heading_data=np.linspace(self.heading_angle,self.heading_angle,100)
        self.line_heading, = self.angular_velocity_window.plot(self.v_x_data, self.heading_data)
        self.desired_angle_data=np.linspace(self.desired_angle,self.desired_angle,100)
        self.line_desired_angle, = self.angular_velocity_window.plot(self.v_x_data, self.desired_angle_data,color='gray')

        
    def init_boat_data(self):
        self.boat_y_data=np.array([-math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            1.5*math.sin(self.heading_angle),
                            math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5,
                            -math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5])*self.boat_size
        self.boat_x_data=np.array([-math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            1.5*math.cos(self.heading_angle),
                            math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5,
                            -math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5])*self.boat_size
        self.line_boat, = self.main_window.plot(self.boat_x_data+np.linspace(self.x,self.x,5),self.boat_y_data+np.linspace(self.y,self.y,5))

        self.rudder_y_data=np.array([-math.sin(self.heading_angle),
                                -math.sin(self.heading_angle)-math.cos(self.rudder-math.pi/2+self.heading_angle)])*self.boat_size
        self.rudder_x_data=np.array([-math.cos(self.heading_angle),
                                -math.cos(self.heading_angle)+math.sin(self.rudder-math.pi/2+self.heading_angle)])*self.boat_size
        self.line_rudder,=self.main_window.plot(self.rudder_x_data+np.linspace(self.x,self.x,2),self.rudder_y_data+np.linspace(self.y,self.y,2))

        self.sail_y_data=np.array([0.8*math.sin(self.heading_angle),
                                0.8*math.sin(self.heading_angle)-2*math.cos(self.sail-math.pi/2+self.heading_angle)])*self.boat_size
        self.sail_x_data=np.array([0.8*math.cos(self.heading_angle),
                                0.8*math.cos(self.heading_angle)+2*math.sin(self.sail-math.pi/2+self.heading_angle)])*self.boat_size
        self.line_sail,=self.main_window.plot(self.sail_x_data+np.linspace(self.x,self.x,2),self.sail_y_data+np.linspace(self.x,self.x,2))
        self.line_disired_angle,=self.main_window.plot([1.5*math.cos(self.heading_angle)*self.boat_size,1.5*math.cos(self.heading_angle)+math.cos(self.desired_angle)*self.boat_size],
                                    [1.5*math.sin(self.heading_angle)*self.boat_size,1.5*math.sin(self.heading_angle)+math.sin(self.desired_angle)*self.boat_size])

    def init_window_data(self):
        self.window_y_data=np.array([0,2.5,2.5,2.5,5,5])
        self.window_x_data=np.array([5.5,5.5,8,5.5,5.5,8])
        self.line_window,=self.main_window.plot(self.window_x_data,self.window_y_data,color='b')

        self.boundary_y_data=np.array([2,2,8,8,2])
        self.boundary_x_data=np.array([0.8,5.5,5.5,0.8,0.8])
        self.line_boundary,=self.main_window.plot(self.boundary_x_data,self.boundary_y_data,color='gray',linestyle='--')

        self.window_boat_y_data=2.5*self.boat_y_data+np.linspace(1.25,1.25,5)
        self.window_boat_x_data=2.5*self.boat_x_data+np.linspace(6.75,6.75,5)
        self.line_win_boat,=self.main_window.plot(self.window_boat_x_data,self.window_boat_y_data)

        self.window_rudder_y_data=1.5*self.rudder_y_data+np.linspace(1.25,1.25,2)
        self.window_rudder_x_data=1.5*self.rudder_x_data+np.linspace(6.75,6.75,2)
        self.line_win_rudder,=self.main_window.plot(self.window_rudder_x_data,self.window_rudder_y_data)

        self.window_sail_y_data=2*self.sail_y_data+np.linspace(1.25,1.25,2)
        self.window_sail_x_data=2*self.sail_x_data+np.linspace(6.75,6.75,2)
        self.line_win_sail,=self.main_window.plot(self.window_sail_x_data,self.window_sail_y_data)


        self.wind_y_data=np.array([3.75,5])
        self.wind_x_data=np.array([6.75,6.75])
        self.line_wind,=self.main_window.plot(self.wind_x_data,self.wind_y_data)

    def init1(self):  # only required for blitting to give a clean slate.
        
        return [self.trajectory_line,self.line_forward_velocity,self.line_side_velocity,self.line_heading,self.line_boat,self.line_rudder,self.line_sail,self.line_win_boat,self.line_win_rudder,self.line_win_sail,
        self.line_wind,self.line_disired_angle,self.line_boundary,self.line_desired_angle,self.line_target_velocity,self.line_points]

    def to_next_moment(self):
        # if gl.get_value('flag'):
            
        self.x=gl.get_value('x')
        self.y= gl.get_value('y')
        self.true_wind=gl.get_value('true_wind')
        self.desired_angle=gl.get_value('desired_angle')
        self.v=gl.get_value('v')
        self.u=gl.get_value('u')
        self.w=gl.get_value('w')
        self.rudder=gl.get_value('rudder')
        self.sail=gl.get_value('sail')
        self.app_wind=[3,-math.pi/2]
        self.heading_angle=gl.get_value('heading_angle')
        self.get_true_sail()
        self.target_v=gl.get_value('target_v')
        # print(self.target_v)

    def get_true_sail(self):
        if math.sin(self.heading_angle-math.pi/2)>0:
            
            self.sail=-self.sail
            
        if self.sign(math.pi/2-self.heading_angle)!=self.sign(math.pi/2-self.heading_angle-self.sail):
            self.sail=math.pi/2-self.heading_angle

    def animate1(self,i):
        
        self.to_next_moment()
        
        self.update_data()
        
        self.update_line_boat()
        
        self.update_window_boat()
        
        self.update_wind()
        

        return [self.trajectory_line,self.line_forward_velocity,self.line_side_velocity,self.line_heading,self.line_boat,self.line_rudder,self.line_sail,self.line_win_boat,self.line_win_sail,self.line_win_rudder,self.line_wind,self.line_disired_angle,self.line_boundary,
        self.line_desired_angle,self.line_target_velocity,self.line_points]

    def update_data(self):
        
        
        
        # print(self.v,u)
        self.location_x_data=np.delete(self.location_x_data,0,0)
        self.location_x_data=np.append(self.location_x_data,[self.x],0)
        self.location_y_data=np.delete(self.location_y_data,0,0)
        self.location_y_data=np.append(self.location_y_data,[self.y],0)
        self.trajectory_line.set_data(self.location_x_data,self.location_y_data)

        self.v_data=np.delete(self.v_data,0,0)
        self.v_data=np.append(self.v_data,[self.v],0)
        self.line_forward_velocity.set_ydata(self.v_data)  # update the data.

        self.target_v_data=np.delete(self.target_v_data,0,0)
        self.target_v_data=np.append(self.target_v_data,[self.target_v],0)
        self.line_target_velocity.set_ydata(self.target_v_data)  # update the data.
        # print(self.target_v)
        
        self.u_data=np.delete(self.u_data,0,0)
        self.u_data=np.append(self.u_data,[self.u],0)
        self.line_side_velocity.set_ydata(self.u_data)  # update the data.
        self.heading_data=np.delete(self.heading_data,0,0)
        self.heading_data=np.append(self.heading_data,[self.heading_angle],0)
        self.line_heading.set_ydata(self.heading_data)
        self.desired_angle_data=np.delete(self.desired_angle_data,0,0)
        self.desired_angle_data=np.append(self.desired_angle_data,[self.desired_angle],0)
        self.line_desired_angle.set_ydata(self.desired_angle_data)

    def update_line_boat(self):
        self.boat_y_data=np.array([-math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            1.5*math.sin(self.heading_angle),
                            math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5,
                            -math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5])*self.boat_size
        self.boat_x_data=np.array([-math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            1.5*math.cos(self.heading_angle),
                            math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5,
                            -math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5])*self.boat_size

       
        self.line_boat, = self.main_window.plot(self.boat_x_data+np.linspace(self.x,self.x,5),self.boat_y_data+np.linspace(self.y,self.y,5),color='b')
        
        self.rudder_y_data=np.array([-math.sin(self.heading_angle),
                                -math.sin(self.heading_angle)-math.cos(self.rudder-math.pi/2+self.heading_angle)])*self.boat_size
        self.rudder_x_data=np.array([-math.cos(self.heading_angle),
                                -math.cos(self.heading_angle)+math.sin(self.rudder-math.pi/2+self.heading_angle)])*self.boat_size
        self.line_rudder,=self.main_window.plot(self.rudder_x_data+np.linspace(self.x,self.x,2),self.rudder_y_data+np.linspace(self.y,self.y,2),color='blue')

        self.sail_y_data=np.array([0.8*math.sin(self.heading_angle),
                                0.8*math.sin(self.heading_angle)-2*math.cos(self.sail-math.pi/2+self.heading_angle)])*self.boat_size
        self.sail_x_data=np.array([0.8*math.cos(self.heading_angle),
                                0.8*math.cos(self.heading_angle)+2*math.sin(self.sail-math.pi/2+self.heading_angle)])*self.boat_size
        self.line_sail,=self.main_window.plot(self.sail_x_data+np.linspace(self.x,self.x,2),self.sail_y_data+np.linspace(self.y,self.y,2),color='blue')
        self.line_disired_angle,=self.main_window.plot([1.5*math.cos(self.heading_angle)*self.boat_size+self.x,1.5*math.cos(self.heading_angle)*self.boat_size+math.cos(self.desired_angle)*self.boat_size+self.x],
                                    [1.5*math.sin(self.heading_angle)*self.boat_size+self.y,1.5*math.sin(self.heading_angle)*self.boat_size+math.sin(self.desired_angle)*self.boat_size+self.y],color='gray')

    def update_window_boat(self):
        try:
            
            points_list=gl.get_value('point_list')
            for i in range(0,4):
                self.points_x[i]=points_list[i][0]
                self.points_y[i]=points_list[i][1]
            self.line_points.set_data(self.points_x,self.points_y)
        except:
            print('!!!!!!!!')
        

        self.window_boat_y_data=2.5*self.boat_y_data+np.linspace(1.25,1.25,5)
        self.window_boat_x_data=2.5*self.boat_x_data+np.linspace(6.75,6.75,5)
        self.line_win_boat,=self.main_window.plot(self.window_boat_x_data,self.window_boat_y_data,color='black')

        self.window_rudder_y_data=1.5*self.rudder_y_data+np.linspace(1.25,1.25,2)
        self.window_rudder_x_data=1.5*self.rudder_x_data+np.linspace(6.75,6.75,2)
        self.line_win_rudder,=self.main_window.plot(self.window_rudder_x_data,self.window_rudder_y_data,color='blue')

        self.window_sail_y_data=2*self.sail_y_data+np.linspace(1.25,1.25,2)
        self.window_sail_x_data=2*self.sail_x_data+np.linspace(6.75,6.75,2)
        self.line_win_sail,=self.main_window.plot(self.window_sail_x_data,self.window_sail_y_data,color='blue')

    def update_wind(self):
        
        coo_wind=[math.cos(self.true_wind[1])*self.true_wind[0],math.sin(self.true_wind[1])*self.true_wind[0]]
        del_x=coo_wind[0]*2*self.boat_size
        del_y=coo_wind[1]*2*self.boat_size
        self.wind_y_data=np.array([3.75,del_y+3.75])
        self.wind_x_data=np.array([6.75,del_x+6.75])
        self.line_wind,=self.main_window.plot(self.wind_x_data,self.wind_y_data,color='black')

    def sign(self,p):
        if p>0:
            return 1
        elif p<0:
            return -1
        else :
            return 0
        
    def plot(self):
        ani = animation.FuncAnimation(
            self.figure, self.animate1, init_func=self.init1, interval=100, blit=True, save_count=50)
    
        plt.show()
        plt.close()

# a=visualazation()
# a.plot()