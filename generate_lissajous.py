import argparse
import math
import sys

from enum import Enum

import build_shape
import combine_functions
import extend_function
import marble_path
import regularization
import slope_function


"""
Implements various curves from section 9.4 of "Practical Handbook of Curve Design and Generation"

Basic Pretzel
-------------

A=5, B=0, C=3
time -0.74 .. 0.74
--y_scale 54 --x_scale 40
Kink at the turns.  Ending is not curved but needs an extension to fit the posts

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 40.5 --x_scale 30 --slope_angle 4 --kink_replace_circle "((-0.21,-0.10),(0.10,0.21))" --start_t -0.74 --end_t 0.74 --extra_t 0.69 --tube_start_angle "((-0.1,0),(0.1,-60))"  --tube_end_angle "((-0.1,240),(0.1,180))"

If placed at 0,0, then one 31mm pole goes at (85.41,-3.74), the other at (-8.79,91.56)

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 40.5 --x_scale 30 --slope_angle 4 --kink_replace_circle "((-0.21,-0.10),(0.10,0.21))" --start_t -0.74 --end_t 0.74 --extra_t 0.69 --tube_start_angle 0  --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11

TODO: Lissajous Crossover
-------------------

# To get exactly horizontal:
python generate_lissajous.py --lissajous SUM_HARMONICS --lissA 1 --lissB 0.5 --lissC 1 --lissD 0 --lissN 3 --x_scale 82.055 --y_scale 87.038 --slope_angle 4 --start_t 0.0979574 --end_t 0.4020426


python generate_lissajous.py --lissajous SUM_HARMONICS --lissA 1 --lissB 0.5 --lissC 1 --lissD 0 --lissN 3 --x_scale 87 --y_scale 88.5 --slope_angle 2.9 --start_t 0.11 --end_t 0.39

Lissajous Wraparound
--------------------

Goal: make the tube wrap around the outside of the posts instead of going through the middle

Post One: (28.15, 41.86)
Post Two: (81.76, 164.67)

# Tube
# Note the overhang at the start
python generate_lissajous.py --lissajous SUM_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD -0.5 --lissN 2.5 --x_scale 55.416 --y_scale 110.832 --slope_angle 3.7 --start_t -0.036 --end_t 1.036 --kink_replace_circle "((0.375, 0.425),(0.575, 0.625))" --tube_radius 12.5 --tube_method oval --tube_start_angle "((0.02,-30),(0.08,0))" --tube_wall_height 6 --overlaps "((0.09,0.6),(0.4,0.91))" --overlap_separation 24

# Stabilizer at the overlap
# Plan: put at same spot as the tube, cut away everything that isn't the supporting piece
# from the first level to the second
# Can use a hole (the next piece) to make sure the support doesn't come through the bottom
python generate_lissajous.py --lissajous SUM_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD -0.5 --lissN 2.5 --x_scale 55.416 --y_scale 110.832 --slope_angle 3.7 --start_t -0.036 --end_t 1.036 --kink_replace_circle "((0.375, 0.425),(0.575, 0.625))" --tube_radius 12.5 --tube_method oval --tube_wall_height 14 --overlaps "((0.09,0.6),(0.4,0.91))" --overlap_separation 24

# Hole for the posts
python generate_lissajous.py --lissajous SUM_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD -0.5 --lissN 2.5 --x_scale 55.416 --y_scale 110.832 --slope_angle 3.7 --start_t -0.036 --end_t 1.036 --kink_replace_circle "((0.375, 0.425),(0.575, 0.625))" --tube_radius 10.5 --wall_thickness 11 --tube_start_angle 0  --tube_end_angle 360 --overlaps "((0.09,0.6),(0.4,0.91))" --overlap_separation 24 

Lissajous Twist Tie
-------------------

maybe a Lissajous product of harmonics like 9.5.8 but with n=7.  poles at the two corners, two paths, and the paths cross in the middle
  a=2, b=0, c=1, d=0.5, n=7

# piece with wiggles
# endpoints 234.1 apart, height 51   (x 205.0155, y 113.0107, z 51)
# end rotation is 2
# although 1 degree works better for the ramp
python generate_lissajous.py --lissajous PRODUCT_HARMONICS --lissA 2 --lissB 0.0 --lissC 1 --lissD 0.5 --lissN 7 --x_scale 94.9873 --y_scale 85.93 --slope_angle 7.10198 --start_t -0.12 --end_t 0.12 --extra_t 0.01 --kink_replace_circle "((-0.088,-0.07),(0.07,0.088))" --tube_start_angle "((-0.055,0),(-0.035,-60),(-0.018,-60),(-0.005,-75),(0.005,-75),(0.018,-60))" --tube_end_angle "((-0.018,240),(-0.005,255),(0.005,255),(0.018,240),(0.035,240),(0.055,180))"

# hole
python generate_lissajous.py --lissajous PRODUCT_HARMONICS --lissA 2 --lissB 0.0 --lissC 1 --lissD 0.5 --lissN 7 --x_scale 94.9873 --y_scale 85.93 --slope_angle 7.10198 --start_t -0.12 --end_t 0.12 --extra_t 0.01 --kink_replace_circle "((-0.088,-0.07),(0.07,0.088))" --tube_start_angle 0  --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11

# piece that looks like a sine
# end rotation is 164
# looks more like 165 when reaching the post

python generate_lissajous.py --lissajous PRODUCT_HARMONICS --lissA 2 --lissB 0.0 --lissC 1 --lissD 0.5 --lissN 7 --x_scale 113.2899 --y_scale 91.8058 --slope_angle 5.50394 --start_t 0.16 --end_t 0.34 --tube_end_angle "((0.241,240),(0.250,255),(0.259,240),(0.268,240),(0.283,180))" --tube_start_angle "((0.217,0),(0.232,-60),(0.241,-60),(0.250,-75),(0.259,-60))" --num_time_steps 360

# hole
python generate_lissajous.py --lissajous PRODUCT_HARMONICS --lissA 2 --lissB 0.0 --lissC 1 --lissD 0.5 --lissN 7 --x_scale 113.2899 --y_scale 91.8058 --slope_angle 5.50394 --start_t 0.16 --end_t 0.34 --tube_start_angle 0 --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11

Center of piece: 
  sine component is: 229.05 x 204.09
  wiggle component:  229.99 x 115.75    -> 113.01 long in its construction
  center: 115, 102.05

  sine component: 0.48,     0
  wiggle:            0, 45.55

Lissajous Butterfly
-------------------

Compound harmonic as per 9.5.12 on p140
a/c = 2/1, b = 0, d = 0, n = 1

rotation at top: 28.1

# travel path
python generate_lissajous.py  --lissajous COMPOUND_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD 0.0 --lissN 1.0 --x_scale 85 --y_scale 105 --slope_angle 4  --y_regularization 0.4 --regularization 0.2 --regularization_radius 0.2 --start_t 0 --end_t 1.0 --overlaps "((0.01,0.24),(0.26, 0.49),(0.51,0.74),(0.76, 0.99))" --overlap_separation 24 --num_time_steps 500 --tube_start_angle "((0.49,0),(0.53,-60))" --tube_end_angle "((0.47,240),(0.51,180))"

# tunnel walls for the central post
# this goes 2.1 higher than the travel path
python generate_lissajous.py  --lissajous COMPOUND_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD 0.0 --lissN 1.0 --x_scale 85 --y_scale 105 --slope_angle 4  --y_regularization 0.4 --regularization 0.2 --regularization_radius 0.2 --start_t 0.04 --end_t 0.96 --overlaps "((0.01,0.24),(0.26, 0.49),(0.51,0.74),(0.76, 0.99))" --overlap_separation 24 --num_time_steps 500 --tube_start_angle 0 --tube_end_angle 360

# holes to go through the central post
python generate_lissajous.py  --lissajous COMPOUND_HARMONICS --lissA 2 --lissB 0 --lissC 1 --lissD 0.0 --lissN 1.0 --x_scale 85 --y_scale 105 --slope_angle 4  --y_regularization 0.4 --regularization 0.2 --regularization_radius 0.2 --start_t 0 --end_t 1.0 --overlaps "((0.01,0.24),(0.26, 0.49),(0.51,0.74),(0.76, 0.99))" --overlap_separation 24 --num_time_steps 500 --tube_start_angle 0 --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11

TODO: Overlapping Lissajous Butterfly
-------------------------------------
sin(2t), sin(t) * sin(4t)
figure it out

Lissajous Splitter
------------------

This represents one branch of a splitter.  What you can do is line up
the wall and the hole, then copy it and mirror it so that the ends
align.  The three end points will be 134mm apart each.

python generate_lissajous.py  --lissajous COMPOUND_HARMONICS --lissA 2 --lissB 0.25 --lissC 1 --lissD 0.0 --lissN 1.0 --x_scale 85.8538 --y_scale 71.8232 --slope_angle 9 --extra_start_t 0.04 --start_t 0.25 --end_t .5625 --tube_end_angle "((.245,180),(.305,240))" --tube_start_angle "((.24,-60),(.32,-30))"

python generate_lissajous.py  --lissajous COMPOUND_HARMONICS --lissA 2 --lissB 0.25 --lissC 1 --lissD 0.0 --lissN 1.0 --x_scale 85.8538 --y_scale 71.8232 --slope_angle 9 --extra_start_t 0.04 --start_t 0.25 --end_t .5625 --tube_radius 10.6 --wall_thickness 11 --tube_end_angle 360


TODO: really crazy compound something
-------------------------------------
\left(\sin(8\pi t),\sin(2\pi\sin(2\pi t))\left(1+0\sin\left(4\pi t\right)\right)\right)
"""

