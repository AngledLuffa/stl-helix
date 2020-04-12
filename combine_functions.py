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


def replace_kinks_with_circles(args, time_t, x_t, y_t, r_t, kink_args, num_time_steps):
    """Replaces a section of a path with a section of circle.

    Given a start and end time for replacing a kink, calculates the
    start and end of the kink.  This tells us the rotation needed for
    the circle.

    Note that the radius of the circle cannot be calculated exactly
    using this method.  There are four parameters we use to build the
    kink replacement: start location, end location, start angle, end
    angle.  A circle only has two degrees of freedom: center, radius.
    So the circle is overconstrained by one dimension.  The degree of
    freedom we give up is to specify the end location.  Instead, the
    radius is used as a parameter.  The recommended radius is whatever
    the tube radius is, as the tube self-intersecting is the problem
    we are trying to solve in the first place.

    Alternatively, we could use an ellipse, but that may just
    reintroduce a new kink if the eccentricity is too high.

    Assumes kinks are less than 180 degrees.
    """
    times = [time_t(t) for t in range(num_time_steps+1)]
    kink_locations = kink_args.kink_replace_circle    
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
        print("  Start x, y: %.4f %.4f" % (x0, y0))
        print("  End x, y:   %.4f %.4f" % (xn, yn))
        print("  Distance: %.4f" % distance)
        # this only works for isosceles kinks:
        # radius = (distance / 2) / math.sin(rotation / 2 * math.pi / 180)
        radius = kink_args.kink_replacement_radius

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
    parser.add_argument('--kink_replacement_radius', default=12.5, type=float,
                        help='How big to make the replacement circle')



def zero_circle_dimensions(x_0, y_0, r_0):
    """
    Calculate the radius and amount of circle needed to go to the origin

    Given x, y, and initial rotation, calculates how large to make a
    circle and how far around you need to go to get to the origin.

    Note that given an initial position, the fact that you want to go
    to the origin, and the initial rotation, there is exactly enough
    information for there to be one circle which fits those initial
    parameters.
    """
    phi = r_0 / 180 * math.pi

    rad_0 = -(x_0 ** 2 + y_0 ** 2) / (2 * x_0 * math.cos(phi) + 2 * y_0 * math.sin(phi))

    half_distance = 0.5 * (x_0 ** 2 + y_0 ** 2) ** 0.5
    theta = math.asin(half_distance / rad_0) * 2

    return rad_0, theta
    
