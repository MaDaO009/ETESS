import numpy as np
import matplotlib.pyplot as plt
from FFDL_DCC_controller_class import FFDLcController
import time
Nt=20000 # total time
N=4 #agent number
k=np.linspace(1,Nt+1,Nt+1)
memory=20000
# controller=FFDLcController(Nt=memory,le=1,lu=2,yd_init=10,xs_init=[1,2,3,4])
# controller=FFDLcController(Nt=memory,le=2,lu=2,yd_init=245,ys_init=[240,240,240,240])
controller=FFDLcController(Nt=memory,le=1,lu=2,yd_init=2,ys_init=[0,0,0,0])
#### constant yd
xd=np.linspace(2,2,Nt+1)
yd=np.linspace(245,245+2*0.01*Nt,Nt+1)
# yd=np.linspace(6,6,Nt+1)+np.sin(np.linspace(0,Nt*0.02*np.pi,Nt+1))
xs=[np.ones((Nt+1,1)),2*np.ones((Nt+1,1)),3*np.ones((Nt+1,1)),4*np.ones((Nt+1,1)) ]
ys=[240*np.ones((Nt+1,1)),240*np.ones((Nt+1,1)),240*np.ones((Nt+1,1)),240*np.ones((Nt+1,1)) ]
us=[np.zeros((Nt,1)) for i in range(N)]


us[0][1],us[1][1],us[2][1],us[3][1]=controller.compute_u(yd[2],[float(ys[i][1]) for i in range(4)])
start_time=time.time()
err=[0 for i in range(N)]
for k in range(1,Nt):
    # Agent model
    #Agent1
    xs[0][k+1]=(xs[0][k-1]*xs[0][k])/(1+xs[0][k-1]**2+xs[0][k]**2)+3*us[0][k]
    ys[0][k+1]=ys[0][k]+xs[0][k]*0.01
    #Agent2
    xs[1][k+1]=(xs[1][k])/(1+xs[1][k]**4)+us[1][k]**3
    ys[1][k+1]=ys[1][k]+xs[1][k]*0.01
    #Agent3
    xs[2][k+1]=(xs[2][k-1]*xs[2][k]*us[2][k-1]+2*us[2][k])/(1+xs[2][k-1]**2+xs[2][k]**2)+us[2][k]**3
    ys[2][k+1]=ys[2][k]+xs[2][k]*0.01
    #Agent4
    xs[3][k+1]=(xs[3][k]*us[3][k])/(1+xs[3][k]**6)+2*us[3][k]
    ys[3][k+1]=ys[3][k]+xs[3][k]*0.01
    
    for i in range (N): err[i]+=abs(yd[k]-ys[i][k])*0.01
    if (k!=Nt-1): us[0][k+1],us[1][k+1],us[2][k+1],us[3][k+1]=controller.compute_u(yd[k+2],[float(ys[i][k+1]) for i in range(4)])

    # if k==30: print(controller.es[0].T)
# print("%0.2f %0.2f %0.2f %0.2f    %0.2f %0.2f %0.2f %0.2f"%(1,25.5,0,0,0,0,0,0))
print((time.time()-start_time))
print("%0.2f %0.2f %0.2f %0.2f "%(err[0],err[1],err[2],err[3]))
# controller.compute_e([float(xs[i][Nt]) for i in range(4)])


t=np.linspace(0,Nt,Nt+1)
line_colors=['b','r','m','g']     
fig, ax = plt.subplots() 
ax.plot(t, yd, color='k',label='yd') 
for i in range(N): ax.plot(t, ys[i], color=line_colors[i],label='Agent%d'%(i+1)) 
ax.legend()
ax.set_title('Tracking performance')
plt.show()

# # t=np.linspace(0,Nt,Nt+1)
# # line_colors=['b','r','m','g']     
# # fig, ax = plt.subplots() 
# # ax.plot(t[memory:], yd[memory:]-6, color='k',label='yd') 
# # for i in range(N): ax.plot(t[memory:]-6, xs[i][memory:]-6, color=line_colors[i],label='Agent%d'%(i+1)) 
# # ax.legend()
# # ax.set_title('Tracking performance')
# # plt.show()

# plt.close()
# fig, ax = plt.subplots() 
# for i in range(N): ax.plot(t[:Nt], controller.phis[i], color=line_colors[i],label='Agent%d'%(i+1)) 
# ax.legend()
# ax.set_title('PPD estimation')
# plt.show()


plt.close()
fig, ax = plt.subplots() 
for i in range(N): ax.plot(t[:Nt], us[i], color=line_colors[i],label='Agent%d'%(i+1)) 
ax.legend()
ax.set_title('Control input')
plt.show()

# # plt.close()
# # fig, ax = plt.subplots() 
# # for i in range(N): ax.plot(t, controller.es[i], color=line_colors[i],label='Agent%d'%(i+1)) 
# # ax.legend()
# # ax.set_title('Tracking error')
# # plt.show()

# # plt.close()
# # fig, ax = plt.subplots() 
# # for i in range(N): ax.plot(t, controller.thetas[i].T, color=line_colors[i],label='Agent%d'%(i+1)) 
# # ax.legend()
# # ax.set_title('Control gain')
# # plt.show()