class Lissajous(Enum):
    BASIC = 1
    SUM_HARMONICS = 2
    PRODUCT_HARMONICS = 3
    COMPOUND_HARMONICS = 4

def build_base_x_t(args):
    def x_t(t):
        x = math.sin((args.lissA / args.lissC) * 2 * math.pi * t + args.lissB * math.pi)
        return x

    return x_t

def build_base_y_t(args):
    if args.lissajous is Lissajous.BASIC:
        def y_t(t):
            y = math.sin(2 * math.pi * t)
            return y
    elif args.lissajous is Lissajous.SUM_HARMONICS:
        def y_t(t):
            y = 0.5 * (math.sin(2 * math.pi * t) + math.sin(args.lissN * 2 * math.pi * t + args.lissD * math.pi))
            return y
    elif args.lissajous is Lissajous.PRODUCT_HARMONICS:
        def y_t(t):
            y = math.sin(2 * math.pi * t) * math.sin(args.lissN * 2 * math.pi * t + args.lissD * math.pi)
            return y
    elif args.lissajous is Lissajous.COMPOUND_HARMONICS:
        def y_t(t):
            y = math.sin(args.lissN * math.pi * math.sin(2 * math.pi * t) + args.lissD * math.pi)
            return y
    else:
        raise ValueError("Unknown lissajous type %s" % args.lissajous.name)

    return y_t

