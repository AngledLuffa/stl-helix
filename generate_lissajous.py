import argparse
import math
import sys

import build_shape
import combine_functions
import extend_function
import marble_path
import slope_function


"""
Implements various curves from section 9.4 of "Practical Handbook of Curve Design and Generation"

A=5, B=0, C=3
time -0.74 .. 0.74
--y_scale 54 --x_scale 40
Kink at the turns.  Ending is not curved but needs an extension to fit the posts

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 40.5 --x_scale 30 --slope_angle 4 --kink_replace_circle "((-0.21,-0.10),(0.10,0.21))" --start_t -0.74 --end_t 0.74 --extra_t 0.69 --tube_start_angle "((-0.1,0),(0.1,-60))"  --tube_end_angle "((-0.1,240),(0.1,180))"

If placed at 0,0, then one 31mm pole goes at (85.41,-3.74), the other at (-8.79,91.56)

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 40.5 --x_scale 30 --slope_angle 4 --kink_replace_circle "((-0.21,-0.10),(0.10,0.21))" --start_t -0.74 --end_t 0.74 --extra_t 0.69 --tube_start_angle 0  --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11

"""


def build_base_x_t(args):
    x_scale = args.x_scale

    def x_t(t):
        x = math.sin((args.lissA / args.lissC) * 2 * math.pi * t + args.lissB * math.pi)
        return x * x_scale

    return x_t

def build_base_y_t(args):
    y_scale = args.y_scale

    def y_t(t):
        y = math.sin(2 * math.pi * t)
        return y * y_scale

    return y_t

def build_time_t(args):
    return extend_function.build_time_t(args.start_t, args.end_t, args.num_time_steps, args)

def build_x_t(args):
    time_t = build_time_t(args)
    base_x_t = build_base_x_t(args)
    return extend_function.extend_f_t(time_t, base_x_t,
                                      args.start_t, args.end_t,
                                      extension_args=args)

    return x_t

def build_y_t(args):
    time_t = build_time_t(args)
    base_y_t = build_base_y_t(args)
    return extend_function.extend_f_t(time_t, base_y_t,
                                      args.start_t, args.end_t,
                                      extension_args=args)

def describe_curve(args):
    print("Building ordinary lissajous curve")
    print("  x(t) = sin((%.4f / %.4f) 2 pi t) + %.4f pi" % (args.lissA, args.lissC, args.lissB))
    print("  y(t) = sin(2 pi t)")


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a lissajous curve or its relatives')

    marble_path.add_tube_arguments(parser, default_slope_angle=10.0, default_output_name='lissajous.stl')
    slope_function.add_overlap_args(parser)
    combine_functions.add_kink_circle_args(parser)
    extend_function.add_extend_args(parser)

    parser.add_argument('--lissA', default=5, type=float,
                        help='value A in the lissajous formula')
    parser.add_argument('--lissB', default=0, type=float,
                        help='value B in the lissajous formula')
    parser.add_argument('--lissC', default=3, type=float,
                        help='value C in the lissajous formula')

    parser.add_argument('--start_t', default=-0.74, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=0.74, type=float,
                        help='Time to end the equation')
    parser.add_argument('--num_time_steps', default=250, type=int,
                        help='Number of time steps in the whole curve')

    # TODO: refactor the scale arguments?
    parser.add_argument('--x_scale', default=40, type=float,
                        help='Scale the shape by this much in the x direction')
    parser.add_argument('--y_scale', default=50, type=float,
                        help='Scale the shape by this much in the y direction')
    parser.add_argument('--scale', default=None, type=float,
                        help='Scale both directions by this much')

    args = parser.parse_args(args=sys_args)

    if args.scale is not None:
        args.x_scale = args.scale
        args.y_scale = args.scale

    return args
    

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

