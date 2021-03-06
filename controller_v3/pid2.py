'''
Updated on THU DEC 28 9:13:48 2018

@author: Zeyuan Feng

The parameters of PID object are for the angle in rads instead of in degrees.
To use it, you can call the method update(current angle, goal angle) and get the output (rudder angle).
'''
import time

class PID:
    """PID Controller
    """

    def __init__(self, P=0.45, I=0.2, D=0.3,minimum=-0.7,maximum=0.7,SetPoint=0):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.min=minimum
        self.max=maximum
        self.SetPoint=SetPoint
        self.ITerm_max=0.25
        self.DTerm_max=0.4

        self.sample_time = 0.1
        self.current_time = time.time()
        self.last_time = self.current_time
        self.windup_guard=120
        self.clear()

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
        
        lastpoint=self.SetPoint
      
        #     lastpoint=0
        self.SetPoint=SetPoint
        self.PTerm = 0.0
        if lastpoint!=SetPoint:
            newITerm = self.ITerm/abs(lastpoint-self.SetPoint)*5
            if newITerm<self.ITerm:
                self.ITerm=newITerm
            self.DTerm = 0.0
    def update(self, feedback_value,newPoint):
        """Calculates PID value for given reference feedback
        .. math::
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        .. figure:: images/pid_1.png
           :align:   center
           Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)
        """
        
        error = newPoint - feedback_value
        # print('error',error)
        
        # self.current_time = time.time()
        # delta_time = self.current_time - self.last_time
        if self.if_start==0:
            delta_error=0
            self.if_start=1
        else:
            delta_error = error - self.last_error

        # if (delta_time >= self.sample_time):
        self.PTerm = self.Kp * error
        self.ITerm += error * self.sample_time

        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard
        # print(' ITERM',self.ITerm,end=' ')
        self.DTerm = 0.0
        self.DTerm = delta_error /self.sample_time
        if abs(self.SetPoint-newPoint)>0.5:
            self.ITerm=0
            # self.DTerm=0
            
        self.SetPoint=newPoint
        # Remember last time and last error for next calculation
        # self.last_time = self.current_time
        self.last_error = error
        if self.ITerm>self.ITerm_max:
            self.ITerm=self.ITerm_max
        elif self.ITerm<-self.ITerm_max:
            self.ITerm=-self.ITerm_max
        if self.DTerm>self.DTerm_max:
            self.DTerm=self.DTerm_max
        elif self.DTerm<-self.DTerm_max:
            self.DTerm=-self.DTerm_max
        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
        
        if self.output>self.max:
            self.output=self.max
        elif self.output<self.min:
            self.output=self.min
        # print(self.ITerm*self.Ki,self.PTerm,self.DTerm*self.Kd,self.output)
        return self.output

        def setKp(self, proportional_gain):
            """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
            self.Kp = proportional_gain

        def setKi(self, integral_gain):
            """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
            self.Ki = integral_gain

        def setKd(self, derivative_gain):
            """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
            self.Kd = derivative_gain

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time

        
    def setBoundary(self,maximum,minimum):
        self.max=maximum
        self.min=minimum
        
    def setPerameter(self,P,I,D):
        self.Kp=P
        self.Ki = I
        self.Kd = D