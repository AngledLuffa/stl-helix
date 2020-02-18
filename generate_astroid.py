import argparse
import math
import marble_path

from enum import Enum

class Cusp(Enum):
    OFFSET = 1
    CHOP = 2

# astroid has parametric equations as follows:
# x = a cos^3 t
# y = a sin^3 t
# where a is the radius of the large circle
# (an astroid is a small circle revolved inside a large circle)

# so the inner radius is half the outer radius

def astroid_step(outer_radius, cusp_method, tube_radius, corner_t, corner_rotation,
                 astroid_power, time_step, subdivisions_per_side):
    quadrant = math.floor(time_step / (subdivisions_per_side * 3)) % 4
    time_step = time_step % (subdivisions_per_side * 3)

    # in this time span, we are on the astroid itself.  return the astroid calculation
    if time_step >= subdivisions_per_side and time_step <= subdivisions_per_side * 2:
        time_step = time_step - subdivisions_per_side
        # TODO: maybe we can set corner_t earlier for this method and
        # then process the center of the circles on the ends differently
        # the issue is that going all the way to 0 angle and then
        # starting the curve again makes a bit of a discontinuity
        # where the tube is "going backwards" and that effect
        # dominates the very short distances covered by the circular
        # caps on the tube.  (that's the theory, at least)
        if cusp_method is Cusp.OFFSET:
            corner_t = 90 / subdivisions_per_side
        astroid_t = (90 - corner_t * 2) / subdivisions_per_side * time_step + corner_t
        location = (outer_radius * math.cos(astroid_t / 180 * math.pi) ** astroid_power,
                    outer_radius * math.sin(astroid_t / 180 * math.pi) ** astroid_power)

        if cusp_method is Cusp.OFFSET:
            location = (location[0] + tube_radius, location[1] + tube_radius)
    elif time_step < subdivisions_per_side:
        # to do the rounded corners, we will simply put a circle centered
        # on the axis at the location where the astroid is cut off

        center = (outer_radius * math.cos(corner_t / 180 * math.pi) ** astroid_power,
                  outer_radius * math.sin(corner_t / 180 * math.pi) ** astroid_power)
        center = (center[0] - math.cos(corner_rotation / 180 * math.pi) * tube_radius,
                  center[1] - math.sin(corner_rotation / 180 * math.pi) * tube_radius)
        angle = corner_rotation * time_step / subdivisions_per_side * math.pi / 180
        location = (center[0] + math.cos(angle) * tube_radius,
                    center[1] + math.sin(angle) * tube_radius)
        if cusp_method is Cusp.OFFSET:
            location = (location[0] + tube_radius, location[1] + tube_radius)
    else:
        center = (outer_radius * math.sin(corner_t / 180 * math.pi) ** astroid_power,
                  outer_radius * math.cos(corner_t / 180 * math.pi) ** astroid_power)
        center = (center[0] - math.sin(corner_rotation / 180 * math.pi) * tube_radius,
                  center[1] - math.cos(corner_rotation / 180 * math.pi) * tube_radius)
        time_step = time_step - subdivisions_per_side * 2
        angle = (90 - corner_rotation + corner_rotation * time_step / subdivisions_per_side) * math.pi / 180
        location = (center[0] + math.cos(angle) * tube_radius,
                    center[1] + math.sin(angle) * tube_radius)
        if cusp_method is Cusp.OFFSET:
            location = (location[0] + tube_radius, location[1] + tube_radius)

    if quadrant == 0:
        return location
    elif quadrant == 1:
        return (-location[1], location[0])
    elif quadrant == 2:
        return (-location[0], -location[1])
    else:
        return (location[1], -location[0])

def astroid_derivative(outer_radius, theta, astroid_power):
    # astroid is f(t) = (a cos^3, a sin^3)
    # derivative of the astroid x', y' is
    #   a * (-3 * cos^2 t * sin t, 3 * sin^2 t * cos t)
    # we can generalize this to higher power astroids
    theta = theta / 180 * math.pi
    return (-astroid_power * outer_radius * math.cos(theta) ** (astroid_power - 1) * math.sin(theta),
             astroid_power * outer_radius * math.sin(theta) ** (astroid_power - 1) * math.cos(theta))


def get_normal_rotation(outer_radius, theta, astroid_power):
    # note that these extremes can happen when cusp_method=OFFSET
    if theta == 0.0:
        return 90.0
    # note that we drop the - because we want to rotate to the left by a positive amount
    dx, dy = astroid_derivative(outer_radius, theta, astroid_power)
    dx = -dx
    return math.asin(dx / (dx ** 2 + dy ** 2) ** 0.5) * 180 / math.pi

