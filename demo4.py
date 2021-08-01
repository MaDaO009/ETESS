from simulator import simulator
from controller2.FFDL_controller import FFDL_controller
import math
my_controllers=FFDL_controller()
a=simulator(my_controllers,config_file="config/default4.txt")
a.run()
# a.replay("./data/test",0.02)