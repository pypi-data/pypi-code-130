from pyroll.core import RollPass


@RollPass.hookspec
def upper_left_intersection_point(roll_pass: RollPass):
    """Upper left intersection point between incoming profile and groove"""


@RollPass.hookspec
def upper_right_intersection_point(roll_pass: RollPass):
    """Upper right intersection point between incoming profile and groove"""


@RollPass.hookspec
def lower_right_intersection_point(roll_pass: RollPass):
    """Lower right intersection point between incoming profile and groove"""


@RollPass.hookspec
def lower_left_intersection_point(roll_pass: RollPass):
    """Lower left intersection point between incoming profile and groove"""


@RollPass.hookspec
def left_lendl_width_boundary(roll_pass: RollPass):
    """Line between the left side intersection points"""


@RollPass.hookspec
def right_lendl_width_boundary(roll_pass: RollPass):
    """Line between the right side intersection points"""


@RollPass.hookspec
def lendl_width(roll_pass: RollPass):
    """Distance between left and right boundary"""


@RollPass.hookspec
def lendl_initial_area(roll_pass: RollPass):
    """Initial Lendl area"""


@RollPass.hookspec
def lendl_final_area(roll_pass: RollPass):
    """Final Lendl area"""