def tube_angle(outer_radius, cusp_method, corner_t, corner_rotation,
               astroid_power, time_step, subdivisions_per_side):
    if cusp_method is Cusp.OFFSET:
        corner_t = 90 / subdivisions_per_side
    quadrant = math.floor(time_step / (subdivisions_per_side * 3)) % 4
    time_step = time_step % (subdivisions_per_side * 3)
    
    if time_step < subdivisions_per_side:
        rotation = corner_rotation * time_step / subdivisions_per_side
    elif time_step > subdivisions_per_side * 2:
        time_step = time_step - subdivisions_per_side * 2
        rotation = (90 - corner_rotation) + corner_rotation * time_step / subdivisions_per_side
    else:
        time_step = time_step - subdivisions_per_side
        astroid_t = (90 - corner_t * 2) / subdivisions_per_side * time_step + corner_t
        rotation = get_normal_rotation(outer_radius, astroid_t, astroid_power)

    return rotation + quadrant * 90

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
    if args.cusp_method is Cusp.CHOP:
        corner_t, corner_rotation = find_corner(args.outer_radius, args.tube_radius, args.astroid_power)
        x_offset = y_offset = 0
    elif args.cusp_method is Cusp.OFFSET:
        corner_t = 0.0
        corner_rotation = 90.0
        x_offset = y_offset = args.tube_radius
    else:
        raise ValueError('Not supported: %s' % args.cusp_method)

    num_time_steps = args.subdivisions_per_side * 12   # the extra factor of 3 is for the rounded corners

    #for i in range(num_time_steps):
    #    print(i,
    #          astroid_step(args.outer_radius, corner_t, corner_rotation, args.astroid_power, i, args.subdivisions_per_side),
    #          tube_angle(args.outer_radius, corner_t, corner_rotation, args.astroid_power, i, args.subdivisions_per_side))

    # start at 45 degrees so we can connect easily to the post in the middle
    time_step_offset = int(args.subdivisions_per_side * 1.5)

    # TODO: might be nice to make a combined x_y_t that saves on these calculations
    def x_t(time_step):
        return astroid_step(outer_radius=args.outer_radius,
                            cusp_method=args.cusp_method,
                            tube_radius=args.tube_radius,
                            corner_t=corner_t,
                            corner_rotation=corner_rotation,
                            astroid_power=args.astroid_power,
                            time_step=time_step + time_step_offset,
                            subdivisions_per_side=args.subdivisions_per_side)[0]
    
    def y_t(time_step):
        return astroid_step(outer_radius=args.outer_radius,
                            cusp_method=args.cusp_method,
                            tube_radius=args.tube_radius,
                            corner_t=corner_t,
                            corner_rotation=corner_rotation,
                            astroid_power=args.astroid_power,
                            time_step=time_step + time_step_offset,
                            subdivisions_per_side=args.subdivisions_per_side)[1]

    z_t = marble_path.arclength_slope_function(x_t, y_t, num_time_steps, args.slope_angle)

    def r_t(time_step):
        return tube_angle(outer_radius=args.outer_radius,
                          cusp_method=args.cusp_method,
                          corner_t=corner_t,
                          corner_rotation=corner_rotation,
                          astroid_power=args.astroid_power,
                          time_step=time_step + time_step_offset,
                          subdivisions_per_side=args.subdivisions_per_side)
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps,
                                              slope_angle=-args.slope_angle):
        yield triangle


def closest_approach_to_radius(cusp_method, tube_radius, closest_approach, astroid_power):
    # closest approach is at 45 degrees
    # so x, y = a cos^k t
    #    x, y = a / sqrt(2)^k
    #    d = sqrt(x^2 + y^2) = sqrt(2) x
    #    closest_approach / sqrt(2) = a / sqrt(2)^k
    #    a = closest_approach * sqrt(2)^(k-1)
    if cusp_method is Cusp.OFFSET:
        # factor of sqrt(2) is because we move by tube_radius in both x & y
        closest_approach = closest_approach - tube_radius * 2 ** 0.5
        if closest_approach <= 0:
            raise ValueError("Not enough room for Cusp.OFFSET")
    elif cusp_method is Cusp.CHOP:
        pass
    else:
        raise ValueError("Cusp method {} not handled".format(cusp_method))
    return closest_approach * 2 ** ((astroid_power - 1) / 2)
     

def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl astroid.')

    marble_path.add_tube_arguments(parser)
    # outer_radius used for measurements because most articles on the
    # subject start from the outer radius.  for example,
    # https://en.wikipedia.org/wiki/Astroid
    parser.add_argument('--outer_radius', default=52, type=float,
                        help='Measurement from the center to the tip of the astroid.  inner_radius will be 1/2 this (for a power 3 astroid)')
    parser.add_argument('--closest_approach', default=None, type=float,
                        help='Measurement from 0,0 to the closest point of the tube center.  Will override outer_radius.  26 for a 31mm connector connecting exactly to the tube')
    parser.add_argument('--subdivisions_per_side', default=50, type=int,
                        help='Subdivisions for each of the 4 sides of the astroid.  Note that there will also be rounded corners adding more subdivisions')
    parser.add_argument('--astroid_power', default=3, type=int,
                        help='Exponent on the various astroid equations.  3 is disappointingly non-curved')

    parser.add_argument('--cusp_method', default=Cusp.OFFSET, type=lambda x: Cusp[x.upper()],
                        help='How to handle the corners.  OFFSET = offset by tube width, CHOP = chop when the cusp is too close to the axis')

    parser.add_argument('--slope_angle', default=8.0, type=float,
                        help='Angle to go down when traveling')
    
    parser.add_argument('--output_name', default='astroid.stl',
                        help='Where to put the stl')

    args = parser.parse_args()

    if args.closest_approach is not None:
        args.outer_radius = closest_approach_to_radius(args.cusp_method, args.tube_radius,
                                                       args.closest_approach, args.astroid_power)
    
    if args.outer_radius / 2 < args.tube_radius and args.cusp_method is not Cusp.OFFSET:
        raise ValueError("Impossible to make an astroid where the tube radius {} is greater than the inner radius {}".format(args.tube_radius, args.outer_radius / 2))
    
    return args


def main():
    args = parse_args()
    marble_path.print_args(args)

    #generate_astroid(args)
    marble_path.write_stl(generate_astroid(args), args.output_name)

            
if __name__ == '__main__':
    main()
