from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class SequenceTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, timesteps=7):
        self.timesteps = timesteps

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        x_seq = []
        for i in range(self.timesteps, len(x)):
            x_seq.append(x.iloc[i - self.timesteps:i].values)
        return np.array(x_seq)