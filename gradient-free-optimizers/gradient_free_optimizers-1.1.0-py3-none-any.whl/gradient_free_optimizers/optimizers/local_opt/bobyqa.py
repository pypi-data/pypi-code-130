# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

from ..smb_opt.smbo import SMBO
from ...search import Search

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


class BoundOptimizationByQuadraticApproximation(SMBO, Search):
    def __init__(self):
        pass

    def training(self):
        X_poly = PolynomialFeatures(degree=2, include_bias=False)
        poly_features = X_poly.fit_transform(self.X_sample.reshape(-1, 1))

        linear_reg = LinearRegression()
        linear_reg.fit(poly_features, self.Y_sample)

    @SMBO.track_nth_iter
    @SMBO.track_X_sample
    def iterate(self):
        pass
