import argparse
import math

import marble_path

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

TODO:
-----
to make a 4 lobed flower:

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 6 --slope_angle 8 --scale 6 --start_t 0.7854 --tube_method OVAL --tube_wall_height 6

needs overlaps, like in the cycloid
also needs some sort of bend into the middle
lobes will need regularization
and ideally we can make it exactly touch the outside of the post

TODO:
-----
inside out flower

three leaves:
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 7 --scale 14 --start_t  0 --tube_method OVAL --tube_wall_height 6

two leaves:
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 7 --scale 14 --start_t  0 --tube_method OVAL --tube_wall_height 6

maybe should have a round path so that the transition to the pole is smooth

Five Pointed Star
-----------------
python generate_hypotrochoid.py --hypoA 5 --hypoB 3 --hypoC 7 --tube_method deep_oval --tube_wall_height 6 --slope_angle 5 --scale 7 --start_t 1.885


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
"""

def build_reg_f_t(args, time_t):
    A = args.hypoA
    B = args.hypoB
    C = args.hypoC
    
    def x_t(time_step):
        t = time_t(time_step)
        return ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))

    def y_t(time_step):
        t = time_t(time_step)
        return ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))

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

def generate_hypotrochoid(args):
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps

    A = args.hypoA
    B = args.hypoB
    C = args.hypoC
    
    print("Generating x(t) = %d cos(t) + %.4f cos((%d / %d) t)" % (A - B, C, A-B, B))
    print("           y(t) = %d sin(t) - %.4f sin((%d / %d) t)" % (A - B, C, A-B, B))
    
    reg_x_t, reg_y_t = build_reg_f_t(args, time_t)
    
    def scale_x_t(time_step):
        return reg_x_t(time_step) * args.x_scale
    
    def scale_y_t(time_step):
        return reg_y_t(time_step) * args.y_scale
    
    z_t = marble_path.arclength_slope_function(scale_x_t, scale_y_t, args.num_time_steps, args.slope_angle)
    r_t = marble_path.numerical_rotation_function(scale_x_t, scale_y_t)

    min_x = min(scale_x_t(i) for i in range(args.num_time_steps + 1))
    min_y = min(scale_y_t(i) for i in range(args.num_time_steps + 1))
    print("Minimum x, y: %f %f" % (min_x, min_y))
    max_x = max(scale_x_t(i) for i in range(args.num_time_steps + 1))
    max_y = max(scale_y_t(i) for i in range(args.num_time_steps + 1))
    print("Maximum x, y: %f %f" % (max_x, max_y))
    print("Z goes from %.4f to %.4f" % (z_t(0), z_t(args.num_time_steps)))
    
    # can calculate dx & dy like this
    # but when adding regularization, that becomes hideous
    #t = time_t(time_step)
    #dx = -(A - B) * math.sin(t) - C * ((A - B) / B) * math.sin((A - B) * t / B)
    #dx = dx * args.x_scale
    #dy =  (A - B) * math.cos(t) - C * ((A - B) / B) * math.cos((A - B) * t / B)
    #dy = dy * args.y_scale
    
    for triangle in marble_path.generate_path(x_t=scale_x_t, y_t=scale_y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps):
        yield triangle    
    


def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl zigzag.')

    marble_path.add_tube_arguments(parser, default_slope_angle=12.0, default_output_name='hypo.stl')

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


    # TODO: add a macro argument for a flower, an N pointed star, etc
    # TODO: add a argument for making the closest approach of an hypotrochoid with a-b!=c exactly tangent

    args = parser.parse_args()

    if args.end_t is None:
        N = args.hypoB / math.gcd(args.hypoA, args.hypoB)
        print("Evaluation time: %d * 2pi" % N)
        args.end_t = args.start_t + 2 * math.pi * N
    
    if args.scale is not None:
        args.x_scale = args.scale
        args.y_scale = args.scale

    return args

def main():
    args = parse_args()
    marble_path.print_args(args)    

    marble_path.write_stl(generate_hypotrochoid(args), args.output_name)

if __name__ == '__main__':
    main()

