from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd


class SequenceTransformer(BaseEstimator, TransformerMixin):
	"""
    Transformer that converts tabular time-series data into sequences.

    This transformer creates sliding window sequences from time-series data,
    which is the required input format for LSTM and other recurrent neural
    networks. Each sequence contains `timesteps` consecutive time points.

    The transformer follows the scikit-learn API, making it compatible with
    pipelines and other scikit-learn utilities.

    Attributes:
        timesteps (int): Number of time steps to include in each sequence.
            Each sequence will contain `timesteps` consecutive rows.
    """

	def __init__(self, timesteps=7):
		"""
        Initialize the SequenceTransformer.

        Args:
            timesteps (int, optional): Number of time steps to include in each
                sequence. Defaults to 7. Must be a positive integer.

        Note:
            The number of output sequences will be `len(X) - timesteps`,
            as the first `timesteps` rows are needed to form the first sequence.
        """
		self.timesteps = timesteps

	def fit(self, X, y=None):
		"""
        Fit the transformer (no-op for this transformer).

        This transformer is stateless and doesn't require fitting. This method
        exists for scikit-learn API compatibility and returns self.

        Args:
            X (pd.DataFrame or array-like): Input time-series data. Shape should
                be (n_samples, n_features). Not used in fitting.
            y (None): Ignored. Present for API consistency.

        Returns:
            self: Returns the instance itself.
        """
		return self

	def transform(self, X):
		"""
        Transform time-series data into sequences.

        Creates sliding window sequences from the input data. Each sequence
        contains `timesteps` consecutive rows, starting from index `timesteps`.

        Args:
            X (pd.DataFrame): Input time-series data with shape (n_samples, n_features).
                Must have at least `timesteps` rows.

        Returns:
            np.ndarray: Array of sequences with shape (n_samples - timesteps, timesteps, n_features).
                Each sequence contains `timesteps` consecutive time points.

        Raises:
            ValueError: If `X` has fewer rows than `timesteps`.
            TypeError: If `X` is not a pandas DataFrame or array-like.

        Note:
            - The first `timesteps` rows of the input are not included in any
              sequence, as they are needed to form the first complete sequence
            - The output shape is (n_samples - timesteps, timesteps, n_features)

        Example:
            >>> transformer = SequenceTransformer(timesteps=3)
            >>> data = pd.DataFrame([[1], [2], [3], [4], [5]])
            >>> sequences = transformer.transform(data)
            >>> print(sequences.shape)  # (3, 3, 1)
            >>> print(sequences[0])  # [[1], [2], [3]]
        """
		if len(X) < self.timesteps:
			raise ValueError(
				f"Input data has {len(X)} rows, but timesteps={self.timesteps}. "
				f"Need at least {self.timesteps} rows to create sequences."
			)

		X_seq = []
		for i in range(self.timesteps, len(X)):
			X_seq.append(X.iloc[i - self.timesteps:i].values)
		return np.array(X_seq)