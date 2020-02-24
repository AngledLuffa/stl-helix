import argparse
import math

import marble_path

"""

to make a 3 lobed flower:
this is the ramp
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --end_t 7.3303 --scale 6  --tube_end_angle 240 --slope_angle 12

complete circle tube.  chop everything except the middle.  this produces the tunnels through the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --end_t 7.3303 --scale 6  --tube_end_angle 360 --slope_angle 12

make this a hole, use it for the negative space in the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --end_t 7.3303 --scale 6  --tube_end_angle 360 --slope_angle 12 --tube_radius 10.5 --wall_thickness 11

angle is, not surprisingly, about 60 on the upper connection

to make a 4 lobed flower:
python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 9 --tube_end_angle 240 --slope_angle 8 --scale 4 --start_t 0.7854 --end_t 7.0686
"""

def get_normal_rotation(theta, x_scale, y_scale, a, b):
    # there is a discontinuity in the derivative at theta = 0.0
    # fortunately, we know it will be heading south at that point
    if theta == 0.0:
        return 180
    dx, dy = limacon_derivative(theta, x_scale, y_scale, a, b)
    rotation = math.asin(dx / (dx ** 2 + dy ** 2) ** 0.5)
    if dx > 0 and dy > 0:
        # this gives us a negative rotation, meaning to the right
        rotation = -rotation
    elif dx > 0 and dy < 0:
        rotation = rotation + math.pi
    elif dx < 0 and dy > 0:
        rotation = -rotation
    else: # dx < 0 and dy < 0
        rotation = rotation + math.pi

    return rotation * 180 / math.pi



def generate_hypotrochoid(args):
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps

    A = args.hypoA
    B = args.hypoB
    C = args.hypoC

    def x_t(time_step):
        t = time_t(time_step)
        return args.x_scale * ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))

    def y_t(time_step):
        t = time_t(time_step)
        return args.y_scale * ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))
    
    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps, args.slope_angle)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)
    
    # can calculate dx & dy like this
    # but when adding regularization, that becomes hideous
    #t = time_t(time_step)
    #dx = -(A - B) * math.sin(t) - C * ((A - B) / B) * math.sin((A - B) * t / B)
    #dx = dx * args.x_scale
    #dy =  (A - B) * math.cos(t) - C * ((A - B) / B) * math.cos((A - B) * t / B)
    #dy = dy * args.y_scale
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle=args.slope_angle):
        yield triangle    
    


def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl zigzag.')

    marble_path.add_tube_arguments(parser, default_slope_angle=12.0)

    parser.add_argument('--hypoA', default=9, type=float,
                        help='value A in the hypo formula')
    parser.add_argument('--hypoB', default=3, type=float,
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
    parser.add_argument('--end_t', default=math.pi * 7 / 3, type=float,
                        help='Time to start the equation')
    parser.add_argument('--num_time_steps', default=250, type=int,
                        help='Number of time steps in the whole curve')

    parser.add_argument('--output_name', default='hypo.stl',
                        help='Where to put the stl')


    # TODO: add a macro argument for a flower, an N pointed star, etc
    # TODO: for the flower, calculate N from the value of a/b: b /
    #       gcd(a, b).  use that for end_t.  calculate start_t
    # TODO: add a argument for making the closest approach of an hypotrochoid with a-b!=c exactly tangent

    args = parser.parse_args()

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

