import time

class PID:
    """PID Controller
    """

    def __init__(self, P=1, I=0, D=0,minimum=-3,maximum=3,SetPoint=0,sample_time=0.01,if_print=False):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.min=minimum
        self.max=maximum
        self.SetPoint=SetPoint
        self.ITerm_max=maximum
        self.DTerm_max=maximum/5

        self.sample_time = sample_time
        self.current_time = time.time()
        self.last_time = self.current_time
        self.windup_guard=120
        self.clear()
        self.if_print=if_print

    def clear(self):
        """Clears PID computations and coefficients"""
    
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.if_start=0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 120

        self.output = 0.0

    def setpoint(self,SetPoint):
        # lastpoint=self.SetPoint
        #     lastpoint=0
        self.SetPoint=SetPoint
        # self.PTerm = 0.0
        # if lastpoint!=SetPoint:
        #     newITerm = self.ITerm/abs(lastpoint-self.SetPoint)*5
        #     if newITerm<self.ITerm:
        #         self.ITerm=newITerm
        #     self.DTerm = 0.0
    def update(self, current_y,y_star):
        """Calculates PID value
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        """
        
        error = y_star - current_y
        
        if self.if_start==0:
            delta_error=0
            self.if_start=1
        else:
            delta_error = error - self.last_error
        
        self.last_error = error
        self.PTerm = self.Kp * error
        self.ITerm += error * self.sample_time*self.Ki

        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard

        self.DTerm = 0.0
        self.DTerm = delta_error /self.sample_time
        if abs(self.SetPoint-y_star)>0.3:
            self.ITerm=0
            self.DTerm=0
            
        self.SetPoint=y_star
        if self.ITerm>self.ITerm_max:
            self.ITerm=self.ITerm_max
        elif self.ITerm<-self.ITerm_max:
            self.ITerm=-self.ITerm_max
        if self.DTerm>self.DTerm_max:
            self.DTerm=self.DTerm_max
        elif self.DTerm<-self.DTerm_max:
            self.DTerm=-self.DTerm_max
        self.output = self.PTerm +  self.ITerm + (self.Kd * self.DTerm)
        
        if self.output>self.max:
            self.output=self.max
        elif self.output<self.min:
            self.output=self.min
        
        if self.if_print: print(y_star, current_y,self.PTerm,self.ITerm,self.DTerm,self.output)
        return self.output
        

    def setWindup(self, windup):
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time

        
    def setBoundary(self,maximum,minimum):
        self.max=maximum
        self.min=minimum
        
    def setPerameter(self,P,I,D):
        self.Kp=P
        self.Ki = I
        self.Kd = D