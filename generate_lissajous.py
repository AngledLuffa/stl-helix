import argparse
import math

import marble_path
import slope_function


"""
Implements various curves from section 9.4 of "Practical Handbook of Curve Design and Generation"

TODO: One idea:
figure 9.4.3
basic Lissajous, A=3, B=0, C=2
time 1.22 .. 2.78
x_scale 35, y_scale 60
Issue with this one is there is a pretty noticeable kink at the turns.  Also, the ending is a little too curved


TODO: another similar idea:
A=5, B=0, C=3
time -0.74 .. 0.74
--y_scale 54 --x_scale 40
same general issue, kink at the turns.  Ending is not curved but needs an extension to fit the posts

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05))" --overlap_separation 25 --y_scale 54 --x_scale 40 --slope_angle 4

kink removal: -0.12 to -0.2

"""

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
    
    # TODO: need to fix kinks

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=None)
    
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps, args.slope_angle)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle




def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a lissajous curve or its relatives')

    marble_path.add_tube_arguments(parser, default_slope_angle=10.0, default_output_name='lissajous.stl')
    slope_function.add_overlap_args(parser)

    parser.add_argument('--lissA', default=5, type=float,
                        help='value A in the lissajous formula')
    parser.add_argument('--lissB', default=0, type=float,
                        help='value B in the lissajous formula')
    parser.add_argument('--lissC', default=3, type=float,
                        help='value C in the lissajous formula')

    parser.add_argument('--start_t', default=-0.74, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=0.74, type=float,
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
