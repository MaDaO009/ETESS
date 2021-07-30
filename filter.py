import numpy as np



from pykalman import KalmanFilter


class filter():
    def __init__(self):
        self.observation_matrix = np.eye(2) + random_state.randn(2, 2) * 0.1
        self.transition_matrix = [[1, 0.1], [0, 1]]
        self.transition_offset = [-0.1, 0.1]
        self.observation_offset = [1.0, -1.0]
        self.transition_covariance = np.eye(2)
        self.observation_covariance = np.eye(2) + random_state.randn(2, 2) * 0.1
        self.initial_state_mean = [5, -5]
        self.initial_state_covariance = [[1, 0.1], [-0.1, 1]]
        self.random_state = np.random.RandomState(0)
# specify parameters



    def update(self,)
















# sample from model

kf = KalmanFilter(

    self.transition_matrix, self.observation_matrix, self.transition_covariance,

    self.observation_covariance, self.transition_offset, self.observation_offset,

    self.initial_state_mean, self.initial_state_covariance,

    random_state=random_state

)

states, observations = kf.sample(

    n_timesteps=50,

    initial_state=initial_state_mean

)



# estimate state with filtering and smoothing

# filtered_state_estimates = kf.filter(observations)[0]

smoothed_state_estimates = kf.smooth(observations)[0]