def build_time_t(args):
    return extend_function.build_time_t(args.start_t, args.end_t, args.num_time_steps, args)

def build_x_y_t(args):
    time_t = build_time_t(args)
    base_x_t = build_base_x_t(args)
    x_t = extend_function.extend_f_t(time_t, base_x_t,
                                     args.start_t, args.end_t,
                                     extension_args=args)

    time_t = build_time_t(args)
    base_y_t = build_base_y_t(args)
    y_t = extend_function.extend_f_t(time_t, base_y_t,
                                     args.start_t, args.end_t,
                                     extension_args=args)

    reg_x_t = regularization.radial_reg_x_t(x_t, y_t, args)
    x_scale = args.x_scale
    def scale_x_t(t):
        return reg_x_t(t) * x_scale
    
    reg_y_t = regularization.radial_reg_y_t(x_t, y_t, args)
    y_scale = args.y_scale
    def scale_y_t(t):
        return reg_y_t(t) * y_scale
    
    return scale_x_t, scale_y_t
    
def describe_curve(args):
    if args.lissajous is Lissajous.BASIC:
        print("Building basic lissajous curve")
    elif args.lissajous is Lissajous.SUM_HARMONICS:
        print("Building a sum of harmonics lissajous curve")
    elif args.lissajous is Lissajous.PRODUCT_HARMONICS:
        print("Building a product of harmonics lissajous curve")
    elif args.lissajous is Lissajous.COMPOUND_HARMONICS:
        print("Building a compound harmonic lissajous curve")
    else:
        raise ValueError("Unknown lissajous type %s" % args.lissajous.name)

    print("  x(t) = sin((%d / %d) 2 pi t + %.4f pi)" % (args.lissA, args.lissC, args.lissB))

    if args.lissajous is Lissajous.BASIC:
        print("  y(t) = sin(2 pi t)")
    elif args.lissajous is Lissajous.SUM_HARMONICS:
        print("  y(t) = 0.5 * (sin(2 pi t) + sin(%.4f * pi * t + %.4f * pi))" % (2 * args.lissN, args.lissD))
    elif args.lissajous is Lissajous.PRODUCT_HARMONICS:
        print("  y(t) = sin(2 pi t) sin(%.4f pi t + %.4f * pi)" % (2 * args.lissN, args.lissD))
    elif args.lissajous is Lissajous.COMPOUND_HARMONICS:
        print("  y(t) = sin(%.4f pi sin(2 pi t) + %.4f * pi)" % (args.lissN, args.lissD))
    else:
        raise ValueError("Unknown lissajous type %s" % args.lissajous.name)


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a lissajous curve or its relatives')

    marble_path.add_tube_arguments(parser, default_slope_angle=10.0, default_output_name='lissajous.stl')
    slope_function.add_overlap_args(parser)
    combine_functions.add_kink_circle_args(parser)
    extend_function.add_extend_args(parser)
    regularization.add_regularization_args(parser)

    parser.add_argument('--lissA', default=5, type=int,
                        help='value A in the lissajous formula')
    parser.add_argument('--lissB', default=0, type=float,
                        help='value B in the lissajous formula')
    parser.add_argument('--lissC', default=3, type=int,
                        help='value C in the lissajous formula')
    parser.add_argument('--lissD', default=0, type=float,
                        help='value D in the y(t) expression if an alternate formulation is used')
    parser.add_argument('--lissN', default=0, type=float,
                        help='value N in the y(t) expression if an alternate formulation is used')

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

    parser.add_argument('--lissajous', default=Lissajous.BASIC, type=lambda x: Lissajous[x.upper()],
                        help='What formula to use.  Options are ' + " ".join(i.name for i in Lissajous))

    # TODO: refactor the regularization argument?

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

