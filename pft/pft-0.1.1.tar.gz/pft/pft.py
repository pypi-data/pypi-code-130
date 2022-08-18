"""Extract principal FFT components for features generation"""

# Module imports
import torch
import numpy as np


class PrincipalFFT:
    """Extract principal FFT components for features generation"""
    def __init__(self, n_components, use_torch=True):
        self.n_components = n_components
        self.original_size = 0
        self.idx = None
        self.use_torch = use_torch

    def fit(self, X):
        """Fit data (find the n top components of the FT)"""

        # Selects the correct library
        lib = torch if self.use_torch else np
        vec = torch.tensor if self.use_torch else np.array

        # Extracts top N components from the Fourier Transformation
        Xfft = lib.fft.rfft(X)
        Xabs = lib.abs(Xfft)
        Xsort_idx = lib.sort(Xabs, descending=True)[1]
        self.idx = []
        col = 0
        while len(self.idx) < self.n_components:
            Xtop_idx = lib.unique(
                Xsort_idx[:, col],
                sorted=False,
                return_counts=True,
            )
            max_counts = lib.sort(Xtop_idx[1], descending=True)
            self.idx.append(Xtop_idx[0][max_counts[1]])
            col += 1

        # Stores the most prominent indexes
        self.idx = vec(self.idx[:self.n_components])

        return self

    def transform(self, X):
        """Transform data"""
        assert self.idx is not None, "PrincipalFFT instance not fitted"
        lib = torch if self.use_torch else np
        return lib.abs(lib.fft.rfft(X)[:, self.idx])

    def fit_transform(self, X):
        """Fit and transform"""
        self.fit(X)
        return self.transform(X)
