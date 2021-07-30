import threading
from test2 import scene_displayer

a=scene_displayer()
t1 = threading.Thread(target= a.main) 
    
t1.start() # start thread 1

t1.join() # wait for the t1 thread to complete