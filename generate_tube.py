import argparse
import math
import marble_path

def generate_tube(args):
    def x_t(time_step):
        return 0

    def y_t(time_step):
        return args.length * time_step / args.time_steps

    angle = args.slope_angle / 180 * math.pi
    # - so a positive slope represents down.  TODO: not sure that was a great decision
    tan_angle = -math.tan(angle)
    def z_t(time_step):
        # reuse the function in case the other definition changes
        y = y_t(time_step)
        z = tan_angle * y
        return z

    def r_t(time_step):
        return 0

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.time_steps):
        yield triangle

    
def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl tube.')

    marble_path.add_tube_arguments(parser,
                                   default_slope_angle=2.9,
                                   default_output_name='tube.stl')
    
    parser.add_argument('--length', default=50, type=float,
                        help='Length of the tube')
    parser.add_argument('--time_steps', default=100, type=int,
                        help='How refined to make the tube')

    args = parser.parse_args(args=sys_args)
    return args

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_tube(args), args.output_name)

            
if __name__ == '__main__':
    main()
