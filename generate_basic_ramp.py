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
python generate_basic_ramp.py --num_time_steps 200 --tube_radius 10.5 --wall_thickness 11 --effective_tube_radius 12.5 --effective_wall_thickness 2 --tube_start_angle 0 --tube_end_angle 360 --ramp_extension 0.0
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
    tube_radius = args.effective_tube_radius
    wall_thickness = args.effective_wall_thickness

    # The y distance between the centers of the posts will be:
    #   radius of a post + radius of the tube - wall_thickness
    # the wall thickness is so that the tube is fused to the second post
    y_dist = args.post_radius + tube_radius - wall_thickness
    x_dist = (args.post_distance ** 2 - y_dist ** 2) ** 0.5
    print("Post distance: {}".format(args.post_distance))
    print("x_dist: {} y_dist: {}".format(x_dist, y_dist))

    time_divisions = [0, int(args.num_time_steps / 2),
                      int(args.num_time_steps * 3 / 4), args.num_time_steps]

    tube_args = argparse.Namespace(**vars(args))
    tube_args.rotation = 90
    # increase the length by post_radius so that the tube can be used
    # for the landing tube inside the first post
    tube_args.length = x_dist + args.ramp_extension
    tube_args.num_time_steps = time_divisions[1]
    x_t, y_t, r_t = generate_tube.build_x_y_r_t(tube_args)

    if args.post_radius - wall_thickness < tube_radius:
        raise ValueError("Post is too narrow for the final helix piece to adequately fit")

    # We want to wrap around the post at least 1/2 of the way, but less than 3/4 of the way
    # The way we do this is to figure out what angle the turn finishes at
    final_rotation = math.asin(tube_radius / (args.post_radius - wall_thickness)) * 180 / math.pi
    inner_rotation = (90 + final_rotation) / 360
    outer_rotation = 1.0 - inner_rotation
    
    outer_time_steps = time_divisions[2] - time_divisions[1]
    helix_args = argparse.Namespace(**vars(args))
    helix_args.rotations = outer_rotation
    helix_args.initial_rotation = 90
    helix_args.helix_radius = args.post_radius + tube_radius - wall_thickness
    helix_args.helix_sides = outer_time_steps / helix_args.rotations
    helix_args.clockwise = True

    x_t, y_t, _, r_t = combine_functions.append_functions(x1_t=x_t, y1_t=y_t, slope1_t=2.9, r1_t=r_t,
                                                          x2_t=generate_helix.helix_x_t(helix_args),
                                                          y2_t=generate_helix.helix_y_t(helix_args),
                                                          slope2_t=2.9,
                                                          r2_t=generate_helix.helix_r_t(helix_args),
                                                          inflection_t=time_divisions[1])

    inner_time_steps = time_divisions[3] - time_divisions[2]
    helix_args = argparse.Namespace(**vars(args))
    helix_args.rotations = inner_rotation
    helix_args.initial_rotation = 90 - 360.0 * outer_rotation
    helix_args.helix_radius = tube_radius
    helix_args.helix_sides = inner_time_steps / helix_args.rotations
    helix_args.clockwise = True

    x_t, y_t, _, r_t = combine_functions.append_functions(x1_t=x_t, y1_t=y_t, slope1_t=2.9, r1_t=r_t,
                                                          x2_t=generate_helix.helix_x_t(helix_args),
                                                          y2_t=generate_helix.helix_y_t(helix_args),
                                                          slope2_t=2.9,
                                                          r2_t=generate_helix.helix_r_t(helix_args),
                                                          inflection_t=time_divisions[2])

    return x_t, y_t, r_t


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a basic ramp')

    marble_path.add_tube_arguments(parser, default_slope_angle=2.9, default_output_name='ramp.stl')
    parser.add_argument('--post_distance', default=134, type=float,
                        help='Distance from one post to another')
    parser.add_argument('--post_radius', default=15.5, type=float,
                        help='Radius of a post')
    parser.add_argument('--num_time_steps', default=200, type=int,
                        help='Number of time steps in the whole ramp')

    parser.add_argument('--effective_tube_radius', default=None, type=float,
                        help='If set, do the calculations assuming this tube radius.  Useful for the hole of a ramp, for example')
    parser.add_argument('--effective_wall_thickness', default=None, type=float,
                        help='If set, do the calculations assuming this wall thickness.  Useful for the hole of a ramp, for example')
    parser.add_argument('--ramp_extension', default=None, type=float,
                        help='How far to extend the ramp past the post')

    args = parser.parse_args(args=sys_args)

    if args.effective_tube_radius is None:
        args.effective_tube_radius = args.tube_radius
    if args.effective_wall_thickness is None:
        args.effective_wall_thickness = args.wall_thickness
    if args.ramp_extension is None:
        args.ramp_extension = args.post_radius

    return args

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