def add_zero_circle(args, circle_start, num_time_steps, x_t, y_t, slope_angle_t, r_t):
    """
    Constructs a partial helix and either prepends or appends it to make a curve touch the origin.
    """
    helix_args = argparse.Namespace(**vars(args))
    if circle_start:
        r_0 = r_t(0)
        x_0 = x_t(0)
        y_0 = y_t(0)
    else:
        r_0 = r_t(num_time_steps)
        x_0 = x_t(num_time_steps)
        y_0 = y_t(num_time_steps)
    if abs(x_0) < 0.1 and abs(y_0) < 0.1:
        print("Not processing circle at %s of curve: already reaches %.4f %.4f" % ("start" if circle_start else "end", x_0, y_0))
        return num_time_steps, x_t, y_t, slope_angle_t, r_t
    print("Adding zero circle at the %s of the curve" % ("start" if circle_start else "end"))
    print("  Parameters for the ramp: r %.4f x %.4f y %.4f" % (r_0, x_0, y_0))
    rad_0, theta = zero_circle_dimensions(x_0, y_0, r_0)
    # TODO: determine if this was going backwards and needs more than half a loop

    if circle_start:
        helix_args.rotations = -theta / (2 * math.pi)
        helix_args.initial_rotation = r_0 - helix_args.rotations * 360
        helix_args.helix_radius = -rad_0
        helix_args.helix_sides = args.zero_circle_sides / helix_args.rotations
    else:
        helix_args.rotations = -theta / (2 * math.pi)
        helix_args.initial_rotation = r_0
        helix_args.helix_radius = -rad_0
        helix_args.helix_sides = args.zero_circle_sides / helix_args.rotations
    # TODO: allow for CW on/off ramps instead of just CCW
    helix_args.clockwise = False
    print("  Amount of loop: %.4f radians / %.4f rotations / %.4f sides" % (theta, helix_args.rotations, helix_args.helix_sides))
    print("  Initial rotation: %.4f" % helix_args.initial_rotation)
    print("  Radius of circle: %.4f" % helix_args.helix_radius)

    helix_x_t = generate_helix.helix_x_t(helix_args)
    helix_y_t = generate_helix.helix_y_t(helix_args)
    helix_r_t = generate_helix.helix_r_t(helix_args)
    helix_slope_t = lambda t: args.slope_angle

    #for i in range(args.zero_circle_sides+1):
    #    print("%d %.4f %.4f %.4f" % (i, helix_x_t(i), helix_y_t(i), helix_r_t(i)))
        
    if circle_start:
        helix_x_t0 = helix_x_t(args.zero_circle_sides) - x_0
        trans_x_t = lambda t: helix_x_t(t) - helix_x_t0

        helix_y_t0 = helix_y_t(args.zero_circle_sides) - y_0
        trans_y_t = lambda t: helix_y_t(t) - helix_y_t0
    else:
        trans_x_t = helix_x_t
        trans_y_t = helix_y_t

    if circle_start:
        x_t, y_t, slope_angle_t, r_t = append_functions(trans_x_t, trans_y_t, helix_slope_t, helix_r_t,
                                                        x_t, y_t, slope_angle_t, r_t,
                                                        args.zero_circle_sides)
        num_time_steps = num_time_steps + args.zero_circle_sides
        print("  Updated circle-to-zero at start of curve")
        print("  Start circle x, y: %.4f %.4f" % (x_t(0), y_t(0)))
        print("  Start curve x, y:  %.4f %.4f" % (x_t(args.zero_circle_sides), y_t(args.zero_circle_sides)))
        print("  End curve x, y:    %.4f %.4f" % (x_t(num_time_steps), y_t(num_time_steps)))
    else:
        x_t, y_t, slope_angle_t, r_t = append_functions(x_t, y_t, slope_angle_t, r_t,
                                                        trans_x_t, trans_y_t, helix_slope_t, helix_r_t,
                                                        num_time_steps)
        print("  Updated circle-to-zero at end of hypo")
        print("  Start curve x, y:  %.4f %.4f" % (x_t(0), y_t(0)))
        print("  End curve x, y:    %.4f %.4f" % (x_t(num_time_steps), y_t(num_time_steps)))
        num_time_steps = num_time_steps + args.zero_circle_sides
        print("  End cicle x, y:    %.4f %.4f" % (x_t(num_time_steps), y_t(num_time_steps)))

    return num_time_steps, x_t, y_t, slope_angle_t, r_t

def add_both_zero_circles(args, num_time_steps, x_t, y_t, slope_angle_t, r_t):
    """
    Adds zero circles at both the start and the end of a curve.
    """
    updated_functions = add_zero_circle(args=args,
                                        circle_start=True,
                                        num_time_steps=num_time_steps,
                                        x_t=x_t,
                                        y_t=y_t,
                                        slope_angle_t=slope_angle_t,
                                        r_t=r_t)
    num_time_steps, x_t, y_t, slope_angle_t, r_t = updated_functions

    updated_functions = add_zero_circle(args=args,
                                        circle_start=False,
                                        num_time_steps=num_time_steps,
                                        x_t=x_t,
                                        y_t=y_t,
                                        slope_angle_t=slope_angle_t,
                                        r_t=r_t)
    return updated_functions

def add_zero_circle_args(parser):
    parser.add_argument('--zero_circle', dest='zero_circle', default=False, action='store_true',
                        help='Go from wherever start_t and end_t wind up to 0,0 using a circle')
    parser.add_argument('--no_zero_circle', dest='zero_circle', action='store_false',
                        help="Don't go from wherever start_t and end_t wind up to 0,0 using a circle")
    parser.add_argument('--zero_circle_sides', default=36, type=int,
                        help='Number of sides to make the circle to the middle')

