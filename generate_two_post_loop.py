import argparse
import math
import sys

import build_shape
import combine_functions
import marble_path

""" 
Builds a sequence of loops between two posts.

Three loops
-----------

The default arguments build three loops that fit exactly between posts
150 mm tall

  python generate_two_post_loop.py

Default shape is 154.59 wide.  154.59 / 2 = 77.29.  Assuming loop
length is 82, so the ellipse is 41 long, the post is 31 in diameter,
the tube radius is 12.5, and the wall thickness is 2, we get that this
should be positioned at:

  77.29 - 12.5 - 31 + 2 - 41

Loops go at (5.21, 0)
posts go at (0, 32) and (134, 32)

posts rotate by 138

To generate the holes in the post:

  python generate_two_post_loop.py --loop_length 82 --tube_radius 10.5 --wall_thickness 11 --tube_start_angle 0 --tube_end_angle 360

Similar math puts the holes at 5.21
"""


def describe_curve(args):
    print("Building loops between two posts")
    print("{} loop(s) between posts which are {} apart".format(args.num_loops, args.post_distance))
    print("Ellipses making up the loops are {} long and {} wide".format(args.loop_length, args.loop_width))

def build_x_y_r_t(args):
    # start and end segments are the curves into the post
    num_segments = 4 * args.num_loops + 2
    start_length = args.num_time_steps // num_segments
    end_length = args.num_time_steps // num_segments
    num_loop_steps = args.num_time_steps - start_length - end_length

    def time_t(time_step):
        return time_step * 2 * math.pi * args.num_loops / num_loop_steps - math.pi / 2
    
    def x_t(time_step):
        t = time_t(time_step)
        return math.cos(t) * args.loop_length / 2 + args.post_distance / 2

    def y_t(time_step):
        t = time_t(time_step)
        return math.sin(t) * args.loop_width / 2

    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    slope_angle_t = lambda x: args.slope_angle

    args.zero_circle_sides = start_length
    num_time_steps, x_t, y_t, _, r_t = combine_functions.add_zero_circle(args, True, num_loop_steps, x_t, y_t, slope_angle_t, r_t)

    args.zero_circle_sides = end_length
    num_time_steps, x_t, y_t, _, r_t = combine_functions.add_zero_circle(args, False, num_time_steps, x_t, y_t, slope_angle_t, r_t)
    
    return x_t, y_t, r_t


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a two post loop')

    marble_path.add_tube_arguments(parser, default_slope_angle=7, default_output_name='loops.stl')

    parser.add_argument('--num_time_steps', default=280, type=int,
                        help='Number of time steps in the whole ramp')
    parser.add_argument('--num_loops', default=3, type=int,
                        help='How many times to loop')

    parser.add_argument('--post_distance', default=134, type=float,
                        help='Distance from one post to another')
    parser.add_argument('--post_radius', default=15.5, type=float,
                        help='Radius of a post')
    parser.add_argument('--loop_length', default=None, type=float,
                        help='The ellipse axis between the posts')
    parser.add_argument('--loop_width', default=70, type=float,
                        help='The ellipse axis perpendicular to the posts')

    parser.set_defaults(tube_start_angle=-45)
    args = parser.parse_args(args=sys_args)

    # To get the loops to just contact the wall of the tube, we calculate:
    #   the center will be at 67
    #   the tube radius is 12.5
    #   the post radius is 15.5
    #   wall thickness is 2
    #   67 - 12.5 - 15.5 + 2 = 41
    # so we want the loops to be 82 long
    if args.loop_length is None:
        args.loop_length = (args.post_distance / 2 - args.tube_radius - args.post_radius + args.wall_thickness) * 2
        print("Using a loop length of {}".format(args.loop_length))

    return args

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

