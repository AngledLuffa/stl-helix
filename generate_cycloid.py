import argparse
import math
import sys

import build_shape
import combine_functions
import extend_function
import marble_path
import slope_function

"""
Generates a cycloid of the form (t + sin(4t), 1 - cos(4t))
----------------------------------------------------------
There is a loop here from .16675 to 1.40405 which must go down >= 23mm
(Also the negative of that obviously needs to happen as well)

To get walls to hopefully stop the marble from jumping:
python generate_cycloid.py --extra_t 0.1 --slope_angle 3.0 --tube_method oval --tube_wall_height 6 --overlaps "((.16675,1.40405),(-.16675,-1.40405))" --overlap_separation 25 --scale 32.3547

Note that other arguments can make pretty interesting curves as well

p67 of Practical Handbook of Curve Design and Generation


a possibly interesting variant:
------------------------------
  t - sin 4t, cos 3t
from -5pi/4 to pi/4

Initial construction:

the regularization here is because otherwise the graph curves so much in the middle section that there is a kink
the phase change means it can go from -3pi/4 to 3pi/4
TODO: the description below produces one which is too shallow.  Need a different way of handling kinks

loops in this cycloid:
0.95215~0.95216   ..  2.18944~2.18945

python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 46.3392 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --reg_x 0.4 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.19 --overlap_separation 23 --tube_method oval --tube_wall_height 6 --wall_thickness 2.5 --kinks "(-0.3927, 0.3927)" --kink_width 0.15 --kink_slope 0.5


this will be good on & off holes
python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 46.3392 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --reg_x 0.4  --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.19 --overlap_separation 23 --tube_radius 10.5 --wall_thickness 11 --tube_start_angle 0 --tube_end_angle 360  --kinks "(-0.3927, 0.3927)" --kink_width 0.15  --kink_slope 0.5

this will clear up tiny notches

python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 46.3392 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --reg_x 0.4 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.19 --overlap_separation 23 --tube_method oval --tube_wall_height 6 --wall_thickness 5 --tube_radius 10.5 --tube_wall_height 10  --kinks "(-0.3927, 0.3927)" --kink_width 0.15 --kink_slope 0.5

put the first squiggle at
0, 0, 16.47
it is 231.68 x 136.21 x 78.90
posts at -8.85, 91.92, 50 and 209.53, 13.28, 0
tube is 18.5 high

squiggle for the holes:
229.40 x 132.21 x 81.40
tube is 22 high
so it goes at 1.99, 2, 18.47

Alternate formulation that stops it from ever going below 2.2 degrees slope:

python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 47.01455 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.2 --overlap_separation 23 --tube_method oval --tube_wall_height 6 --wall_thickness 2 --kink_replace_circle "((-0.55,-0.2),(0.2,0.55))"

Can make the bottoms of loops connect to the tops of loops as follows:

python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 47.01455 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.2 --overlap_separation 23 --tube_method oval --tube_wall_height 14 --wall_thickness 2 --kink_replace_circle "((-0.55,-0.2),(0.2,0.55))"

This removes the extra material that comes out through the bottom (the rest of the unwanted stuff can be removed with boxes)
python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 47.01455 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.2 --overlap_separation 23 --tube_method ellipse --tube_start_angle 0 --tube_end_angle 360 --tube_radius 11.5 --wall_thickness 12 --kink_replace_circle "((-0.55,-0.2),(0.2,0.55))"

This is the holes for the start & stop
python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --scale 47.01455 --no_use_sign --y_scale 1.2 --y_phase 1.5708 --overlaps "((0.95215,2.18945),(-0.95215,-2.18945))" --slope_angle 2.2 --overlap_separation 23 --tube_method ellipse --tube_start_angle 0 --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11 --kink_replace_circle "((-0.55,-0.2),(0.2,0.55))"

33 degree rotation on the top

another variant: two omega symbols
----------------------------------

python generate_cycloid.py --slope_angle 7.0 --tube_method ellipse --scale 46 --x_coeff -0.6 --x_t_coeff 4 --y0 0 --y_coeff 1.5 --y_t_coeff 2 --y_phase 1.5708 --min_domain -1.5708 --max_domain 1.5708 --no_use_sign --extra_t 0.094243 --tube_end_angle "((-0.2,240),(0.0,180))"  --tube_start_angle "((0.0,0),(0.2,-60))"

hole:
python generate_cycloid.py --slope_angle 7.0 --tube_method ellipse --scale 46 --x_coeff -0.6 --x_t_coeff 4 --y0 0 --y_coeff 1.5 --y_t_coeff 2 --y_phase 1.5708 --min_domain -1.5708 --max_domain 1.5708 --no_use_sign --extra_t 0.094243 --tube_end_angle 360   --tube_start_angle 0 --tube_radius 10.5 --wall_thickness 11
"""


