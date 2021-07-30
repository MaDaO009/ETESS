from simulator import simulator
from sailboat_v3 import sailboat
import math
my_controllers=[sailboat(position=[i+1,1,0,0],true_wind=[1.5,-math.pi/2]) for i in range(5)] 
a=simulator(my_controllers,config_file="config/default2.txt")
a.run()