from simulator import simulator
from sailboat_v3 import sailboat
import math
my_controllers=[sailboat(position=[1,1,0,0],true_wind=[1.5,-math.pi/2])] 
a=simulator(my_controllers,config_file="config/test.txt")
a.run()
