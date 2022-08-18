from pyroll.core import RollPass


@RollPass.OutProfile.hookspec
def equivalent_rectangle(roll_pass, profile):
    """Get the dimensions of the equivalent rectangle of the rotated profile."""