def build_base_x_t(args):
    scale = args.scale

    def x_t(t):
        reg = (1.0 - args.reg_x) + args.reg_x * math.exp(args.reg_power * t ** 2) / (1.0 + math.exp(args.reg_power * t ** 2))
        return (t + reg * args.x_coeff * math.sin(args.x_t_coeff * t)) * scale

    return x_t

def build_base_y_t(args):
    scale = args.scale
    use_sign = args.use_sign

    def y_t(t):
        if t < 0 and use_sign:
            sign = -1
        else:
            sign = 1
        reg = (1.0 - args.reg_y) + args.reg_y * math.exp(args.reg_power * t ** 2) / (1.0 + math.exp(args.reg_power * t ** 2))
        return ((sign * (args.y0 + args.y_coeff * math.cos(args.y_t_coeff * t + args.y_phase))) *
                scale * args.y_scale * reg)

    return y_t
    

def build_time_t(args):
    return extend_function.build_time_t(args.min_domain, args.max_domain, args.num_time_steps, args)

def build_x_t(args):
    time_t = build_time_t(args)
    base_x_t = build_base_x_t(args)
    return extend_function.extend_f_t(time_t, base_x_t,
                                      args.min_domain, args.max_domain,
                                      args)

def build_y_t(args):
    time_t = build_time_t(args)
    base_y_t = build_base_y_t(args)
    return extend_function.extend_f_t(time_t, base_y_t,
                                      args.min_domain, args.max_domain,
                                      args)

def describe_curve(args):
    print("Building cycloid")
    print("  x(t) = t + %.4f sin(%.4f t)" % (args.x_coeff, args.x_t_coeff))
    print("  y(t) = %.4f + %.4f cos(%.4ft + %.4f)" % (args.y0, args.y_coeff, args.y_t_coeff, args.y_phase))

def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl cycloid.')

    marble_path.add_tube_arguments(parser, default_slope_angle=8.0, default_output_name='cycloid.stl')
    slope_function.add_kink_args(parser)
    slope_function.add_overlap_args(parser)
    combine_functions.add_kink_circle_args(parser)
    extend_function.add_extend_args(parser, default_extra_t=0.1)

    # Start & end times for the curve
    parser.add_argument('--domain', default=None, type=float,
                        help='If set, the domain will be -domain..domain')
    parser.add_argument('--min_domain', default=None, type=float,
                        help='t0 in the domain [t0, t1]')
    parser.add_argument('--max_domain', default=None, type=float,
                        help='t1 in the domain [t0, t1].  If left None, will be derived from the coefficients')

    # Parameters for the equation of this curve
    parser.add_argument('--x_coeff', default=1, type=float,
                      help='Coefficient A of x=t+A sin(Bt)')
    parser.add_argument('--x_t_coeff', default=4, type=int,
                      help='Coefficient B of x=t+A sin(Bt)')
    parser.add_argument('--y0', default=1, type=float,
                        help='Coefficient y0 of y(t) = y0 + C cos(Dt + phase)')
    parser.add_argument('--y_coeff', default=-1, type=float,
                        help='Coefficient C of y(t) = y0 + C cos(Dt + phase)')
    parser.add_argument('--y_t_coeff', default=4, type=int,
                      help='Coefficient D of y(t) = y0 + C cos(Dt + phase)')

    parser.add_argument('--use_sign', dest='use_sign',
                        default=True, action='store_true',
                        help='multiply y by sign(t)')
    parser.add_argument('--no_use_sign', dest='use_sign',
                        action='store_false',
                        help="Don't multiply y by sign(t)")
    
    
    parser.add_argument('--num_time_steps', default=400, type=int,
                      help='Number of time steps to model')

    parser.add_argument('--scale', default=None, type=float,
                        help='Scale by which to multiple f_t')

    # TODO: just make separate x_scale & y_scale arguments
    parser.add_argument('--y_scale', default=0.8, type=float,
                        help='Make the model a little squished or stretched vertically')
    parser.add_argument('--y_phase', default=0.0, type=float,
                        help='Adjust the phase of y(t) = y0 + C cos(Dt + phase)')

    parser.add_argument('--reg_x', default=0.0, type=float,
                        help='How much to use regularization on x around t=0.  Idea is to make squiggle with loops not have sharp corners')
    parser.add_argument('--reg_y', default=0.0, type=float,
                        help='How much to use regularization on y around t=0.  Idea is to make squiggle with loops not have sharp corners')
    parser.add_argument('--reg_power', default=4.0, type=float,
                        help='How tightly to apply the reg around t=0.  Higher t means less wide effect')

    args = parser.parse_args(args=sys_args)

    if args.domain is not None:
        args.min_domain = -args.domain
        args.max_domain = args.domain

    if args.min_domain is None or args.max_domain is None:
        width = math.pi * 4 / math.gcd(args.x_t_coeff, args.y_t_coeff)
        if args.min_domain is None and args.max_domain is None:
            args.min_domain = -width / 2
            args.max_domain =  width / 2
        elif args.min_domain is None:
            args.min_domain = args.max_domain - width
        else:
            args.max_domain = args.min_domain + width
            
    return args
    

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

