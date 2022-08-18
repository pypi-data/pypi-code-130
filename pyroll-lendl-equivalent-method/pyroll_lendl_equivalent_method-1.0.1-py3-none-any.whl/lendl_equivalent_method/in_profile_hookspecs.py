from pyroll.core import RollPass


@RollPass.InProfile.hookspec
def equivalent_rectangle(roll_pass, profile):
    """Get the dimensions of the equivalent rectangle of the rotated profile."""


@RollPass.InProfile.hookspec
def intersections(roll_pass, profile):
    """Intersection points between incoming profile and groove"""
