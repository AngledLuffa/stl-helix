import argparse
import math

import marble_path
import slope_function

"""
p173 has some interesting alterations to trig waves

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 9 --tube_method oval --tube_wall_height 8 --wall_thickness 3


python generate_trig.py --y_coeff 3 --power 2 --slope_angle 11 --tube_method oval --tube_wall_height 8 --wall_thickness 3 --tube_radius 12.5  --kinks "(1.5708, 4.7124, 7.8540, 10.9956)" --kink_width 1.0 --kink_slope 0.5 --kink_sharpness 0.25 --output_name trig.stl

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 11 --tube_method oval --tube_wall_height 8 --wall_thickness 11 --tube_radius 10.5  --kinks "(1.5708, 4.7124, 7.8540, 10.9956)" --kink_width 1.0 --kink_slope 0.5 --kink_sharpness 0.25 --output_name trig_hole.stl


this is
x(t) = t + math.sin(t) ** 2
y(t) = 3 math.sin(t)

from 0 to 4pi

issue here: for some reason the corresponding inner tube has some
holes.  Could possibly fix that by merging neighboring tube chunks
using a 3d union algorithm.  Fortunately they have libraries for that
rather just doing it ourselves

"""

def generate_trig(args):
    max_t = args.end_t
    min_t = args.start_t

    def time_t(time_step):
        return min_t + (max_t - min_t) * time_step / args.num_time_steps

    def x_t(time_step):
        t = time_t(time_step)
        return args.scale * (t + math.sin(t) ** args.power)

    def y_t(time_step):
        t = time_t(time_step)
        return args.scale * args.y_coeff * math.sin(t)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlaps=None,
                                                  overlap_separation=None,
                                                  kink_args=args)
        
    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps,
                                               slope_angle_t=slope_angle_t)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle    
    

def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for a random trig graph  p173 of Curves.')

    marble_path.add_tube_arguments(parser, default_slope_angle=5.0)
    slope_function.add_kink_args(parser)

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

    parser.add_argument('--scale', default=None, type=float,
                        help='Multiple all samples by this value.  If set to None, will be calculated from the width.')

    # TODO: refactor output_name
    parser.add_argument('--output_name', default='trig.stl',
                        help='Where to put the stl')
    
    args = parser.parse_args()

    if args.scale is None:
        max_t = args.end_t
        min_t = args.start_t
        args.scale = args.width / (max_t - min_t)
        print("Calculated scale to be ", args.scale)
    
    return args
    
    

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_trig(args), args.output_name)
            
if __name__ == '__main__':
    main()

