import numpy as np


class FFDLcController:
    def __init__(self,Nt=200,N=4,le=1,lu=1,offsets=[0,0,0,0],lambda_=100,gamma=0.01,eta=0.02,mu=0.01,epsilon=1e-3 ,b_phi=50,b_theta=20,
                yd_init=0,ys_init=[0,0],u_init=[0,0,0,0],min_u=-10,max_u=30):
        self.counter=0
        self.Nt=Nt
        self.N=N
        self.k=np.linspace(1,Nt+1,Nt+1)
        self.offsets=offsets
        self.le=le
        self.lu=lu
        self.min_u=min_u
        self.max_u=max_u
        if le-2>lu:
            self.max_leu=le
        else:
            self.max_leu=lu


        ''' weight and step factors '''
        self.lambda_=lambda_
        self.gamma=gamma
        self.eta=eta
        self.mu=mu
        self.epsilon=epsilon
        ''' for bound '''
        self.b_phi=b_phi
        self.b_theta=b_theta


        ''' system and controller initilization'''
        self.yd=np.linspace(yd_init,yd_init,Nt+1)
        self.ys=[ys_init[i]*np.ones((Nt,1)) for i in range(N)]
        self.us=[u_init[i]*np.ones((Nt,1)) for i in range(N)]
        self.dys=[np.zeros((Nt,1)) for i in range(N)]
        self.dus=[np.zeros((Nt,1)) for i in range(N)]

        self.es=[np.zeros((Nt,1)) for i in range(N)]
        for i in range(N):
            self.es[i][0]=self.yd[0]+self.offsets[i]-self.ys[i][0]
            self.es[i][1]=self.yd[1]+self.offsets[i]-self.ys[i][1]
            self.es[i][2]=self.yd[2]+self.offsets[i]-self.ys[i][2]

        self.e=np.zeros((N,Nt))
        for i in range(N): self.e[i][0]=self.es[i][0]
        self.es_hat=[np.zeros((Nt+1,1)) for i in range(N)]

        self.e_hat=np.zeros((N,Nt+1)) 

        self.ksi=np.zeros((N,Nt)) 
        self.dksi=np.zeros((N,Nt))
        self.ksi_hat=np.zeros((N,Nt+1)) 

        self.deltHs=[np.zeros((le+lu,Nt)) for i in range(N)]


        '''controller initilization'''
        self.phis=[np.zeros((Nt,1)) for i in range(N)]
        for i in range(N): self.phis[i][0]=0.5

        self.thetas=[-np.ones((le+lu,Nt+1))*0.01 for i in range(N)] 

        '''communication topology'''
        self.L=np.array([[2, -1, -1,  0],
                        [0,  1,  0, -1],
                        [-1,  0,  1,  0],
                        [0, -1, -1,  2]])
        self.D=np.diag([1, 0, 0, 1])


        for k in range(Nt):
            self.ksi[:,k]=np.matmul((self.L+self.D),self.e[:,k])


    def PPD_DEstimator(self,i):
        
        dy1=self.dys[i][self.counter]
        du1=self.dus[i][self.counter-1]
        phi1=self.phis[i][self.counter-1]

        newphi=phi1+self.eta*(dy1-phi1*du1)*du1/(self.mu+du1**2)

        if newphi<self.epsilon:
            newphi=self.epsilon
        elif newphi>self.b_phi:
            newphi=self.b_phi
        
        
        return newphi

    def FFDLc_DCC_controller(self,i):
        
        u=self.us[i][self.counter-1]
        ksi_hat=self.ksi_hat[i][self.counter+1]
        deltH=self.deltHs[i][:,self.counter]
        phi=self.phis[i][self.counter]
        theta=self.thetas[i][:,self.counter]
        lth=len(theta)
        newtheta=theta+self.gamma*(phi*ksi_hat-np.matmul(self.lambda_*theta.T,deltH) )*deltH/( (self.lambda_+phi**2)*np.linalg.norm(deltH)**2+self.epsilon )

        for j in range (lth):
            if newtheta[j]<-self.b_theta:
                newtheta[j]=-self.b_theta
            elif newtheta[j]>-self.epsilon:
                newtheta[j]=-self.epsilon

        newu=u+np.matmul(theta.T,deltH)
        # if newu<self.min_u: newu=self.min_u
        # elif newu>self.max_u: newu=self.min_u

        return newu,newtheta




    def compute_u(self,new_yd,new_ys):

        self.counter+=1
        if self.counter+1>self.Nt:
            results=self.compute_u_maximum_arr(new_yd,new_ys)
            return results
        self.yd[self.counter+1]=new_yd

        #update data
        for i in range(self.N): 
            self.ys[i][self.counter]=new_ys[i]
            self.es[i][self.counter]=self.yd[self.counter]+self.offsets[i]-self.ys[i][self.counter]
            

        self.e[:,self.counter]=np.array([self.es[0][self.counter][0],self.es[1][self.counter][0],self.es[2][self.counter][0],self.es[3][self.counter][0]])
        self.ksi[:,self.counter]=np.matmul((self.L+self.D),self.e[:,self.counter])
        self.dksi[:,self.counter]=self.ksi[:,self.counter]-self.ksi[:,self.counter-1]
        
        for i in range(self.N): self.dys[i][self.counter]=self.ys[i][self.counter]-self.ys[i][self.counter-1]
        if self.counter>1:
            for i in range(self.N): self.dus[i][self.counter-1]=self.us[i][self.counter-1]-self.us[i][self.counter-2]
        
        for j in range(self.le+self.lu):
            if j==0:
                for i in range(self.N):
                    self.deltHs[i][j][self.counter]=-self.ksi[i,self.counter+j]   ########## Need further check

            elif j<=self.le-1:
                for i in range(self.N):
                    self.deltHs[i][j][self.counter]=-self.dksi[i][self.counter-j]

            else:
                self.deltHs[i][j][self.counter]=-self.dus[i][self.counter-j-1+self.le]


        #compute new u
        for i in range(self.N): self.phis[i][self.counter]=self.PPD_DEstimator(i)
        for i in range(self.N): self.es_hat[i][self.counter+1]=self.yd[self.counter+1]+self.offsets[i]-self.ys[i][self.counter]\
                                                        -np.matmul(self.phis[i][self.counter]*self.thetas[i][:,self.counter].T,self.deltHs[i][:,self.counter])
        
        self.e_hat[:,self.counter+1]=np.array([self.es_hat[i][self.counter+1][0] for i in range(self.N)])
        self.ksi_hat[:,self.counter+1]=np.matmul((self.L+self.D),self.e_hat[:,self.counter+1])
        for i in range(self.N): self.us[i][self.counter],self.thetas[i][:,self.counter+1]=self.FFDLc_DCC_controller(i)

        return [self.us[i][self.counter] for i in range(self.N)]


    def compute_u_maximum_arr(self,new_yd,new_ys):

        self.counter-=1
        for i in range(self.N): 
            self.ys[i]=np.delete(self.ys[i],0,axis=0)
            self.es[i]=np.delete(self.es[i],0,axis = 0)
            self.dys[i]=np.delete(self.dys[i],0,axis = 0)
            self.dus[i]=np.delete(self.dus[i],0,axis = 0)
            self.phis[i]=np.delete(self.phis[i],0,axis = 0)
            self.es_hat[i]=np.delete(self.es_hat[i],0,axis = 0)
            self.us[i]=np.delete(self.us[i],0,axis = 0)
        self.yd=np.delete(self.yd,0)
        self.e=np.delete(self.e,0,axis = 1)
        self.ksi=np.delete(self.ksi,0,axis = 1)
        self.dksi=np.delete(self.dksi,0,axis = 1)
        self.e_hat=np.delete(self.e_hat,0,axis = 1)
        self.ksi_hat=np.delete(self.ksi_hat,0,axis = 1)

        for i in range(self.N):
            self.deltHs[i]=np.delete(self.deltHs[i],0,axis=1)


        self.yd=np.hstack((self.yd,new_yd))
        #update data
        for i in range(self.N): 
            # print(self.ys[i],new_ys[i])
            self.ys[i]=np.vstack((self.ys[i],new_ys[i]))
            self.es[i]=np.vstack((self.es[i],self.yd[self.counter]+self.offsets[i]-self.ys[i][self.counter]))

        self.e=np.hstack((self.e,np.array([[self.es[0][self.counter][0]],[self.es[1][self.counter][0]],[self.es[2][self.counter][0]],[self.es[3][self.counter][0]]])))
        self.ksi=np.hstack((self.ksi,np.transpose([np.matmul((self.L+self.D),self.e[:,self.counter])])))
        self.dksi=np.hstack((self.dksi,np.transpose([self.ksi[:,self.counter]-self.ksi[:,self.counter-1]])))
        
        
        for i in range(self.N): 
            self.dys[i]=np.vstack((self.dys[i],self.ys[i][self.counter]-self.ys[i][self.counter-1]))
            self.dus[i]=np.vstack((self.dus[i],self.us[i][self.counter-1]-self.us[i][self.counter-2]))
        
        # print(self.deltHs[0])
        temp=[np.zeros((self.le+self.lu,1)) for i in range(self.N)]
        for j in range(self.le+self.lu):
            if j==0:
                for i in range(self.N):
                    temp[i][j]=-self.ksi[i,self.counter+j]
            elif j<=self.le-1:
                for i in range(self.N):
                    temp[i][j]=-self.dksi[i][self.counter-j]          
            else:
                temp[i][j]=-self.dus[i][self.counter-j-1+self.le]
        
        for i in range(self.N): 
            self.deltHs[i]=np.hstack((self.deltHs[i],temp[i]))

        #compute new u
        for i in range(self.N): self.phis[i]=np.vstack((self.phis[i],self.PPD_DEstimator(i)))
        for i in range(self.N): 
            self.es_hat[i]=np.vstack((self.es_hat[i],self.yd[self.counter+1]+self.offsets[i]-self.ys[i][self.counter]\
                                    -np.matmul(self.phis[i][self.counter]*self.thetas[i][:,self.counter].T,self.deltHs[i][:,self.counter])))

        self.e_hat=np.hstack((self.e_hat,np.array([[self.es_hat[i][self.counter+1][0] for i in range(self.N)]]).T))
        self.ksi_hat=np.hstack((self.ksi_hat,np.array([np.matmul((self.L+self.D),self.e_hat[:,self.counter+1])]).T))

        for i in range(self.N): 
            temp1,temp2=self.FFDLc_DCC_controller(i)
            
            self.us[i]=np.vstack((self.us[i],temp1))
            self.thetas[i]=np.hstack((self.thetas[i],np.array([temp2]).T))
        
        return [self.us[i][self.counter] for i in range(self.N)]

