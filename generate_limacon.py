import argparse
import math
import marble_path

"""
Produces the bottom part of a limacon curve, specifically, the loop.

The defaults produce a nice looking curve.

python generate_limacon.py

The hole can be generated as follows:

python generate_limacon.py --tube_radius 10.5 --wall_thickness 11 --tube_start_angle 0 --tube_end_angle 360

There are parameters to make the limacon stretched in different directions.
"""

def limacon_derivative(theta, x_scale, y_scale, a, b):
    # x(t) = math.cos(theta) * (a - b * math.cos(theta))
    # y(t) = math.sin(theta) * (a - b * math.cos(theta))
    # derivatives are fun!
    # x(t) =  -math.sin(theta) * (a - b * math.cos(theta)) + b * math.cos(theta) * math.sin(theta)
    # y(t) =   math.cos(theta) * (a - b * math.cos(theta)) + b * math.sin(theta) * math.sin(theta)
    # and then of course we scale it by x_scale, y_scale
    return (x_scale * (-math.sin(theta) * (a - b * math.cos(theta)) + b * math.cos(theta) * math.sin(theta)),
            y_scale * ( math.cos(theta) * (a - b * math.cos(theta)) + b * math.sin(theta) * math.sin(theta)))


def get_normal_rotation(theta, x_scale, y_scale, a, b):
    # there is a discontinuity in the derivative at theta = 0.0
    # fortunately, we know it will be heading south at that point
    if theta == 0.0:
        return 180
    dx, dy = limacon_derivative(theta, x_scale, y_scale, a, b)
    rotation = math.asin(dx / (dx ** 2 + dy ** 2) ** 0.5)
    if dx > 0 and dy > 0:
        # this gives us a negative rotation, meaning to the right
        rotation = -rotation
    elif dx > 0 and dy < 0:
        rotation = rotation + math.pi
    elif dx < 0 and dy > 0:
        rotation = -rotation
    else: # dx < 0 and dy < 0
        rotation = rotation + math.pi

    return rotation * 180 / math.pi


def generate_limacon(args):
    # the domain of the limacon will be -domain_size to +domain_size
    domain_size = args.domain_size
    min_time = -domain_size
    time_step_width = (domain_size * 2) / (args.time_steps)

    def theta_t(time_step):
        return min_time + time_step_width * time_step
        
    def x_t(time_step):
        theta = theta_t(time_step)
        r = args.constant_factor - args.cosine_factor * math.cos(theta)
        return math.cos(theta) * r

    def y_t(time_step):
        theta = theta_t(time_step)
        r = args.constant_factor - args.cosine_factor * math.cos(theta)
        return math.sin(theta) * r

    min_y = min(y_t(y) for y in range(0, args.time_steps+1))
    max_y = max(y_t(y) for y in range(0, args.time_steps+1))
    y_scale = args.length / (max_y - min_y)

    min_x = min(x_t(x) for x in range(0, args.time_steps+1))
    max_x = max(x_t(x) for x in range(0, args.time_steps+1))
    if args.width is None:
        x_scale = y_scale
    else:
        x_scale = args.width / (max_x - min_x)

    def scaled_x_t(time_step):
        return (x_t(time_step) - min_x) * x_scale
    
    def scaled_y_t(time_step):
        return (y_t(time_step) - min_y) * y_scale

    z_t = marble_path.arclength_height_function(scaled_x_t, scaled_y_t, args.time_steps, args.slope_angle)

    def r_t(time_step):
        theta = theta_t(time_step)
        return get_normal_rotation(theta, x_scale, y_scale, args.constant_factor, args.cosine_factor)

    print("Center of tube at time step 0: ", scaled_x_t(0), scaled_y_t(0))
    print("Angle of tube: ", r_t(0))

    for triangle in marble_path.generate_path(x_t=scaled_x_t, y_t=scaled_y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.time_steps):
        yield triangle    


def balance_domain(constant_factor, cosine_factor):
    """
    Given the parameters of the curve, find a theta for which the mass
    on both sides of the line between the endpoints is balanced.

    Calculation method is to sum x * m (approximated numerically) and
    return when sum(x * m) / m crosses x.  We note that the theta
    where the x derivative is 0 is a good place to start looking for
    this crossing, since it is impossible to be balanced before then.

    -math.sin(theta) * (a - b * math.cos(theta)) + b * math.cos(theta) * math.sin(theta) = 0
       -> drop the sin, since this will not be theta = 0 or theta = pi
    -a + 2b * math.cos(theta) = 0
    math.cos(theta) = a/2b
    theta = math.acos(a/2b)

    As an approximation, we treat the tube as a point mass, although
    this changes the effect of the tube.

    return value is theta, in radians
    """
    mass = 0.0
    torque = 0.0
    theta = math.acos(constant_factor / 2.0 / cosine_factor)
    for i in range(math.floor(math.pi * 2 * 1000)):
        t = i / 1000
        x1 = math.cos(t) * (constant_factor - cosine_factor * math.cos(t))
        x2 = math.cos(t+0.001) * (constant_factor - cosine_factor * math.cos(t + 0.001))
        y1 = math.cos(t) * (constant_factor - cosine_factor * math.cos(t))
        y2 = math.cos(t+0.001) * (constant_factor - cosine_factor * math.cos(t + 0.001))
        delta_mass = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        mass = mass + delta_mass
        torque = torque + x1 * delta_mass
        if t > theta and torque / mass > x1:
            print("Balanced at t =", t)
            return t
    raise ValueError("Could not find balance point!")

    
        
    
def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl limacon.  Graph of r = a - b cos(theta)')

    marble_path.add_tube_arguments(parser, default_slope_angle=12.0, default_output_name='limacon.stl')

    parser.add_argument('--constant_factor', default=1, type=float,
                        help='The a in the "a - b cos(theta)"')
    parser.add_argument('--cosine_factor', default=2, type=float,
                        help='The b in the "a - b cos(theta)"')
    
    parser.add_argument('--time_steps', default=200, type=int,
                        help='How refined to make the limacon')

    parser.add_argument('--length', default=134, type=float,
                        help='Distance from one end to the other, ignoring the tube')
    parser.add_argument('--width', default=None, type=float,
                        help='Distance from left to right, ignoring the tube.  If None, the curve will be scaled to match the length')

    parser.add_argument('--domain_size', default=1.806, type=float,
                        help='Theta goes from -domain_size to domain_size')
    parser.add_argument('--auto_domain', dest='auto_domain',
                        default=True, action='store_true',
                        help='Dynamically calculate the domain by trying to balance the torque')
    parser.add_argument('--no_auto_domain', dest='auto_domain',
                        action='store_false',
                        help="Don't dynamically calculate the domain by trying to balance the torque")

    parser.set_defaults(tube_start_angle=-60)

    args = parser.parse_args(args=sys_args)
    if args.cosine_factor == 1.0:
        raise ValueError("Sorry, but b=1.0 causes a discontinuity in the derivative")
    if args.cosine_factor == 0.0:
        raise ValueError("Consider using generate_helix if you just want a circle")
    if args.cosine_factor < 0.0:
        raise ValueError("You can simply mirror the resulting curve and set cosine_factor > 0.0")
    if args.cosine_factor < 1.0:
        raise ValueError("0.0<b<1.0 not implemented yet")

    if args.auto_domain:
        args.domain_size = balance_domain(args.constant_factor, args.cosine_factor)
    
    return args


def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_limacon(args), args.output_name)
            
if __name__ == '__main__':
    main()
