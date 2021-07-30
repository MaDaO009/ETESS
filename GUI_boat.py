import pywavefront
import numpy as np

class boat:
    def __init__(self,pose=[0,0,0,0],components=[0,0],boat_type="sailboat"):
        self.boat_type=boat_type
        self.boat = pywavefront.Wavefront('obj/boat.obj', collect_faces=True)
        self.scaled_size   = 1
        self.boat_color=[0.5,0.5,0.5]
        self.sail_color=[0.8,0.9,1]
        self.rudder_color=[0.8,0.9,1]

        self.boat_scale,self.boat_trans=self.init_obj(self.boat,'boat')

        self.rudder_obj=pywavefront.Wavefront('obj/rudder.obj', collect_faces=True)
        self.rudder_scale, self.rudder_trans =  self.init_obj(self.rudder_obj,'rudder')
        self.rudder_pos=+np.array([-130,0,0])

        self.sail_obj=pywavefront.Wavefront('obj/sail.obj', collect_faces=True)
        self.sail_scale, self.sail_trans =  self.init_obj(self.sail_obj,'sail')
        self.sail_pos=np.array([0,0,0])
        self.pose=np.array(pose)
        self.components=components


    def init_obj(self,obj,name):
        box = (obj.vertices[0], obj.vertices[0])
        for vertex in obj.vertices:
            min_v = [min(box[0][i], vertex[i]) for i in range(3)]
            max_v = [max(box[1][i], vertex[i]) for i in range(3)]
            box = (min_v, max_v)
        # if name=='boat' or 'sail':
        box[0][2]-=box[1][2]
        box[1][2]=0

        boat_size     = [box[1][i]-box[0][i] for i in range(3)]
        max_boat_size = max(boat_size)
        
        scale    = np.array([self.scaled_size/max_boat_size for i in range(3)])
        
        trans    = np.array([-(box[1][i]+box[0][i])/2 for i in range(3)])
        if name=='rudder':
            scale    = np.array([self.scaled_size/max_boat_size/2 for i in range(3)])
            trans[0]=box[1][0]
        if name=='sail':
            trans[0]=box[1][0]

        return scale,trans