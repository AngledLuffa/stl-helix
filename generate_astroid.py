import argparse
import math
import marble_path


# astroid has parametric equations as follows:
# x = a cos^3 t
# y = a sin^3 t
# where a is the radius of the large circle
# (an astroid is a small circle revolved inside a large circle)

# so the inner radius is half the outer radius

def astroid_step(outer_radius, corner_t, corner_rotation, astroid_power, time_step, subdivisions_per_side):
    # in this time span, we are on the astroid itself.  return the astroid calculation
    if time_step >= subdivisions_per_side and time_step <= subdivisions_per_side * 2:
        time_step = time_step - subdivisions_per_side
        astroid_t = (90 - corner_t * 2) / subdivisions_per_side * time_step + corner_t
        return (outer_radius * math.cos(astroid_t / 180 * math.pi) ** astroid_power,
                outer_radius * math.sin(astroid_t / 180 * math.pi) ** astroid_power)
    # to do the rounded corners, we will simply put a circle centered
    # on the axis at the location where the astroid is cut off

    # actually this is just the tube radius
    radius = outer_radius * math.sin(corner_t * math.pi / 180) ** astroid_power
    if time_step < subdivisions_per_side:
        center = (outer_radius * math.cos(corner_t / 180 * math.pi) ** astroid_power,
                  outer_radius * math.sin(corner_t / 180 * math.pi) ** astroid_power)
        center = (center[0] - math.cos(corner_rotation / 180 * math.pi) * radius,
                  center[1] - math.sin(corner_rotation / 180 * math.pi) * radius)
        angle = corner_rotation * time_step / subdivisions_per_side * math.pi / 180
        return (center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius)
    else:
        center = (outer_radius * math.sin(corner_t / 180 * math.pi) ** astroid_power,
                  outer_radius * math.cos(corner_t / 180 * math.pi) ** astroid_power)
        center = (center[0] - math.sin(corner_rotation / 180 * math.pi) * radius,
                  center[1] - math.cos(corner_rotation / 180 * math.pi) * radius)
        time_step = time_step - subdivisions_per_side * 2
        angle = (90 - corner_rotation + corner_rotation * time_step / subdivisions_per_side) * math.pi / 180
        center = (center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius)
        return center
    

def astroid_derivative(outer_radius, theta, astroid_power):
    # astroid is f(t) = (a cos^3, a sin^3)
    # derivative of the astroid x', y' is
    #   a * (-3 * cos^2 t * sin t, 3 * sin^2 t * cos t)
    # we can generalize this to higher power astroids
    theta = theta / 180 * math.pi
    return (-astroid_power * outer_radius * math.cos(theta) ** (astroid_power - 1) * math.sin(theta),
             astroid_power * outer_radius * math.sin(theta) ** (astroid_power - 1) * math.cos(theta))


def get_normal_rotation(outer_radius, theta, astroid_power):
    # note that we drop the - because we want to rotate to the left by a positive amount
    dx, dy = astroid_derivative(outer_radius, theta, astroid_power)
    dx = -dx
    return math.asin(dx / (dx ** 2 + dy ** 2) ** 0.5) * 180 / math.pi

def tube_angle(outer_radius, corner_t, corner_rotation, astroid_power, time_step, subdivisions_per_side):
    if time_step < subdivisions_per_side:
        return corner_rotation * time_step / subdivisions_per_side
    if time_step > subdivisions_per_side * 2:
        time_step = time_step - subdivisions_per_side * 2
        return (90 - corner_rotation) + corner_rotation * time_step / subdivisions_per_side

    time_step = time_step - subdivisions_per_side
    astroid_t = (90 - corner_t * 2) / subdivisions_per_side * time_step + corner_t
    return get_normal_rotation(outer_radius, astroid_t, astroid_power)


def find_corner(outer_radius, tube_radius, astroid_power):
    """
    Somewhere between 0 and 45 is an angle at which the astroid is
    close enough that the tube width on one side of the corner hits
    the tube on the other side of the corner

    We binary search for that spot, using a tolerance of 0.001

    Note that we need to take into account the rotation of the tube
    """
    upper_bound = 45.0
    lower_bound = 0.0

    while upper_bound > lower_bound + 0.001:
        current_test = (upper_bound + lower_bound) / 2.0
        rotation = get_normal_rotation(outer_radius, current_test, astroid_power)
        y = (outer_radius * math.sin(current_test / 180 * math.pi) ** astroid_power -
             tube_radius * math.sin(rotation / 180 * math.pi))
        if y == 0:
            upper_bound = lower_bound = current_test
            break
        elif y > 0:
            upper_bound = current_test
        else:
            lower_bound = current_test
    return upper_bound, get_normal_rotation(outer_radius, upper_bound, astroid_power)
    

def generate_astroid(args):
    # there are 4 corners in the astroid
    # we want to chop off those corners and replace them with approximated circles
    # to do this, we first calculate where the corners occur
    # this happens when the tube on one side of the corner touches the tube on the other
    # we will need to keep in mind the angle of the tube at that point
    corner_t, corner_rotation = find_corner(args.outer_radius, args.tube_radius, args.astroid_power)

    num_time_steps = args.subdivisions_per_side * 3   # the extra factor of 3 is for the rounded corners

    #for i in range(num_time_steps):
    #    print(i,
    #          astroid_step(args.outer_radius, corner_t, corner_rotation, args.astroid_power, i, args.subdivisions_per_side),
    #          tube_angle(args.outer_radius, corner_t, corner_rotation, args.astroid_power, i, args.subdivisions_per_side))

    def x_t(time_step):
        return astroid_step(args.outer_radius, corner_t, corner_rotation, args.astroid_power, time_step, args.subdivisions_per_side)[0]
    
    def y_t(time_step):
        return astroid_step(args.outer_radius, corner_t, corner_rotation, args.astroid_power, time_step, args.subdivisions_per_side)[1]
    
    def z_t(time_step):
        # TODO: add a slope
        return 0.0

    def r_t(time_step):
        return tube_angle(args.outer_radius, corner_t, corner_rotation, args.astroid_power, time_step, args.subdivisions_per_side)
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps,
                                              slope_angle=0.0):
        yield triangle

     

def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl astroid.')

    marble_path.add_tube_arguments(parser)
    # outer_radius used for measurements because most articles on the
    # subject start from the outer radius.  for example,
    # https://en.wikipedia.org/wiki/Astroid
    parser.add_argument('--outer_radius', default=52, type=float,
                        help='Measurement from the center to the tip of the astroid.  inner_radius will be 1/2 this')
    parser.add_argument('--subdivisions_per_side', default=50, type=int,
                        help='Subdivisions for each of the 4 sides of the astroid.  Note that there will also be rounded corners adding more subdivisions')
    parser.add_argument('--astroid_power', default=3, type=int,
                        help='Exponent on the various astroid equations.  3 is disappointingly non-curved')

    parser.add_argument('--output_name', default='astroid.stl',
                        help='Where to put the stl')

    args = parser.parse_args()

    if args.outer_radius / 2 < args.tube_radius:
        raise ValueError("Impossible to make an astroid where the tube radius {} is greater than the inner radius {}".format(args.tube_radius, args.outer_radius / 2))
    
    return args


def main():
    args = parse_args()
    marble_path.print_args(args)

    #generate_astroid(args)
    marble_path.write_stl(generate_astroid(args), args.output_name)

            
if __name__ == '__main__':
    main()
