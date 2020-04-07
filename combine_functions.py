import argparse
import math

import generate_helix
import marble_util

def append_functions(x1_t, y1_t, slope1_t, r1_t,
                     x2_t, y2_t, slope2_t, r2_t,
                     inflection_t):
    """
    Combine two x, y, slope, r functions into one function

    Second function will be offset in x&y so it matches the first function at inflection_t.

    Slope is assumed to not need that offset.

    r_t must be combined as the "arclength" manner of generating it
    will have a very noticeable discontinuity at inflection_t otherwise
    """
    x_off = x1_t(inflection_t) - x2_t(0)
    y_off = y1_t(inflection_t) - y2_t(0)
    def x_t(t):
        if t < inflection_t:
            return x1_t(t)
        else:
            return x2_t(t - inflection_t) + x_off

    def y_t(t):
        if t < inflection_t:
            return y1_t(t)
        else:
            return y2_t(t - inflection_t) + y_off

    def slope_t(t):
        if t < inflection_t:
            return slope1_t(t)
        else:
            return slope2_t(t - inflection_t)

    def r_t(t):
        if t < inflection_t:
            return r1_t(t)
        else:
            return r2_t(t - inflection_t)
        
    return x_t, y_t, slope_t, r_t

def splice_functions(x1_t, y1_t, slope1_t, r1_t,
                     x2_t, y2_t, slope2_t, r2_t,
                     start_splice, end_splice):
    """
    Splice function 2 into function 1.  
    time 0..end-start from function 2 will be implanted into function 1.

    For example, can replace a kink with a small circular attachment.

    Second function will be offset in x&y so it matches the first function at start_splice
    First function will then be offset to match the splice.
    slope_t needs to be spliced to avoid discontinuities when using the arclength method
    in marble_path
    """

    x_s, y_s, slope_s, r_s = append_functions(x1_t, y1_t, slope1_t, r1_t,
                                              x2_t, y2_t, slope2_t, r2_t,
                                              start_splice)

    x_f, y_f, slope_f, r_f = append_functions(x_s, y_s, slope_s, r_s,
                                              lambda t: x1_t(t + end_splice),
                                              lambda t: y1_t(t + end_splice),
                                              lambda t: slope1_t(t + end_splice),
                                              lambda t: r1_t(t + end_splice),
                                              end_splice)

    return x_f, y_f, slope_f, r_f


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
        helix_args.initial_rotation = angle_start
        helix_args.helix_radius = abs(radius)
        helix_args.helix_sides = splice_time_steps / helix_args.rotations
        helix_args.clockwise = clockwise

        print("  Producing helix: rotations %.4f, initial rotation %.4f, radius %.4f" % (helix_args.rotations, helix_args.initial_rotation, helix_args.helix_radius))

        helix_x_t = generate_helix.helix_x_t(helix_args)
        helix_y_t = generate_helix.helix_y_t(helix_args)
        helix_r_t = generate_helix.helix_r_t(helix_args)
        #helix_slope_t = lambda t: args.slope_angle

        #for i in range(splice_time_steps+1):
        #    print(i, helix_x_t(i), helix_y_t(i), helix_r_t(i))
        
        # don't care about slope_t for the following reason:
        # when the kink replacement has been spliced into the original
        # function, this could invalidate any use of slope_function to
        # fix overlaps.  therefore, slope_t can't even be calculated
        # until the kinks are already fixed
        x_t, y_t, _, r_t = splice_functions(x_t, y_t, None, r_t,
                                            helix_x_t, helix_y_t, None, helix_r_t,
                                            start_time, end_time)

        #for i in range(start_time - 10, end_time + 10):
        #    print(i, x_t(i), y_t(i), r_t(i))

    return x_t, y_t, r_t
    

def parse_kink_circles(arg):
    return marble_util.parse_tuple_tuple(arg, "--kink_replace_circle")

def add_kink_circle_args(parser):
    parser.add_argument('--kink_replace_circle', default=None, type=parse_kink_circles,
                        help='Tuple (or list) of time spans to replace with circles in order to smooth kinks')

