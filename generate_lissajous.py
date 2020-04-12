import argparse
import math
import sys

import build_shape
import combine_functions
import marble_path
import slope_function


"""
Implements various curves from section 9.4 of "Practical Handbook of Curve Design and Generation"

A=5, B=0, C=3
time -0.74 .. 0.74
--y_scale 54 --x_scale 40
same general issue, kink at the turns.  Ending is not curved but needs an extension to fit the posts

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 54 --x_scale 40 --slope_angle 4 --kink_replace_circle "((-0.21,-0.10),(0.10,0.21))" --start_t -0.74 --end_t 0.74
"""

def build_time_t(args):
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps

    return time_t

def build_x_t(args):
    time_t = build_time_t(args)
    def x_t(time_step):
        t = time_t(time_step)
        x = math.sin((args.lissA / args.lissC) * 2 * math.pi * t + args.lissB * math.pi)
        return x * args.x_scale

    return x_t

def build_y_t(args):
    time_t = build_time_t(args)
    def y_t(time_step):
        t = time_t(time_step)
        y = math.sin(2 * math.pi * t)
        return y * args.y_scale    

    return y_t

def describe_curve(args):
    print("Building ordinary lissajous curve")
    print("  x(t) = sin((%.4f / %.4f) 2 pi t) + %.4f pi" % (args.lissA, args.lissC, args.lissB))
    print("  y(t) = sin(2 pi t)")

def print_stats(x_t, y_t, num_time_steps):
    x0 = x_t(0)
    y0 = y_t(0)
    xn = x_t(num_time_steps)
    yn = y_t(num_time_steps)
    print("Start of the curve: (%.4f, %.4f)" % (x0, y0))
    print("End of the curve:   (%.4f, %.4f)" % (xn, yn))
    dist = ((xn - x0) ** 2 + (yn - y0) ** 2) ** 0.5
    print("Distance: %.4f" % dist)


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a lissajous curve or its relatives')

    marble_path.add_tube_arguments(parser, default_slope_angle=10.0, default_output_name='lissajous.stl')
    slope_function.add_overlap_args(parser)
    combine_functions.add_kink_circle_args(parser)

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
    args = parse_args(sys_args)
    marble_path.print_args(args)

    module = sys.modules[__name__]

    marble_path.write_stl(build_shape.generate_shape(module, args), args.output_name)

if __name__ == '__main__':
    main()

