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
class simulator:
    def __init__(self,controllers=[sailboat(),sailboat(),sailboat(),sailboat(),sailboat()],
                    observer=None,config_file="config/default.txt"):
        with open(config_file, "r") as f:
            self.boat_types=ast.literal_eval(re.split(r'#',f.readline())[0])
            self.poses=np.array(ast.literal_eval(re.split(r'#',f.readline())[0]))
            self.twists=np.array(ast.literal_eval(re.split(r'#',f.readline())[0]))
            self.components=np.array(ast.literal_eval(re.split(r'#',f.readline())[0]))
            self.commands=np.array(ast.literal_eval(re.split(r'#',f.readline())[0]))
            self.true_wind=np.array(ast.literal_eval(re.split(r'#',f.readline())[0]))
            self.total_step=int(re.split(r'#',f.readline())[0])
            self.command_cycle=float(re.split(r'#',f.readline())[0])
            self.simulation_cycle=float(re.split(r'#',f.readline())[0])
            self.GUI_cycle=float(re.split(r'#',f.readline())[0])
            self.save=bool(re.split(r'#',f.readline())[0])
            self.experiment=bool(re.split(r'#',f.readline())[0])
            self.GUI_EN=bool(re.split(r'#',f.readline())[0])

        self.N=len(self.boat_types)
        self.stop_signal=False
        self.counter=0
        self.controller=controllers
        self.observer=observer
        self.dynamic_models=[four_DOF_simulator.single_sailboat_4DOF_simulator(location_and_orientation=self.poses[i],
                                boat_type=self.boat_type[i],sample_time=self.simulation_cycle) for i in range(self.N)]
        self.GUI=GUI.scene_displayer(N=self.N,poses=self.poses,cycle=self.GUI_cycle,boat_type=self.boat_types)
        self.data_writer=data_writer.data_writer(cycle=self.command_cycle,mission="position keeping")

        

        

        
        