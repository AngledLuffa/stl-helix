import argparse
import math

import marble_path
import slope_function


def generate_lissajous(args):
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps

    def x_t(time_step):
        t = time_t(time_step)
        x = math.sin((args.lissA / args.lissC) * 2 * math.pi * t + args.lissB * math.pi)
        return x * args.x_scale

    def y_t(time_step):
        t = time_t(time_step)
        y = math.sin(2 * math.pi * t)
        return y * args.y_scale

    #for i in range(0, args.num_time_steps+1):
    #    print(i, time_t(i), x_t(i), y_t(i))
    x0 = x_t(0)
    y0 = y_t(0)
    xn = x_t(args.num_time_steps)
    yn = y_t(args.num_time_steps)
    print("Start of the curve: (%.4f, %.4f)" % (x0, y0))
    print("End of the curve:   (%.4f, %.4f)" % (xn, yn))
    dist = ((xn - x0) ** 2 + (yn - y0) ** 2) ** 0.5
    print("Distance: %.4f" % dist)
    
    # TODO: utilize slope_function

    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps, args.slope_angle)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps):
        yield triangle




def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a lissajous curve or its relatives')

    marble_path.add_tube_arguments(parser, default_slope_angle=10.0, default_output_name='lissajous.stl')
    slope_function.add_overlap_args(parser)

    parser.add_argument('--lissA', default=3, type=float,
                        help='value A in the lissajous formula')
    parser.add_argument('--lissB', default=0, type=float,
                        help='value B in the lissajous formula')
    parser.add_argument('--lissC', default=2, type=float,
                        help='value C in the lissajous formula')

    parser.add_argument('--start_t', default=1.22, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=2.78, type=float,
                        help='Time to end the equation')
    parser.add_argument('--num_time_steps', default=250, type=int,
                        help='Number of time steps in the whole curve')

    # TODO: refactor the scale arguments?
    parser.add_argument('--x_scale', default=40, type=float,
                        help='Scale the shape by this much in the x direction')
    parser.add_argument('--y_scale', default=50, type=float,
                        help='Scale the shape by this much in the y direction')
    parser.add_argument('--scale', default=None, type=float,
                        help='Scale both directions by this much')

    args = parser.parse_args(args=sys_args)

    if args.scale is not None:
        args.x_scale = args.scale
        args.y_scale = args.scale

    return args
    

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_lissajous(args), args.output_name)

if __name__ == '__main__':
    main()

