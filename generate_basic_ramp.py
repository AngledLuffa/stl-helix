import argparse
import math
import sys

import build_shape
import combine_functions
import generate_helix
import generate_tube
import marble_path

"""
Produces the ramp part of a basic ramp.

Round wall to stop narbles from flying off:
python generate_basic_ramp.py --num_time_steps 200 --tube_end_angle "((90,180),(110,240))"


python generate_basic_ramp.py --num_time_steps 200 --tube_method OVAL --tube_wall_height 4
python generate_basic_ramp.py --num_time_steps 200
python generate_basic_ramp.py --num_time_steps 200 --tube_radius 10.5 --wall_thickness 11 --post_effective_tube_radius 12.5 --post_effective_wall_thickness 2 --tube_start_angle 0 --tube_end_angle 360 --ramp_extension 0.0
"""

def describe_curve(args):
    print("Building a basic ramp")
    print("Posts are {} aparts and {} in radius".format(args.post_distance, args.post_radius))

def build_x_y_r_t(args):
    """
    The curve will consist of 3 pieces.  A tube, a helix going around
    the second post, and a helix going into the second post
    """
    # the effective radius & thickness are so that holes can be made
    # at the right size for the shell they are in the middle of
    tube_radius = args.post_effective_tube_radius
    wall_thickness = args.post_effective_wall_thickness

    # The y distance between the centers of the posts will be:
    #   radius of a post + radius of the tube - wall_thickness
    # the wall thickness is so that the tube is fused to the second post
    y_dist = args.post_radius + tube_radius - wall_thickness
    x_dist = (args.post_distance ** 2 - y_dist ** 2) ** 0.5
    print("Post distance: {}".format(args.post_distance))
    print("x_dist: {} y_dist: {}".format(x_dist, y_dist))

    tube_args = argparse.Namespace(**vars(args))
    tube_args.rotation = 90
    # increase the length by post_radius so that the tube can be used
    # for the landing tube inside the first post
    tube_args.length = x_dist + args.ramp_extension
    tube_args.num_time_steps = args.num_time_steps // 2
    x_t, y_t, r_t = generate_tube.build_x_y_r_t(tube_args)

    updated_functions = combine_functions.add_post_exit(args,
                                                        clockwise=True,
                                                        num_time_steps=tube_args.num_time_steps,
                                                        post_time_steps=args.num_time_steps - tube_args.num_time_steps,
                                                        x_t=x_t,
                                                        y_t=y_t,
                                                        slope_angle_t=lambda t: args.slope_angle,
                                                        r_t=r_t)
    _, x_t, y_t, _, r_t = updated_functions
    return x_t, y_t, r_t


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a basic ramp')

    marble_path.add_tube_arguments(parser, default_slope_angle=2.9, default_output_name='ramp.stl')
    combine_functions.add_post_args(parser)

    parser.add_argument('--num_time_steps', default=200, type=int,
                        help='Number of time steps in the whole ramp')
    parser.add_argument('--ramp_extension', default=None, type=float,
                        help='How far to extend the ramp past the first post')

    args = parser.parse_args(args=sys_args)

    combine_functions.process_post_args(args)

    if args.ramp_extension is None:
        args.ramp_extension = args.post_radius

    return args

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

