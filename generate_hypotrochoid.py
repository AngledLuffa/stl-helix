import argparse
import math

from enum import Enum

import build_shape
import combine_functions
import generate_helix
import marble_path
import slope_function

"""
Generates a hypotrochoid, a curve on a circle defined by 3 parameters.

x(t) = ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))
y(t) = ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))

to make a 3 lobed flower:
------------------------
this is the ramp
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 6  --tube_end_angle 240 --slope_angle 12

problem: the ramp has some obvious kinks in the corners
so we can add some regularization
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 240 --slope_angle 12 --regularization 0.07

complete circle tube.  chop everything except the middle.  this produces the tunnels through the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 360 --slope_angle 12 --regularization 0.07

make this a hole, use it for the negative space in the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 360 --slope_angle 12 --regularization 0.07  --tube_radius 10.5 --wall_thickness 11


angle is, not surprisingly, about 60 on the upper connection



Inside out flower, two leaves:
-----------------------------

Tube
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  0 --tube_method ELLIPSE --tube_start_angle -60 --overlaps "(7.0686, 11.7810)" --overlap_separation 25

Put this at 0, 0, 18
Angle is 56

Tunnels
If you put the tunnel from start_t 0 end_t 18.8496 you get top & bottom tunnels you don't want.
Start from start_t=2, piece is 77.17 tall.  
Go from start_t=2 end_t 16, piece is 72.41 tall.
Difference: 4.76
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  6 --end_t 12 --tube_method ELLIPSE --tube_end_angle 360 --overlaps "(7.0686, 11.7810)" --overlap_separation 25

Put this 0, 0, 22.76

Holes
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  0 --tube_method ELLIPSE --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11  --overlaps "(7.0686, 11.7810)" --overlap_separation 25

ramp out: 12 tilt, 63 rotate

Four lobed outside flower
-----

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 6 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --regularization 0.05 --overlap_separation 23 --overlaps "((0.9117, 2.2299),(2.4825, 3.8007),(4.0533, 5.3715),(5.6241, 6.9423))" --zero_circle --start_t 0.8854 --end_t 6.9886

put this at 0,0,18
post goes at 81.15,81.15,0
rotate post 55 degrees

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 6 --slope_angle 3 --tube_method ELLIPSE --tube_radius 10.5 --wall_thickness 11 --closest_approach 26 --regularization 0.05 --overlap_separation 23 --overlaps "((0.9117, 2.2299),(2.4825, 3.8007),(4.0533, 5.3715),(5.6241, 6.9423))" --zero_circle --start_t 0.8854 --end_t 6.9886 --tube_start_angle 0 --tube_end_angle 360

Three leaf inside out flower
----------------------------
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method ELLIPSE --tube_start_angle -60 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26

0, 0, 17.04

tunnels through the pole:
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  1.5 --end_t 30 --tube_method ELLIPSE --tube_start_angle -180 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26
then remove everything outside the pole

0, 0, 19.13

holes for the crossings, the on ramp, and the off ramp:
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method ELLIPSE --tube_start_angle -180 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26 --tube_radius 10.5 --wall_thickness 11

2, 2, 19.04

rotation on the out post: roughly 62 degrees

TODO: Five Pointed Star
-----------------

python generate_hypotrochoid.py --hypoA 5 --hypoB 3 --hypoC 7 --tube_method deep_oval --tube_wall_height 6 --slope_angle 5 --start_t 1.885 --closest_approach 26



5 lobed flower:
--------------
this is a solid tube for the links
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --regularization 0.01

slight regularization is needed to fit in a Dremel 3d40
height is 136.51
put it at x=0,y=0,z=15
the hole in the middle will make it perfect for connecting to the
  previous piece at 150mm up and the next piece at 18mm

cut off the bottom of the tube
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --end_t 6.2 --regularization 0.01
new height: 123.34
so make z=15+136.51-123.34=28.17
z=28.17

cut off the top of the tube as well
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 1.2 --end_t 6.2 --regularization 0.01

connector tube will go at x=51.89,y=58.30

actual ramp:
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 240 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --regularization 0.01
this goes at 0,0,15

hole that goes down the middle:
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283  --regularization 0.01  --tube_radius 10.5 --wall_thickness 11
this goes at 2,2,17

rotation on post: 36 degrees


TODO:  Epitrochoid
------------------

python generate_hypotrochoid.py --hypoA 15 --hypoB 3 --hypoC 9 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 3 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID

python generate_hypotrochoid.py --hypoA 21 --hypoB 6 --hypoC 15 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID

"""

