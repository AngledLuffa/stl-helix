import argparse
import math
import sys

import build_shape
import combine_functions
import marble_path
import marble_util

"""
Can produce graphs like this:

r = ((cos theta)^6 + (sin theta)^6) ^ 1/2
r = (cos^6 theta/3 + sin^6 theta/3) ^ 1/2

To make sure there is never a square root of a negative number, such
as if the A=6 is turned into a 5.5, we first square and then take the
A/2 power.  Consider this implied for the rest of the equations.

r = ((cos^2 theta)^3 + (sin^2 theta)^3) ^ 1/2

By default this makes 4 petals to the flower.  The polar equation
represents a parametric equation such as

x = (((cos theta)^6 + (sin theta)^6) ^ 1/2) cos theta
y = (((cos theta)^6 + (sin theta)^6) ^ 1/2) sin theta

The last term can be changed to make it rotate faster or slower,
changing the number of petals.  If we set this to R, so that we get

x = (((cos theta)^6 + (sin theta)^6) ^ 1/2) cos R theta
y = (((cos theta)^6 + (sin theta)^6) ^ 1/2) sin R theta

then there are 4/R petals per loop.  So, for example, R=8/7 makes
there be 7/2 petals per loop, and 2 loops makes for a very pleasing 7
petals overlapping twice.  R=12/7 is also worth investigating, as is
16/9 (set A=4.4, B=1.5 for 16/9)

The R coefficient could be substituted in the inner trig terms, such
as these equations.  This makes it possible to represent the entire
equation as a polar equation.  However, it is more convenient to put
the term in the outer cos/sin because of the problem we describe next.

x = (((cos theta / R)^6 + (sin theta)^6) ^ 1/2) cos theta
y = (((cos theta / R)^6 + (sin theta)^6) ^ 1/2) sin theta

r = (((cos theta / R)^6 + (sin theta)^6) ^ 1/2)

Basic problem: the 4 petal flower has a corner too tight at the
central pole.  However, we can wiggle the cos/sin R theta terms with
(sin 8t) to spread out the central pole and the endpoints.

x = (((cos theta)^6 + (sin theta)^6) ^ 1/2) cos R (theta + .3 sin 8 theta)
y = (((cos theta)^6 + (sin theta)^6) ^ 1/2) sin R (theta + .3 sin 8 theta)


Clover with really fat petals
-----------------------------

python generate_clover.py --slope_angle 5.6 --start_t 1.0472 --end_t 6.8068 --flower_power 4.4  --twist_numerator 3 --zero_circle  --pinch_power 1.3   --tube_method oval --tube_wall_height 6


150mm post goes 73.638, 73.647

hole:
python generate_clover.py --slope_angle 5.6 --start_t 1.0472 --end_t 6.8068 --flower_power 4.4  --twist_numerator 3 --zero_circle  --pinch_power 1.3   --tube_method oval --tube_wall_height 6 --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11


Clover with 7 petals in 3 loops
-------------------------------

python generate_clover.py --slope_angle 5.6 --start_t 1.1781 --end_t 11.3883 --flower_power 3.2 --zero_circle  --pinch_power 2.1 --twist_numerator 12 --twist_denominator 7   --tube_method oval --tube_wall_height 6 


hole: goes at 55.041, 58.158
python generate_clover.py --slope_angle 5.6 --start_t 1.1781 --end_t 11.3883 --flower_power 3.2 --zero_circle  --pinch_power 2.1 --twist_numerator 12 --twist_denominator 7   --tube_method oval --tube_wall_height 3  --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11


Clover with 4 petals, corners wiggled a little
----------------------------------------------

python generate_clover.py --slope_angle 7.3 --start_t 0.9425 --end_t 6.9115 --flower_power 3.2 --zero_circle  --pinch_power 3 --twist_wiggle 0.2   --tube_method oval --tube_wall_height 6

python generate_clover.py --slope_angle 7.3 --start_t 0.9425 --end_t 6.9115 --flower_power 3.2 --zero_circle  --pinch_power 3 --twist_wiggle 0.2   --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11



No idea what to call this function, since it's not in Curve Design... for now, calling it a clover
"""

