import math

from shapely.geometry import LineString
from shapely.ops import clip_by_rect, unary_union

from pyroll.core import Profile, RollPass
from pyroll.core.shapes import rectangle


@RollPass.InProfile.hookimpl
def intersections(roll_pass: RollPass, profile: Profile):
    upper_intersections = roll_pass.in_profile.upper_contour_line.intersection(roll_pass.upper_contour_line)
    lower_intersections = roll_pass.in_profile.lower_contour_line.intersection(roll_pass.lower_contour_line)

    return unary_union([upper_intersections, lower_intersections])


@RollPass.hookimpl
def upper_left_intersection_point(roll_pass: RollPass):
    for point in roll_pass.in_profile.intersections.geoms:
        if point.x < 0 < point.y:
            return point


@RollPass.hookimpl
def upper_right_intersection_point(roll_pass: RollPass):
    for point in roll_pass.in_profile.intersections.geoms:
        if point.x > 0 and point.y > 0:
            return point


@RollPass.hookimpl
def lower_right_intersection_point(roll_pass: RollPass):
    for point in roll_pass.in_profile.intersections.geoms:
        if point.x > 0 > point.y:
            return point


@RollPass.hookimpl
def lower_left_intersection_point(roll_pass: RollPass):
    for point in roll_pass.in_profile.intersections.geoms:
        if point.x < 0 and point.y < 0:
            return point


@RollPass.hookimpl
def left_lendl_width_boundary(roll_pass: RollPass):
    return LineString([roll_pass.upper_left_intersection_point, roll_pass.lower_left_intersection_point])


@RollPass.hookimpl
def right_lendl_width_boundary(roll_pass: RollPass):
    return LineString([roll_pass.upper_right_intersection_point, roll_pass.lower_right_intersection_point])


@RollPass.hookimpl
def lendl_width(roll_pass: RollPass):
    return roll_pass.left_lendl_width_boundary.distance(roll_pass.right_lendl_width_boundary)


@RollPass.hookimpl
def lendl_initial_area(roll_pass: RollPass):
    return clip_by_rect(
        roll_pass.in_profile.cross_section, -roll_pass.lendl_width / 2,
        -math.inf, roll_pass.lendl_width / 2, math.inf).area


@RollPass.hookimpl
def lendl_final_area(roll_pass: RollPass):
    return clip_by_rect(
        roll_pass.out_profile.cross_section, -roll_pass.lendl_width / 2,
        -math.inf, roll_pass.lendl_width / 2, math.inf).area


@RollPass.InProfile.hookimpl(specname="equivalent_rectangle")
def in_equivalent_rectangle(roll_pass: RollPass, profile: Profile):
    eq_width = profile.width
    eq_height = roll_pass.lendl_initial_area / roll_pass.lendl_width

    return rectangle(eq_width, eq_height)


@RollPass.OutProfile.hookimpl(specname="equivalent_rectangle")
def out_equivalent_rectangle(roll_pass: RollPass, profile: Profile):
    eq_width = profile.width
    eq_height = roll_pass.lendl_final_area / roll_pass.lendl_width

    return rectangle(eq_width, eq_height)