class Trochoid(Enum):
    HYPOTROCHOID = 1
    EPITROCHOID = 2

def build_time_t(args):
    """
    Return a function which converts discrete times 0..args.num_time_steps to the range
    args.start_t..args_end_t
    """
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps
    return time_t

def build_reg_f_t(args):
    """
    Using the given args, builds a pair of functions for x & y

    x, y will take time steps and convert them to the correct span before calculating.

    The functions apply regularization to the x & y values.

    Not scaled yet, though.  This is refactored so that the method
    which calculates the scaling can do so
    """
    time_t = build_time_t(args)

    A = args.hypoA
    B = args.hypoB
    C = args.hypoC

    if args.trochoid == Trochoid.HYPOTROCHOID:
        def x_t(time_step):
            t = time_t(time_step)
            return ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))

        def y_t(time_step):
            t = time_t(time_step)
            return ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))
    elif args.trochoid == Trochoid.EPITROCHOID:
        def x_t(time_step):
            t = time_t(time_step)
            return ((A + B) * math.cos(t) - C * math.cos((A + B) * t / B))

        def y_t(time_step):
            t = time_t(time_step)
            return ((A + B) * math.sin(t) - C * math.sin((A + B) * t / B))
    else:
        raise ValueError("Unhandled trochoid type: " + args.trochoid)

    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < 1:
            length = 0
        else:
            length = length - 1
        reg = 1 / (args.regularization * length + 1)
        return y * reg

    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < 1:
            length = 0
        else:
            length = length - 1
        reg = 1 / (args.regularization * length + 1)
        return x * reg
    
    return reg_x_t, reg_y_t

def build_f_t(args):
    reg_x_t, reg_y_t = build_reg_f_t(args)
    
    def scale_x_t(time_step):
        return reg_x_t(time_step) * args.x_scale
    
    def scale_y_t(time_step):
        return reg_y_t(time_step) * args.y_scale

    return scale_x_t, scale_y_t


def describe_curve(args):
    A = args.hypoA
    B = args.hypoB
    C = args.hypoC

    if args.trochoid == Trochoid.HYPOTROCHOID:
        print("Generating Hypotrochoid: x(t) = %d cos(t) + %.4f cos((%d / %d) t)" % (A - B, C, A-B, B))
        print("                         y(t) = %d sin(t) - %.4f sin((%d / %d) t)" % (A - B, C, A-B, B))
    elif args.trochoid == Trochoid.EPITROCHOID:
        print("Generating Epitrochoid: x(t) = %d cos(t) - %.4f cos((%d / %d) t)" % (A + B, C, A+B, B))
        print("                        y(t) = %d sin(t) - %.4f sin((%d / %d) t)" % (A + B, C, A+B, B))
    else:
        raise ValueError("Unhandled trochoid type: " + args.trochoid)

