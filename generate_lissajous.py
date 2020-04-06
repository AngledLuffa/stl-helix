import argparse
import math

import combine_functions
import generate_helix
import marble_path
import marble_util
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

python generate_lissajous.py --lissA 5 --lissB 0 --lissC 3 --overlaps "((-0.55,0.05),(-0.05, 0.55))" --overlap_separation 25 --y_scale 54 --x_scale 40 --slope_angle 4

kink removal: -0.12 to -0.2

"""

def replace_kinks_with_circles(args, time_t, x_t, y_t, r_t, kink_locations, num_time_steps):
    """
    Assumes kinks are less than 180 degrees
    """
    times = [time_t(t) for t in range(num_time_steps+1)]
    for kink in kink_locations:
        start_time = marble_util.get_time_step(times, kink[0])
        end_time = marble_util.get_time_step(times, kink[1])

        if start_time == end_time:
            print("Kink from %.4f to %.4f represents no time steps" % (kink[0], kink[1]))
            continue

        print("Smoothing kink from %.4f (%d) to %.4f (%d)" % (kink[0], start_time, kink[1], end_time))

        angle_start = r_t(start_time) % 360.0
        angle_end = r_t(end_time) % 360.0
        if angle_start < angle_end and angle_start + 180 > angle_end:
            clockwise = False
            rotation = angle_end - angle_start
        elif angle_start < angle_end:
            clockwise = True
            rotation = -(angle_start + 360 - angle_end)
        elif angle_end < angle_start and angle_end + 180 > angle_start:
            clockwise = True
            rotation = angle_start - angle_end
        elif angle_end < angle_start:
            clockwise = False
            rotation = 360 - angle_start + angle_end
        else:  # angle_start == angle_end
            raise ValueError("Need to add a straight tube here, but that is not implemented yet")

        print("  Start angle: %.4f  End angle: %.4f  Clockwise: %s  Rotation: %.4f" % (angle_start, angle_end, clockwise, rotation))

        x0 = x_t(start_time)
        y0 = y_t(start_time)
        xn = x_t(end_time)
        yn = y_t(end_time)
        distance = ((yn - y0) ** 2 + (xn - x0) ** 2) ** 0.5
        radius = (distance / 2) / math.sin(rotation / 2 * math.pi / 180)
        print("  Start x, y: %.4f %.4f" % (x0, y0))
        print("  End x, y:   %.4f %.4f" % (xn, yn))
        print("  Distance: %.4f   Radius of circle: %.4f" % (distance, radius))

        splice_time_steps = end_time - start_time
        helix_args = argparse.Namespace(**vars(args))
        helix_args.rotations = abs(rotation / 360)
        helix_args.initial_rotation = angle_end if clockwise else angle_start
        helix_args.helix_radius = abs(radius)
        helix_args.helix_sides = splice_time_steps / helix_args.rotations

        print("  Producing helix: rotations %.4f, initial rotation %.4f, radius %.4f" % (helix_args.rotations, helix_args.initial_rotation, helix_args.helix_radius))

        helix_x_t = generate_helix.helix_x_t(helix_args)
        helix_y_t = generate_helix.helix_y_t(helix_args)
        helix_r_t = generate_helix.helix_r_t(helix_args)
        #helix_slope_t = lambda t: args.slope_angle

        #for i in range(splice_time_steps+1):
        #    print(i, helix_x_t(i), helix_y_t(i), helix_r_t(i))

        #for i in range(splice_time_steps+1):
        #    print(i, helix_x_t(i), helix_y_t(i), helix_r_t(i))
        
        # don't care about slope_t for the following reason:
        # when the kink replacement has been spliced into the original
        # function, this could invalidate any use of slope_function to
        # fix overlaps.  therefore, slope_t can't even be calculated
        # until the kinks are already fixed
        x_t, y_t, _, r_t = combine_functions.splice_functions(x_t, y_t, None, r_t,
                                                              helix_x_t, helix_y_t, None, helix_r_t,
                                                              start_time, end_time)

        for i in range(start_time - 10, end_time + 10):
            print(i, x_t(i), y_t(i), r_t(i))

    return x_t, y_t, r_t
    

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
    
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    if args.kink_replace_circle:
        x_t, y_t, r_t = replace_kinks_with_circles(args=args,
                                                   time_t=time_t,
                                                   x_t=x_t,
                                                   y_t=y_t,
                                                   r_t=r_t,
                                                   kink_locations=args.kink_replace_circle,
                                                   num_time_steps=args.num_time_steps)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=None)
    
    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps, args.slope_angle)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle


def parse_kink_circles(arg):
    return marble_util.parse_tuple_tuple(arg, "--kink_replace_circle")


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

    parser.add_argument('--kink_replace_circle', default=None, type=parse_kink_circles,
                        help='Tuple (or list) of time spans to replace with circles in order to smooth kinks')
    
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

