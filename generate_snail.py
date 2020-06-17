import argparse
import math
import sys

import build_shape
import combine_functions
import generate_tube
import marble_path
import slope_function

"""
Generates some of the shapes from the 'spirals' section of Curve Design and Generation

Two branch spiral, opposite sides
---------------------------------

# Tube:
python generate_snail.py --slope_angle 3 --post_exit_counterclockwise --post_entrance_clockwise --tube_end_angle "((110,240),(170,180))" --tube_start_angle "((190,0),(250,-60))" --overlaps "((130, 230))" --overlap_separation 37

# Hole:
python generate_snail.py --slope_angle 3 --post_exit_counterclockwise --post_entrance_clockwise --overlaps "((130, 230))" --overlap_separation 37 --tube_end_angle 360 --wall_thickness 11 --tube_radius 10.5 --post_effective_tube_radius 12.5 --post_effective_wall_thickness 2

Two branch spiral, same sides
-----------------------------
Doing this on a single level requires a very shallow angle.

Problem with doing it on a steep angle over 2 levels is that the tube
wraps around the lower post at a higher than the top of the lower post

# Tube:
python generate_snail.py --slope_angle 1.7 --post_exit_clockwise --post_entrance_clockwise --tube_end_angle 240

# Hole:
python generate_snail.py --slope_angle 1.7 --post_exit_clockwise --post_entrance_clockwise --tube_end_angle 360 --wall_thickness 11 --tube_radius 10.5 --post_effective_tube_radius 12.5 --post_effective_wall_thickness 2


# This version builds the piece on two levels, using the overlap functionality to make the drop between the posts

# Tube:
python generate_snail.py --slope_angle 3 --post_exit_clockwise --post_entrance_clockwise --tube_end_angle 240 --overlaps "((130, 230))" --overlap_separation 37

# Hole:
python generate_snail.py --slope_angle 3 --post_exit_clockwise --post_entrance_clockwise --tube_end_angle 360 --overlaps "((130, 230))" --overlap_separation 37 --wall_thickness 11 --tube_radius 10.5 --post_effective_tube_radius 12.5 --post_effective_wall_thickness 2

"""

def describe_curve(args):
    print("Building a ramp with snails at both ends")
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

    # The y distance between the center of a post and the tube will be:
    #   radius of a post + radius of the tube - wall_thickness
    # the wall thickness is so that the tube is fused to the second post
    # there are two posts, and they can either be on the same side (0)
    #   or opposite sides (2x)
    if args.post_entrance_clockwise == args.post_exit_clockwise:
        y_dist = 0
    else:
        y_dist = 2 * (args.post_radius + tube_radius - wall_thickness)
    if y_dist > args.post_distance:
        raise ValueError("Post distance too close for this post size")
    x_dist = (args.post_distance ** 2 - y_dist ** 2) ** 0.5
    print("Post distance: {}".format(args.post_distance))
    print("x_dist: {} y_dist: {}".format(x_dist, y_dist))

    tube_args = argparse.Namespace(**vars(args))
    tube_args.rotation = 90
    # increase the length by post_radius so that the tube can be used
    # for the landing tube inside the first post
    tube_args.length = x_dist
    num_time_steps = args.num_time_steps // 3
    tube_args.num_time_steps = num_time_steps
    x_t, y_t, r_t = generate_tube.build_x_y_r_t(tube_args)

    updated_functions = combine_functions.add_post(args,
                                                   num_time_steps=num_time_steps,
                                                   post_time_steps=(args.num_time_steps - num_time_steps) // 2,
                                                   x_t=x_t,
                                                   y_t=y_t,
                                                   slope_angle_t=lambda t: args.slope_angle,
                                                   r_t=r_t,
                                                   is_entrance=True)
    num_time_steps, x_t, y_t, _, r_t = updated_functions

    updated_functions = combine_functions.add_post(args,
                                                   num_time_steps=num_time_steps,
                                                   post_time_steps=args.num_time_steps - num_time_steps,
                                                   x_t=x_t,
                                                   y_t=y_t,
                                                   slope_angle_t=lambda t: args.slope_angle,
                                                   r_t=r_t,
                                                   is_entrance=False)
    _, x_t, y_t, _, r_t = updated_functions
    return x_t, y_t, r_t


def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a spiral - chapter 7 of Curve Design')

    marble_path.add_tube_arguments(parser, default_slope_angle=2.5, default_output_name='snail.stl')
    combine_functions.add_post_args(parser)
    slope_function.add_overlap_args(parser)

    parser.add_argument('--num_time_steps', default=360, type=int,
                        help='Number of time steps in the whole ramp')
    parser.add_argument('--post_distance', default=134, type=float,
                        help='Distance from one post to another')

    args = parser.parse_args(args=sys_args)

    combine_functions.process_post_args(args)

    return args

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