def generate_hypotrochoid(args):
    describe_curve(args)
    x_t, y_t = build_f_t(args)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=build_time_t(args),
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=None)

    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    num_time_steps = args.num_time_steps

    if args.zero_circle:
        updated_functions = combine_functions.add_both_zero_circles(args=args,
                                                                    num_time_steps=num_time_steps,
                                                                    x_t=x_t,
                                                                    y_t=y_t,
                                                                    slope_angle_t=slope_angle_t,
                                                                    r_t=r_t)
        num_time_steps, x_t, y_t, slope_angle_t, r_t = updated_functions

    z_t = marble_path.arclength_height_function(x_t, y_t, num_time_steps,
                                                slope_angle_t=slope_angle_t)

    build_shape.print_stats(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t, num_time_steps=num_time_steps)

    print("Z goes from %.4f to %.4f" % (z_t(0), z_t(num_time_steps)))
    
    # can calculate dx & dy like this
    # but when adding regularization, that becomes hideous
    #t = time_t(time_step)
    #dx = -(A - B) * math.sin(t) - C * ((A - B) / B) * math.sin((A - B) * t / B)
    #dx = dx * args.x_scale
    #dy =  (A - B) * math.cos(t) - C * ((A - B) / B) * math.cos((A - B) * t / B)
    #dy = dy * args.y_scale

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle


def tune_closest_approach(args):
    """
    Calculate the closest approach to the center, then return a scale
    appropriate for making the marble path get exactly that close
    """
    reg_x, reg_y = build_reg_f_t(args)

    d_t = lambda t: (reg_x(t) ** 2 + reg_y(t) ** 2) ** 0.5

    ds = [d_t(t) for t in range(0, args.num_time_steps+1)]
    closest_approach = min(ds)
    closest_step = ds.index(closest_approach)
    print("Closest approach occurs at %d: %f away" % (closest_step, ds[closest_step]))
    if closest_approach <= 0.1:
        raise ValueError("The curve is going through (or very close to) the center, making it impossible to auto-scale")

    scale = args.closest_approach / closest_approach
    print("Calculated scale: %f" % scale)
    
    #for i, d in enumerate(ds):
    #    print(i, d)
    
    return scale
    
def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl zigzag.')

    marble_path.add_tube_arguments(parser, default_slope_angle=12.0, default_output_name='hypo.stl')
    slope_function.add_overlap_args(parser)
    combine_functions.add_zero_circle_args(parser)

    parser.add_argument('--hypoA', default=9, type=int,
                        help='value A in the hypo formula')
    parser.add_argument('--hypoB', default=3, type=int,
                        help='value B in the hypo formula')
    parser.add_argument('--hypoC', default=6, type=float,
                        help='value C in the hypo formula')

    parser.add_argument('--x_scale', default=6, type=float,
                        help='Scale the shape by this much in the x direction')
    parser.add_argument('--y_scale', default=6, type=float,
                        help='Scale the shape by this much in the y direction')
    parser.add_argument('--scale', default=None, type=float,
                        help='Scale both directions by this much')

    parser.add_argument('--start_t', default=math.pi / 3, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=None, type=float,
                        help='Time to end the equation.  If None, will be 2pi * b / gcd(a, b)')
    parser.add_argument('--num_time_steps', default=250, type=int,
                        help='Number of time steps in the whole curve')

    parser.add_argument('--regularization', default=0.0, type=float,
                        help='Hypotrochoids often get long lobes.  This can help smooth them out')

    parser.add_argument('--closest_approach', default=None, type=float,
                        help='Measurement from 0,0 to the closest point of the tube center.  Will override scale.  26 for a 31mm connector connecting exactly to the tube')

    parser.add_argument('--trochoid', default=Trochoid.HYPOTROCHOID, type=lambda x: Trochoid[x.upper()],
                        help='What formula to use.  Options are hypotrochoid and epitrochoid.')
    # TODO: add a macro argument for a flower, an N pointed star, etc

    args = parser.parse_args(args=sys_args)

    if args.end_t is None:
        N = args.hypoB / math.gcd(args.hypoA, args.hypoB)
        print("Evaluation time: {}2pi".format("%d * " % N if N != 1 else ""))
        args.end_t = args.start_t + 2 * math.pi * N

    if args.closest_approach is not None:
        args.scale = tune_closest_approach(args)

    if args.scale is not None:
        args.x_scale = args.scale
        args.y_scale = args.scale

    return args

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)    

    marble_path.write_stl(generate_hypotrochoid(args), args.output_name)

if __name__ == '__main__':
    main()