def build_time_t(args):
    start_t = args.start_t
    end_t = args.end_t
    num_time_steps = args.num_time_steps

    def time_t(t):
        return start_t + (end_t - start_t) * t / num_time_steps

    return time_t

def build_x_t(args):
    flower_power = args.flower_power / 2
    pinch_power = args.pinch_power
    scale = args.scale

    time_t = build_time_t(args)
    twist = args.twist_numerator / args.twist_denominator

    def x_t(t):
        t = time_t(t)
        return scale * ((math.cos(t) ** 2) ** flower_power + (math.sin(t) ** 2) ** flower_power) ** pinch_power * math.cos(twist * (t + args.twist_wiggle * math.sin (8 * t)))
    return x_t

def build_y_t(args):
    flower_power = args.flower_power / 2
    pinch_power = args.pinch_power
    scale = args.scale

    time_t = build_time_t(args)
    twist = args.twist_numerator / args.twist_denominator
    
    def y_t(t):
        t = time_t(t)
        return scale * ((math.cos(t) ** 2) ** flower_power + (math.sin(t) ** 2) ** flower_power) ** pinch_power * math.sin(twist * (t + args.twist_wiggle * math.sin (8 * t)))
    return y_t

def describe_curve(args):
    print("Building flower")
    flower_power = marble_util.simplify_float_to_string(args.flower_power / 2)
    pinch_power = marble_util.simplify_float_to_string(args.pinch_power)
    twist = marble_util.simplify_integer_ratio(args.twist_numerator, args.twist_denominator)

    f_x = "((cos^2 (t))^{%s} + (sin^2 (t))^{%s}) ^ {%s} cos(%s t)" % (flower_power, flower_power, pinch_power, twist)
    f_y = "((cos^2 (t))^{%s} + (sin^2 (t))^{%s}) ^ {%s} sin(%s t)" % (flower_power, flower_power, pinch_power, twist)
    print("  x = %s" % f_x)
    print("  y = %s" % f_y)
    print("(%s, %s)" % (f_x, f_y))

def tune_closest_approach(args):
    # Closest approach will always be at multiples of pi/4
    # and of course cos pi/4 or sin pi/4 is sqrt(2)/2
    radius = 2.0 ** 0.5 / 2.0
    radius = (2.0 * radius ** args.flower_power) ** args.pinch_power
    scale = args.closest_approach / radius
    print("Calculated scale: %f" % scale)
    return scale


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl clover.')

    marble_path.add_tube_arguments(parser, default_slope_angle=6.0, default_output_name='clover.stl')
    combine_functions.add_zero_circle_args(parser)

    parser.add_argument('--flower_power', default=4, type=float,
                        help='Coefficient A of (cos^A theta + sin^A theta)^B')
    parser.add_argument('--pinch_power', default=1.5, type=float,
                        help='Coefficient B of (cos^A theta + sin^A theta)^B')
    parser.add_argument('--closest_approach', default=26.0, type=float,
                        help='Measurement from 0,0 to the closest point of the tube center.  26 for a 31mm connector connecting exactly to the tube')
    parser.add_argument('--twist_numerator', default=1, type=int,
                        help='Twist the flower - instead of cos(theta), use cos(m/n theta)')
    parser.add_argument('--twist_denominator', default=1, type=int,
                        help='Twist the flower - instead of cos(theta), use cos(m/n theta)')

    parser.add_argument('--twist_wiggle', default=0, type=float,
                        help='Wiggle the twist - instead of cos(m/n theta), use cos(m/n (theta + w sin (8 theta)))')
    parser.add_argument('--scale', default=None, type=float,
                        help='Amount to scale in the x/y directions.  Will override closest_approach if set.')
    
    parser.add_argument('--start_t', default=math.pi / 3, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=(2 + 1/6) * math.pi, type=float,
                        help='Time to end the equation.  If None, will be 2pi * b / gcd(a, b)')
    parser.add_argument('--num_time_steps', default=400, type=int,
                        help='Number of time steps in the whole curve')

    args = parser.parse_args(args=sys_args)

    if args.scale is None:
        args.scale = tune_closest_approach(args)

    return args


def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

    
if __name__ == '__main__':
    main()

    
