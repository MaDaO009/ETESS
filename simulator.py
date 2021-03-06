from xlsxwriter import workbook
import four_DOF_simulator 
import re
import four_DOF_simulator 
import GUI
import threading
import numpy as np
from time import time,sleep
import math
from sailboat_v3 import sailboat
import data_writer
import ast
import os
import xlrd


class simulator:
    def __init__(self,controllers=[],
                    observer=None,config_file="config/default.txt"):
        with open(config_file, "r") as f:
            self.boat_types=ast.literal_eval(re.split(r'#',f.readline())[0])
            init_poses=ast.literal_eval(re.split(r'#',f.readline())[0])
            self.poses=np.array(init_poses).astype(np.float64)
            self.twists=np.array(ast.literal_eval(re.split(r'#',f.readline())[0])).astype(np.float64)
            self.components=np.array(ast.literal_eval(re.split(r'#',f.readline())[0])).astype(np.float64)
            self.commands=np.array(ast.literal_eval(re.split(r'#',f.readline())[0])).astype(np.float64)
            self.true_wind=np.array(ast.literal_eval(re.split(r'#',f.readline())[0])).astype(np.float64)
            # self.true_wind=[1.5,-math.pi/2]
            self.total_step=int(re.split(r'#',f.readline())[0])
            self.command_cycle=float(re.split(r'#',f.readline())[0])
            self.simulation_cycle=float(re.split(r'#',f.readline())[0])
            self.GUI_cycle=float(re.split(r'#',f.readline())[0])
            self.save=bool(int(re.split(r'#',f.readline())[0]))
            self.experiment=bool(int(re.split(r'#',f.readline())[0]))
            self.GUI_EN=bool(int(re.split(r'#',f.readline())[0]))
            self.leader=bool(int(re.split(r'#',f.readline())[0]))


        self.N=len(self.boat_types)
        self.stop_signal=False
        self.counter=0
        self.replay_counter=3
        # self.controllers=[sailboat(position=self.poses,true_wind=self.true_wind)]
        self.controllers=controllers
        if self.leader:
            self.controllers.poses=init_poses
            self.controllers.N=self.N
            self.controllers.init()
        else:
            for i in range(self.N): 
                self.controllers[i].position=init_poses[i]
                # self.controllers[i].position=self.poses[i]
                self.controllers[i].true_wind=self.true_wind.copy()
        self.observer=observer
        self.dynamic_models=[four_DOF_simulator.single_sailboat_4DOF_simulator(location_and_orientation=self.poses[i],
                                boat_type=self.boat_types[i],sample_time=self.simulation_cycle) for i in range(self.N)]
        self.GUI=GUI.scene_displayer(N=self.N,poses=self.poses,components=self.components,cycle=self.GUI_cycle,boat_type=self.boat_types)
        self.data_writer=data_writer.data_writer(N=self.N,cycle=self.command_cycle,mission="position keeping")


    def update_info_with_GUI(self):
        while (not self.stop_signal):
            self.GUI.update_pose(self.poses,self.twists,self.components,self.stop_signal)
            # print(self.components)
            sleep(self.GUI_cycle)


    def compute_dynamic(self):
        while (not self.stop_signal):
            start_time=time()
            for i in range(self.N):
                self.twists[i],self.poses[i],self.components[i][1]=\
                    self.dynamic_models[i].step(self.poses[i],self.twists[i],
                    self.commands[i], self.true_wind)
                if self.boat_types[i]=='sailboat' or 'rudderboat':
                    self.components[i][0]=self.commands[i][0]
                else:
                    self.components[i]=self.commands[i]
            sleep_time=self.simulation_cycle-(time()-start_time)
            # print(self.controllers[0].position,self.poses[0])
            # print(self.twists[0],self.commands[0],self.components)
            if sleep_time>0:
                sleep(sleep_time)
            
    def compute_command_and_write_data(self):
        while (not self.stop_signal):
            self.counter+=1
            start_time=time()
            if self.leader:
                self.commands=self.controllers.update_state(self.true_wind.copy(),self.poses.copy(),self.twists.copy())
            else:
                for i in range(self.N):
                    self.commands[i]=self.controllers[i].update_state(self.true_wind.copy(),self.poses[i].copy())
            if self.save: self.data_writer.add_data(self.poses,self.twists,self.components,self.true_wind,0,0)
            # if self.counter%10==0: print(self.twists[0],self.controllers[0].velocity,self.commands[0],self.components,self.counter)
            sleep_time=self.command_cycle-(time()-start_time)
            if sleep_time>0:
                sleep(sleep_time)
            if self.counter>self.total_step:
                self.stop_signal=True
                if self.save:
                    self.data_writer.write_data_points()
            
    def non_GUI(self):
        start_time=time()
        if self.command_cycle/self.simulation_cycle<5:
            print("Simulation frequency should be at least 5 times of controller frequency")
        else:
            for i in range(self.total_step):
                for j in range(int(self.command_cycle/self.simulation_cycle)):
                    # Compute dynamics
                    for k in range(self.N):
                        self.twists[k],self.poses[k],self.components[k][1]=\
                            self.dynamic_models[k].step(self.poses[k],self.twists[k],
                            self.commands[k], self.true_wind)
                        if self.boat_types[k]=='sailboat' or 'rudderboat':
                            self.components[k][0]=self.commands[k][0]
                        else:
                            self.components[k]=self.commands[k]
                
                # Compute command
                if self.leader:
                    self.commands=self.controllers.update_state(self.true_wind.copy(),self.poses.copy(),self.twists.copy())
                else:
                    for i in range(self.N):
                        self.commands[i]=self.controllers[i].update_state(self.true_wind.copy(),self.poses[i].copy())
                # Record data
                if self.save: self.data_writer.add_data(self.poses,self.twists,self.components,self.true_wind,0,0)
            print("Simulated %d steps within %0.3f second(s)"%(self.total_step,(time()-start_time)))
            if self.save: self.data_writer.write_data_points()

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
            self.non_GUI()

    def update_GUI_replay(self,sleep_time):
        nrows = self.tables[0].nrows
        while (not self.stop_signal):
            self.poses=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(1,5)] for i in range(self.N)]).astype(np.float64)
            self.twists=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(5,9)] for i in range(self.N)]).astype(np.float64)
            self.commands=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(9,11)] for i in range(self.N)]).astype(np.float64)
            self.GUI.update_pose(self.poses,self.twists,self.components,self.stop_signal)
            self.replay_counter+=1
            if self.replay_counter==nrows:
                self.stop_signal=False
                return
            sleep(sleep_time)

    def replay(self,path,sleep_time):
        filelist=[]
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                str=os.path.join(root, name)
                
                if str.split('.')[-1]=='xlsx':
                    str=str.replace('\\','/')
                    filelist.append(str)
        self.N=len(filelist)
        workbooks = [xlrd.open_workbook(filelist[i]) for i in range(self.N)]   
        self.tables=[workbooks[i].sheets()[0] for i in range(self.N)]

        self.poses=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(1,5)] for i in range(self.N)]).astype(np.float64)
        self.twists=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(5,9)] for i in range(self.N)]).astype(np.float64)
        self.commands=np.array([[self.tables[i].cell(self.replay_counter,k).value for k in range(9,11)] for i in range(self.N)]).astype(np.float64)

        t1 = threading.Thread(target= self.GUI.main) 
        t2 = threading.Thread(target= self.update_GUI_replay,kwargs={'sleep_time':sleep_time})

        t1.start() # start thread 1
        t2.start()
        
        t1.join() # wait for the t1 thread to complete
        self.stop_signal=True
        t2.join()