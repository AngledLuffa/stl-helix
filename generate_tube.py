import argparse
import math
import sys

import build_shape
import marble_path

def describe_curve(args):
    if args.rotation == 0:
        print("A basic tube of length {}".format(args.length))
    else:
        print("A basic tube of length {}, rotated {}".format(args.length, args.rotation))

def build_x_y_r_t(args):
    """
    Build x, y, r for a basic tube.
    A rotation of 0 is treated as going south to north along the y axis.
    Rotation is the number of degrees CCW.
    """
    rad = args.rotation * math.pi / 180
    x_r = -math.sin(rad)
    y_r = math.cos(rad)
    def x_t(time_step):
        return x_r * args.length * time_step / args.num_time_steps

    def y_t(time_step):
        return y_r * args.length * time_step / args.num_time_steps

    def r_t(time_step):
        return args.rotation

    return x_t, y_t, r_t

def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl tube.')

    marble_path.add_tube_arguments(parser,
                                   default_slope_angle=2.9,
                                   default_output_name='tube.stl')
    
    parser.add_argument('--length', default=50, type=float,
                        help='Length of the tube')
    parser.add_argument('--num_time_steps', default=100, type=int,
                        help='How refined to make the tube')
    parser.add_argument('--rotation', default=0, type=float,
                        help='Rotation on the tube, in degrees.  0 is going north')

    args = parser.parse_args(args=sys_args)
    return args

def main(sys_args=None):
    module = sys.modules[__name__]
    build_shape.main(module, sys_args)

if __name__ == '__main__':
    main()

