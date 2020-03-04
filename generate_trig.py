import argparse
import math
import marble_path

"""
p173 has some interesting alterations to trig waves

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 6 --tube_method oval --tube_wall_height 8 --wall_thickness 3
"""

def generate_trig(args):
    max_t = args.end_t
    min_t = args.start_t

    def time_t(time_step):
        return min_t + (max_t - min_t) * time_step / args.num_time_steps

    scale = args.width / (max_t - min_t)

    def x_t(time_step):
        t = time_t(time_step)
        return scale * (t + math.sin(t) ** args.power)

    def y_t(time_step):
        t = time_t(time_step)
        return scale * args.y_coeff * math.sin(t)

    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps,
                                               slope_angle=args.slope_angle)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)



    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps):
        yield triangle    
    


def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for a random trig graph  p173 of Curves.')

    marble_path.add_tube_arguments(parser, default_slope_angle=5.0)

    parser.add_argument('--num_time_steps', default=400, type=int,
                      help='Number of time steps to model')

    parser.add_argument('--power', default=3, type=int,
                        help='Power to put on (x=t+sin^k t, y=B sin t)')
    parser.add_argument('--y_coeff', default=2, type=float,
                        help='B in the expression (x=t+sin^k t, y=B sin t)')

    parser.add_argument('--start_t', default=0.0, type=float,
                        help='Curve goes from start_t to end_t')
    parser.add_argument('--end_t', default=4.0 * math.pi, type=float,
                        help='Curve goes from start_t to end_t')

    parser.add_argument('--width', default=134.0, type=float,
                        help='How far apart to make the endpoints of the curve.  Note that the curve itself may extend past the endpoints')

    parser.add_argument('--output_name', default='trig.stl',
                        help='Where to put the stl')
    
    args = parser.parse_args()
    return args
    
    

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_trig(args), args.output_name)
            
if __name__ == '__main__':
    main()

