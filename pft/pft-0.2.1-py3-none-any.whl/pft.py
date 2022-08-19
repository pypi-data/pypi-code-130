"""Extract principal FFT components for features generation"""

# Module imports
import torch
import numpy as np


class PFT:
    """Extract principal FFT components for features generation"""
    def __init__(self, n_components, use_torch=True, norm="ortho"):
        self.n_components = n_components
        self.original_size = 0
        self.idx = None
        self.use_torch = use_torch
        self.norm = norm

    def fit(self, X):
        """Fit data (find the n top components of the FT)"""

        # Selects the correct library
        lib = torch if self.use_torch else np
        vec = torch.tensor if self.use_torch else np.array

        # Extracts top N components from the Fourier Transformation
        Xfft = lib.fft.rfft(X, norm=self.norm)
        self.original_size = Xfft.shape[1]
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

    def rfft(self, freq):
        """Reconstructs the real Fourier transform for frequency values"""
        assert self.idx is not None, "PrincipalFFT instance not fitted"
        lib = torch if self.use_torch else np

        rfft = lib.zeros((freq.shape[0], self.original_size), dtype=torch.complex64)
        rfft[:, self.idx] = freq

        return rfft

    def ifit(self, freq, t):
        """Returns the transient signal from principal Fourier coefficients"""
        assert self.idx is not None, "PrincipalFFT instance not fitted"
        lib = torch if self.use_torch else np

        rfft = self.rfft(freq)

        return  lib.fft.irfft(rfft, len(t), norm=self.norm)

    def transform(self, X):
        """Transform data"""
        assert self.idx is not None, "PrincipalFFT instance not fitted"
        lib = torch if self.use_torch else np
        return lib.fft.rfft(X, norm=self.norm)[:, self.idx]
