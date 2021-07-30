
import four_DOF_simulator 
import GUI
import threading
import numpy as np
from time import time,sleep
import math
from sailboat_v3 import sailboat
import data_writer

class simulator:
    def __init__(self,controller=sailboat(),init_pose=np.array([1,1,0,0]),init_v=[0,0,0,0],GUI_EN=True,total_step=1000,
            true_wind=[1.5,-math.pi/2],command_cycle=0.1,simulation_cycle=0.001,GUI_cycle=0.02,sail_command=0,true_sail=0,
            rudder_command=0,save=True,observer=None,experiment=False,boat_type="sailboat"):
        self.controller=sailboat(position=init_pose,true_wind=true_wind)
        self.dynamic_model=four_DOF_simulator.single_sailboat_4DOF_simulator(location_and_orientation=init_pose,
                                                    boat_type=boat_type,sample_time=simulation_cycle)
        self.GUI=GUI.scene_displayer(pos_and_orientation=init_pose,cycle=GUI_cycle,boat_type=boat_type)
        
        self.counter=0
        self.location_and_orientation=np.array(init_pose)
        self.velocity_and_angular_v=np.array(init_v)
        self.true_sail=true_sail
        self.sail_command=sail_command
        self.rudder_command=rudder_command
        self.GUI_EN=GUI_EN
        self.stop_signal=False
        self.total_step=total_step
        self.command_cycle=command_cycle
        self.simulation_cycle=simulation_cycle
        self.GUI_cycle=GUI_cycle
        self.true_wind=true_wind
        self.data_writer=data_writer.data_writer(cycle=command_cycle,mission="position keeping")
        self.save=save
        self.observer=observer
        self.experiment=experiment

    def update_info_with_GUI(self):
        while (not self.stop_signal):
            self.GUI.update_pose(self.location_and_orientation,self.rudder_command,self.true_sail,self.stop_signal)
            # print(self.rudder_command,self.true_sail)
            sleep(self.GUI_cycle)


    def compute_dynamic(self):
        while (not self.stop_signal):
            start_time=time()
            self.velocity_and_angular_v,self.location_and_orientation,self.true_sail=\
                self.dynamic_model.step(self.location_and_orientation,self.velocity_and_angular_v,
                [self.sail_command,self.rudder_command], self.true_wind)

            sleep_time=self.simulation_cycle-(time()-start_time)

            if sleep_time>0:
                sleep(sleep_time)

        
    def compute_command_and_write_data(self):
        while (not self.stop_signal):
            self.counter+=1
            start_time=time()
            self.rudder_command,self.sail_command,a,b=self.controller.update_state(self.true_wind,self.location_and_orientation)

            self.data_writer.add_data(self.location_and_orientation,self.velocity_and_angular_v,self.sail_command,
                                        self.rudder_command,self.true_wind,0,0)

            sleep_time=self.command_cycle-(time()-start_time)
            if sleep_time>0:
                sleep(sleep_time)
            if self.counter>self.total_step:
                self.stop_signal=True
                if self.save:
                    self.data_writer.write_data_points()



    def run(self):
        if self.GUI_EN:
            t1 = threading.Thread(target= self.GUI.main) 
            t2 = threading.Thread(target= self.update_info_with_GUI)
            if not self.experiment:
                t3 = threading.Thread(target= self.compute_dynamic)
            else:
                t3 = threading.Thread(target= self.observer.run)
            t4 = threading.Thread(target= self.compute_command_and_write_data)

            t1.start() # start thread 1
            t2.start()
            t3.start()
            t4.start()

            t1.join() # wait for the t1 thread to complete
            self.stop_signal=True
            t2.join()
            t3.join()
            t4.join()
        else:
            start_time=time()
            if self.command_cycle/self.simulation_cycle<5:
                print("Simulation frequency should be at least 5 times of controller frequency")
            else:
                for i in range(self.total_step):
                    for j in range(int(self.command_cycle/self.simulation_cycle)):
                        # Compute dynamics
                        self.velocity_and_angular_v,self.location_and_orientation,self.true_sail=\
                            self.dynamic_model.step(self.location_and_orientation,self.velocity_and_angular_v,self.sail_command,\
                                self.rudder_command, self.true_wind)
                    
                    # Compute command
                    self.rudder_command,self.sail_command,a,b=self.controller.update_state(self.true_wind,self.location_and_orientation)
                    # Record data
                    self.data_writer.add_data(self.location_and_orientation,self.velocity_and_angular_v,self.sail_command,
                                                self.rudder_command,self.true_wind,0,0)
                print("Simulated %d steps within %0.3f second(s)"%(self.total_step,(time()-start_time)))
                if self.save: self.data_writer.write_data_points()
            

        
a=simulator(total_step=1000,simulation_cycle=0.01,save=False,boat_type='sailboat')
a.run()
