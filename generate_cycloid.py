import argparse
import math

import marble_path

"""
Generates a cycloid of the form (t + sin(4t), 1 - cos(4t))

Note that other arguments can make pretty interesting curves as well

p67 of Practical Handbook of Curve Dewsign and Generation
"""

def generate_cycloid(args):
    min_t = -args.domain - args.extra_t
    max_t = args.domain + args.extra_t
    def time_t(time_step):
        return min_t + (max_t - min_t) * time_step / args.num_time_steps

    scale = args.width / (max_t - min_t)

    def x_t(time_step):
        t = time_t(time_step)
        if t < -args.domain or t > args.domain:
            return t * scale
        return (t + args.x_coeff * math.sin(args.x_t_coeff * t)) * scale

    def y_t(time_step):
        t = time_t(time_step)
        if t < -args.domain or t > args.domain:
            return 0.0
        if t < 0:
            sign = -1
        else:
            sign = 1
        return (sign * (1 - math.cos(args.y_t_coeff * t))) * scale * args.y_scale

    #for i in range(args.num_time_steps + 1):
    #    print(i, time_t(i), x_t(i), y_t(i))

    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps, args.slope_angle)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle=-args.slope_angle):
        yield triangle    
    
def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl cycloid.')

    marble_path.add_tube_arguments(parser, default_slope_angle=8.0)

    parser.add_argument('--domain', default=None, type=float,
                      help='-domain..domain is where the graph occurs.  If left None, will be derived from the coefficients')

    parser.add_argument('--x_coeff', default=1, type=float,
                      help='Coefficient A of x=t+A sin(Bt)')
    parser.add_argument('--x_t_coeff', default=4, type=int,
                      help='Coefficient B of x=t+A sin(Bt)')
    parser.add_argument('--y_t_coeff', default=4, type=int,
                      help='Coefficient C of y=1-cos(Ct)')
    parser.add_argument('--num_time_steps', default=400, type=int,
                      help='Number of time steps to model')

    parser.add_argument('--extra_t', default=0.4, type=float,
                        help='Extra time to build the model as a straight line before & after the domain')

    parser.add_argument('--width', default=134.0, type=float,
                        help='How far apart to make the endpoints of the curve.  Note that the curve itself may extend past the endpoints')
    parser.add_argument('--y_scale', default=0.8, type=float,
                        help='Make the model a little squished or stretched vertically')

    # TODO: refactor the output_name
    parser.add_argument('--output_name', default='cycloid.stl',
                        help='Where to put the stl')

    args = parser.parse_args()

    if args.domain is None:
        args.domain = math.pi * 2 / math.gcd(args.x_t_coeff, args.y_t_coeff)
    
    return args
    

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_cycloid(args), args.output_name)

if __name__ == '__main__':
    main()

