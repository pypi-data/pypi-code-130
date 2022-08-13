import argparse
import math
import sys

import ezdxf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="name", type=str, default="box")
    parser.add_argument("-x", "--width", help="box width", type=float, default=200)
    parser.add_argument("-y", "--height", help="box height", type=float, default=70)
    parser.add_argument("-z", "--depth", help="box depth", type=float, default=150)
    parser.add_argument(
        "-t", "--thickness", help="material thickness", type=float, default=4
    )
    parser.add_argument("-l", "--toothlen", help="tooth_len", type=float, default=20)
    parser.add_argument("-r", "--radius", help="dogbones radius", type=float, default=0)
    parser.add_argument(
        "-s", "--scad", help="write scad file", type=bool, default=False
    )
    parser.add_argument("--holes", help="front holes", type=str)
    parser.add_argument("--bholes", help="back holes", type=str)
    args = parser.parse_args()

    width = args.width
    height = args.height
    depth = args.depth
    tooth_len = args.toothlen
    thickness = args.thickness
    rad = args.radius

    alpha = 0.5

    print(f"size: {width} x {height} x {depth}")

    num_tooth_width = (width - (thickness * 4)) / tooth_len / 2 + 0.5
    border_width = num_tooth_width - int(num_tooth_width)
    start_width = border_width * tooth_len + thickness * 2

    num_tooth_height = (height - (thickness * 4)) / tooth_len / 2 + 0.5
    border_height = num_tooth_height - int(num_tooth_height)
    start_height = border_height * tooth_len + thickness * 2

    num_tooth_depth = (depth - (thickness * 4)) / tooth_len / 2 + 0.5
    border_depth = num_tooth_depth - int(num_tooth_depth)
    start_depth = border_depth * tooth_len + thickness * 2

    # front and back
    points_fb = [(0, 0)]
    for n in range(0, int(num_tooth_width)):
        points_fb.append((start_width + n * tooth_len * 2, 0))
        if rad:
            points_fb.append((start_width + n * tooth_len * 2, thickness - rad))
            points_fb.append((start_width + n * tooth_len * 2 + rad, thickness, 1))
            points_fb.append(
                (start_width + n * tooth_len * 2 + tooth_len - rad, thickness)
            )
            points_fb.append(
                (start_width + n * tooth_len * 2 + tooth_len, thickness - rad, 1)
            )
        else:
            points_fb.append((start_width + n * tooth_len * 2, thickness))
            points_fb.append((start_width + n * tooth_len * 2 + tooth_len, thickness))
        points_fb.append((start_width + n * tooth_len * 2 + tooth_len, 0))
    points_fb.append((width, 0))
    for n in range(0, int(num_tooth_height)):
        points_fb.append((width, start_height + n * tooth_len * 2))
        if rad:
            points_fb.append(
                (width - thickness + rad, start_height + n * tooth_len * 2)
            )
            points_fb.append(
                (width - thickness, start_height + n * tooth_len * 2 + rad, 1)
            )
            points_fb.append(
                (width - thickness, start_height + n * tooth_len * 2 + tooth_len - rad)
            )
            points_fb.append(
                (
                    width - thickness + rad,
                    start_height + n * tooth_len * 2 + tooth_len,
                    1,
                )
            )
        else:
            points_fb.append((width - thickness, start_height + n * tooth_len * 2))
            points_fb.append(
                (width - thickness, start_height + n * tooth_len * 2 + tooth_len)
            )
        points_fb.append((width, start_height + n * tooth_len * 2 + tooth_len))
    points_fb.append((width, height))
    for n in range(0, int(num_tooth_width)):
        points_fb.append((width - (start_width + n * tooth_len * 2), height))
        if rad:
            points_fb.append(
                (width - (start_width + n * tooth_len * 2), height - thickness + rad)
            )
            points_fb.append(
                (width - (start_width + n * tooth_len * 2) - rad, height - thickness, 1)
            )
            points_fb.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len) + rad,
                    height - thickness,
                )
            )
            points_fb.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len),
                    height - thickness + rad,
                    1,
                )
            )
        else:
            points_fb.append(
                (width - (start_width + n * tooth_len * 2), height - thickness)
            )
            points_fb.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len),
                    height - thickness,
                )
            )
        points_fb.append(
            (width - (start_width + n * tooth_len * 2 + tooth_len), height)
        )
    points_fb.append((0, height))
    for n in range(0, int(num_tooth_height)):
        points_fb.append((0, height - (start_height + n * tooth_len * 2)))
        if rad:
            points_fb.append(
                (thickness - rad, height - (start_height + n * tooth_len * 2))
            )
            points_fb.append(
                (thickness, height - (start_height + n * tooth_len * 2) - rad, 1)
            )
            points_fb.append(
                (
                    thickness,
                    height - (start_height + n * tooth_len * 2 + tooth_len) + rad,
                )
            )
            points_fb.append(
                (
                    thickness - rad,
                    height - (start_height + n * tooth_len * 2 + tooth_len),
                    1,
                )
            )
        else:
            points_fb.append((thickness, height - (start_height + n * tooth_len * 2)))
            points_fb.append(
                (thickness, height - (start_height + n * tooth_len * 2 + tooth_len))
            )
        points_fb.append((0, height - (start_height + n * tooth_len * 2 + tooth_len)))
    points_fb.append((0, 0))

    # top and bottom
    points_top = [(0, thickness)]
    for n in range(0, int(num_tooth_width)):
        if rad:
            points_top.append((start_width + n * tooth_len * 2 - rad, thickness))
            points_top.append((start_width + n * tooth_len * 2, thickness - rad, 1))
            points_top.append((start_width + n * tooth_len * 2, 0))
            points_top.append((start_width + n * tooth_len * 2 + tooth_len, 0))
            points_top.append(
                (start_width + n * tooth_len * 2 + tooth_len, thickness - rad)
            )
            points_top.append(
                (start_width + n * tooth_len * 2 + tooth_len + rad, thickness, 1)
            )
        else:
            points_top.append((start_width + n * tooth_len * 2, thickness))
            points_top.append((start_width + n * tooth_len * 2, 0))
            points_top.append((start_width + n * tooth_len * 2 + tooth_len, 0))
            points_top.append((start_width + n * tooth_len * 2 + tooth_len, thickness))
    points_top.append((width, thickness))
    for n in range(0, int(num_tooth_depth)):
        points_top.append((width, start_depth + n * tooth_len * 2))
        if rad:
            points_top.append(
                (width - thickness + rad, start_depth + n * tooth_len * 2)
            )
            points_top.append(
                (width - thickness, start_depth + n * tooth_len * 2 + rad, 1)
            )
            points_top.append(
                (width - thickness, start_depth + n * tooth_len * 2 + tooth_len - rad)
            )
            points_top.append(
                (
                    width - thickness + rad,
                    start_depth + n * tooth_len * 2 + tooth_len,
                    1,
                )
            )
        else:
            points_top.append((width - thickness, start_depth + n * tooth_len * 2))
            points_top.append(
                (width - thickness, start_depth + n * tooth_len * 2 + tooth_len)
            )
        points_top.append((width, start_depth + n * tooth_len * 2 + tooth_len))
    points_top.append((width, depth - thickness))
    for n in range(0, int(num_tooth_width)):
        if rad:
            points_top.append(
                (width - (start_width + n * tooth_len * 2) + rad, depth - thickness)
            )
            points_top.append(
                (width - (start_width + n * tooth_len * 2), depth - thickness + rad, 1)
            )
            points_top.append((width - (start_width + n * tooth_len * 2), depth))
            points_top.append(
                (width - (start_width + n * tooth_len * 2 + tooth_len), depth)
            )
            points_top.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len),
                    depth - thickness + rad,
                )
            )
            points_top.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len) - rad,
                    depth - thickness,
                    1,
                )
            )
        else:
            points_top.append(
                (width - (start_width + n * tooth_len * 2), depth - thickness)
            )
            points_top.append((width - (start_width + n * tooth_len * 2), depth))
            points_top.append(
                (width - (start_width + n * tooth_len * 2 + tooth_len), depth)
            )
            points_top.append(
                (
                    width - (start_width + n * tooth_len * 2 + tooth_len),
                    depth - thickness,
                )
            )
    points_top.append((0, depth - thickness))
    for n in range(0, int(num_tooth_depth)):
        if rad:
            points_top.append((0, depth - (start_depth + n * tooth_len * 2)))
            points_top.append(
                (thickness - rad, depth - (start_depth + n * tooth_len * 2))
            )
            points_top.append(
                (thickness, depth - (start_depth + n * tooth_len * 2) - rad, 1)
            )
            points_top.append(
                (thickness, depth - (start_depth + n * tooth_len * 2 + tooth_len) + rad)
            )
            points_top.append(
                (
                    thickness - rad,
                    depth - (start_depth + n * tooth_len * 2 + tooth_len),
                    1,
                )
            )
            points_top.append(
                (0, depth - (start_depth + n * tooth_len * 2 + tooth_len))
            )
        else:
            points_top.append((0, depth - (start_depth + n * tooth_len * 2)))
            points_top.append((thickness, depth - (start_depth + n * tooth_len * 2)))
            points_top.append(
                (thickness, depth - (start_depth + n * tooth_len * 2 + tooth_len))
            )
            points_top.append(
                (0, depth - (start_depth + n * tooth_len * 2 + tooth_len))
            )
    points_top.append((0, thickness))

    # sides
    points_side = [(thickness, thickness)]
    for n in range(0, int(num_tooth_depth)):
        if rad:
            points_side.append((start_depth + n * tooth_len * 2 - rad, thickness))
            points_side.append((start_depth + n * tooth_len * 2, thickness - rad, 1))
            points_side.append((start_depth + n * tooth_len * 2, 0))
            points_side.append((start_depth + n * tooth_len * 2 + tooth_len, 0))
            points_side.append(
                (start_depth + n * tooth_len * 2 + tooth_len, thickness - rad)
            )
            points_side.append(
                (start_depth + n * tooth_len * 2 + tooth_len + rad, thickness, 1)
            )
        else:
            points_side.append((start_depth + n * tooth_len * 2, thickness))
            points_side.append((start_depth + n * tooth_len * 2, 0))
            points_side.append((start_depth + n * tooth_len * 2 + tooth_len, 0))
            points_side.append((start_depth + n * tooth_len * 2 + tooth_len, thickness))
    points_side.append((depth - thickness, thickness))
    for n in range(0, int(num_tooth_height)):
        if rad:
            points_side.append(
                (depth - thickness, start_height + n * tooth_len * 2 - rad)
            )
            points_side.append(
                (depth - thickness + rad, start_height + n * tooth_len * 2, 1)
            )
            points_side.append((depth, start_height + n * tooth_len * 2))
            points_side.append((depth, start_height + n * tooth_len * 2 + tooth_len))
            points_side.append(
                (depth - thickness + rad, start_height + n * tooth_len * 2 + tooth_len)
            )
            points_side.append(
                (
                    depth - thickness,
                    start_height + n * tooth_len * 2 + tooth_len + rad,
                    1,
                )
            )
        else:
            points_side.append((depth - thickness, start_height + n * tooth_len * 2))
            points_side.append((depth, start_height + n * tooth_len * 2))
            points_side.append((depth, start_height + n * tooth_len * 2 + tooth_len))
            points_side.append(
                (depth - thickness, start_height + n * tooth_len * 2 + tooth_len)
            )
    points_side.append((depth - thickness, height - thickness))
    for n in range(0, int(num_tooth_depth)):
        if rad:
            points_side.append(
                (depth - (start_depth + n * tooth_len * 2) + rad, height - thickness)
            )
            points_side.append(
                (depth - (start_depth + n * tooth_len * 2), height - thickness + rad, 1)
            )
            points_side.append((depth - (start_depth + n * tooth_len * 2), height))
            points_side.append(
                (depth - (start_depth + n * tooth_len * 2 + tooth_len), height)
            )
            points_side.append(
                (
                    depth - (start_depth + n * tooth_len * 2 + tooth_len),
                    height - thickness + rad,
                )
            )
            points_side.append(
                (
                    depth - (start_depth + n * tooth_len * 2 + tooth_len) - rad,
                    height - thickness,
                    1,
                )
            )
        else:
            points_side.append(
                (depth - (start_depth + n * tooth_len * 2), height - thickness)
            )
            points_side.append((depth - (start_depth + n * tooth_len * 2), height))
            points_side.append(
                (depth - (start_depth + n * tooth_len * 2 + tooth_len), height)
            )
            points_side.append(
                (
                    depth - (start_depth + n * tooth_len * 2 + tooth_len),
                    height - thickness,
                )
            )
    points_side.append((thickness, height - thickness))
    for n in range(0, int(num_tooth_height)):
        if rad:
            points_side.append(
                (thickness, height - (start_height + n * tooth_len * 2) + rad)
            )
            points_side.append(
                (thickness - rad, height - (start_height + n * tooth_len * 2), 1)
            )
            points_side.append((0, height - (start_height + n * tooth_len * 2)))
            points_side.append(
                (0, height - (start_height + n * tooth_len * 2 + tooth_len))
            )
            points_side.append(
                (
                    thickness - rad,
                    height - (start_height + n * tooth_len * 2 + tooth_len),
                )
            )
            points_side.append(
                (
                    thickness,
                    height - (start_height + n * tooth_len * 2 + tooth_len) - rad,
                    1,
                )
            )
        else:
            points_side.append((thickness, height - (start_height + n * tooth_len * 2)))
            points_side.append((0, height - (start_height + n * tooth_len * 2)))
            points_side.append(
                (0, height - (start_height + n * tooth_len * 2 + tooth_len))
            )
            points_side.append(
                (thickness, height - (start_height + n * tooth_len * 2 + tooth_len))
            )
    points_side.append((thickness, thickness))

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.layers.new(name="top", dxfattribs={"color": 1})
    doc.layers.new(name="bottom", dxfattribs={"color": 2})
    doc.layers.new(name="front", dxfattribs={"color": 3})
    doc.layers.new(name="back", dxfattribs={"color": 4})
    doc.layers.new(name="left", dxfattribs={"color": 5})
    doc.layers.new(name="right", dxfattribs={"color": 6})
    doc.units = ezdxf.units.MM
    for vport in doc.viewports.get_config("*Active"):
        vport.dxf.grid_on = True
        vport.dxf.center = (width * 2, height * 4)

    layers = {
        "front": (points_fb, 0, 0),
        "back": (points_fb, width + 20, 0),
        "top": (points_top, 0, height + 20),
        "bottom": (points_top, width + 20, height + 20),
        "left": (points_side, (width + 20) * 2, 0),
        "right": (points_side, (width + 20) * 2, height + 20),
    }

    for layer, data in layers.items():
        last = (data[0][0][0] + data[1], data[0][0][1] + data[2])
        for point in data[0][1:]:
            new = (point[0] + data[1], point[1] + data[2])
            if len(point) == 2:
                msp.add_line(last, new, dxfattribs={"layer": layer})
            else:
                (
                    center,
                    start_angle,
                    end_angle,
                    radius,
                ) = ezdxf.math.bulge_to_arc(last, new, -1.0)
                msp.add_arc(
                    center=center,
                    radius=radius,
                    start_angle=start_angle * 180 / math.pi,
                    end_angle=end_angle * 180 / math.pi,
                    dxfattribs={"layer": layer},
                )
            last = new

    for layer, holes in {"front": args.holes, "back": args.bholes}.items():
        if not holes:
            continue
        for hole in holes.split(":"):
            if hole[0] == "r":
                size_pos = hole[1:].split("+", 1)
                size = size_pos[0].split("x")
                size_w = float(size[0])
                size_h = float(size[1])
                pos = (width / 2, height / 2)
                if len(size_pos) > 1:
                    pos = size_pos[1].split("+")
                    if len(pos) == 1:
                        pos.append(height / 2 - size_h / 2)
                pos_x = float(pos[0])
                pos_y = float(pos[1])
                if layer == "back":
                    pos_x += width + 20
                msp.add_lwpolyline(
                    (
                        (pos_x, height - pos_y),
                        (pos_x + size_w, height - pos_y),
                        (pos_x + size_w, height - pos_y - size_h),
                        (pos_x, height - pos_y - size_h),
                        (pos_x, height - pos_y),
                    ),
                    dxfattribs={"layer": layer},
                )
            elif hole[0] == "c":
                size_pos = hole[1:].split("+", 1)
                size = size_pos[0].split("x")
                diameter = float(size[0])
                pos = (width / 2, height / 2)
                if len(size_pos) > 1:
                    pos = size_pos[1].split("+")
                    if len(pos) == 1:
                        pos.append(height / 2)
                pos_x = float(pos[0])
                pos_y = float(pos[1])
                if layer == "back":
                    pos_x += width + 20
                msp.add_circle(
                    (pos_x, height - pos_y), diameter / 2, dxfattribs={"layer": layer}
                )

    print(f"writing {args.name}.dxf")
    doc.saveas(f"{args.name}.dxf")

    scad = f"""
$fn = 64;    

width = {width};
height = {height};
depth = {depth};
thickness = {thickness};
alpha = {alpha};

color([1, 0, 0, alpha]) {{
    translate([0, 0, 0]) {{
        rotate([0, 0, 0]) {{
            linear_extrude(height = thickness) {{
                translate([-width - 20, -height - 20, 0]) {{
                    import("box.dxf", layer="bottom");
                }}
            }}
        }}
    }}
}}
color([0, 1, 0, alpha]) {{
    translate([width, depth - thickness, 0]) {{
        rotate([90, 0, 180]) {{
            linear_extrude(height = thickness) {{
                translate([-width - 20, 0, 0]) {{
                    import("box.dxf", layer="back");
                }}
            }}
        }}
    }}
}}
color([0, 0, 1, alpha]) {{
    translate([0, 0, 0]) {{
        rotate([90, 0, 90]) {{
            linear_extrude(height = thickness) {{
                translate([-width * 2 - 20 * 2, 0, 0]) {{
                    import("box.dxf", layer="left");
                }}
            }}
        }}
    }}
}}
color([0, 0, 1, alpha]) {{
    translate([width - thickness, 0, 0]) {{
        rotate([90, 0, 90]) {{
            linear_extrude(height = thickness) {{
                translate([-width * 2 - 20 * 2, 0, 0]) {{
                    import("box.dxf", layer="left");
                }}
            }}
        }}
    }}
}}
color([1, 0, 0, alpha]) {{
    translate([0, 0, height - thickness]) {{
        rotate([0, 0, 0]) {{
            linear_extrude(height = thickness) {{
                translate([0, -height - 20, 0]) {{
                    import("box.dxf", layer="top");
                }}
            }}
        }}
    }}
}}

color([0, 1, 0, alpha]) {{
    translate([0, thickness, 0]) {{
        rotate([90, 0, 0]) {{
            linear_extrude(height = thickness) {{
                translate([0, 0, 0]) {{
                    import("box.dxf", layer="front");
                }}
            }}
        }}
    }}
}}

"""
    if args.scad:
        print(f"writing {args.name}.scad")
        open(f"{args.name}.scad", "w").write(scad)

    return 0


if __name__ == "__main__":
    sys.exit(main())
