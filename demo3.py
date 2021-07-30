from simulator import simulator
from controller.rudder_boat_controller import easy_controller
import math
my_controllers=[easy_controller() for i in range(5)] 
a=simulator(my_controllers,config_file="config/default.txt")
a.run()