from __future__ import annotations
from copy import deepcopy
from math import sqrt

from .vector3d import Vector3D

class Quaternion:
  """
  A class representing a Quaternion.

  q = s + v

  where s is a scalar number, v is a vector representing an axis

  ...
  Attributes
  ----------
    s: float
      the scalar number
    v: Vector3D
      the vector representing an axis

  Methods
  ----------
    copy():
      Returns a copy of the quaternion.
    add():
      Returns the result of quaternion addition.
    subtract():
      Returns the result of quaternion subtraction.
    scalar_multiply():
      Returns the result of a quaternion multiplied by a scalar value.
    quaternion_multiply():
      Returns the result of quaternion multiplication.
    norm():
      Returns the norm of the quaternion.
    normalize():
      Returns the normalized quaternion (unit norm).
    conjugate():
      Returns the conjugate of the quaternion.
    inverse():
      Returns the inverse of the quaternion.
  """
  def __init__(self, s: float, v: Vector3D):
    self.s = s
    self.v = v

  def __repr__(self) -> str:
    return f"{self.__class__.__name__} (quaternion={self.s} + {self.v.x}i + {self.v.y}j + {self.v.z}k)"

  def __add__(self, q: Quaternion) -> Quaternion:
    return Quaternion(self.s + q.s, self.v + q.v)

  def __sub__(self, q: Quaternion) -> Quaternion:
    return Quaternion(self.s - q.s, self.v - q.v)

  def __mul__(self, val: int or float or Quaternion) -> Quaternion:
    if isinstance(val, int) or isinstance(val, float):
      return Quaternion(self.s*val, self.v*val)
    elif isinstance(val, Quaternion):
      return Quaternion(
        self.s*val.s - self.v.dot(val.v), 
        val.v*self.s + self.v*val.s + self.v.cross(val.v)
      )
    else:
      raise TypeError(f"{type(k)} is not supported.")

  def copy(self) -> Quaternion:
    """
    Returns a copy of the quaternion.

    Parameters
    ----------
      None

    Returns
    ----------
      (Quaternion) the copied quaternion
    """
    return deepcopy(self)

  def add(self, q: Quaternion) -> Quaternion:
    """
    Returns the result of quaternion addition.

    qa + qb = (sa + sa) + (va + vb) 

    Parameters
    ----------
      q: Quaternion
        the quaternion to be added 

    Returns
    ----------
      (Quaternion) the resulting quaternion
    """
    return Quaternion(self.s + q.s, self.v + q.v)

  def subtract(self, q: Quaternion) -> Quaternion:
    """
    Returns the result of quaternion subtraction.

    Parameters
    ----------
      q: Quaternion
        the quaternion to be subtracted

    Returns
    ----------
      (Quaternion) the resulting quaternion
    """
    return Quaternion(self.s - q.s, self.v - q.v)

  def scalar_multiply(self, s: int or float) -> Quaternion:
    """
    Returns a quaternion multiplied by a scalar value.

    q * s = (qs * s) + (qv * s)

    Parameters
    ----------
      s: int or float
        scaler value to multply by

    Returns
    ----------
      (Quaternion) the resulting quaternion
    """
    return Quaternion(self.s*s, self.v*s)

  def quaternion_multiply(self, q: Quaternion) -> Quaternion:
    """
    Returns the result of quaternion multiplication.

    qa*qb = (sa*sb - va dot vb) + (sa*vb + sb*va + va cross vb)

    Parameters
    ----------
      q: Quaternion
        the quaternion to be multipied

    Returns
    ----------
      (Quaternion) the resulting quaternion
    """
    return Quaternion(
      self.s*q.s - self.v.dot(q.v), 
      q.v*self.s + self.v*q.s + self.v.cross(q.v)
    )

  def norm(self) -> float:
    """
    Returns the norm of the quaternion.

    |q| = sqrt(s^2 + v^2)

    Parameters
    ----------
      None

    Returns
    ----------
      (Quaternion) the norm of the Quaternion
    """
    return sqrt(self.s*self.s + self.v.x * self.v.x + self.v.y * self.v.y + self.v.z * self.v.z)

  def normalize(self) -> Quaternion:
    """
    Returns the normalized quaternion (unit norm).

    qu = q / sqrt(s^2 + v^2)

    Parameters
    ----------
      None

    Returns
    ----------
      (Quaternion) the normalized quaternion
    """
    if self.norm() != 0:
      return Quaternion(self.s * 1/self.norm(), self.v * 1/self.norm())
    else:
      raise ValueError('Unable to normalize as norm value is zero')

  def conjugate(self) -> Quaternion:
    """
    Returns the conjugate of the quaternion.

    q_conj = [s, -v]

        Parameters
    ----------
      None

    Returns
    ----------
      (Quaternion) the conjugated quaternion
    """
    return Quaternion(self.s, self.v * -1)

  def inverse(self) -> Quaternion:
    """
    Returns the inverse of the quaternion.

    q_inv = q_conj / abs(q)^2

        Parameters
    ----------
      None

    Returns
    ----------
      (Quaternion) the inversed quaternion
    """
    q_conj = self.conjugate()
    abs_val = self.norm()

    deno = 1 / (abs_val * abs_val)

    return Quaternion(q_conj.s * deno, q_conj.v * deno)
