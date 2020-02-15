import argparse
import math
import marble_path

def limacon_derivative(theta, x_scale, y_scale, a, b):
    # x(t) = math.cos(theta) * (a - b * math.cos(theta))
    # y(t) = math.sin(theta) * (a - b * math.cos(theta))
    # derivatives are fun!
    # x(t) =  -math.sin(theta) * (a - b * math.cos(theta)) + b * math.cos(theta) * math.sin(theta)
    # y(t) =   math.cos(theta) * (a - b * math.cos(theta)) + b * math.sin(theta) * math.sin(theta)
    # and then of course we scale it by x_scale, y_scale
    return (-math.sin(theta) * (a - b * math.cos(theta)) + b * math.cos(theta) * math.sin(theta),
             math.cos(theta) * (a - b * math.cos(theta)) + b * math.sin(theta) * math.sin(theta))


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
    domain_size = math.pi / 2 + 0.3
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

    z_t = marble_path.arclength_slope_function(scaled_x_t, scaled_y_t, args.time_steps, args.slope_angle)

    def r_t(time_step):
        theta = theta_t(time_step)
        return get_normal_rotation(theta, x_scale, y_scale, args.constant_factor, args.cosine_factor)

    for triangle in marble_path.generate_path(x_t=scaled_x_t, y_t=scaled_y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.time_steps,
                                              slope_angle=-args.slope_angle):
        yield triangle    
    
    
def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl limacon.  Graph of r = a - b cos(theta)')

    marble_path.add_tube_arguments(parser)
    

    parser.add_argument('--output_name', default='limacon.stl',
                        help='Where to put the stl')

    parser.add_argument('--constant_factor', default=1, type=float,
                        help='The a in the "a - b cos(theta)"')
    parser.add_argument('--cosine_factor', default=2.5, type=float,
                        help='The b in the "a - b cos(theta)"')
    
    parser.add_argument('--slope_angle', default=10, type=float,
                        help='Angle to go down when traveling')

    parser.add_argument('--time_steps', default=200, type=int,
                        help='How refined to make the limacon')

    parser.add_argument('--length', default=134, type=float,
                        help='Distance from one end to the other, ignoring the tube')
    parser.add_argument('--width', default=None, type=float,
                        help='Distance from left to right, ignoring the tube.  If None, the curve will be scaled to match the length')
    
    args = parser.parse_args()
    if args.cosine_factor == 1.0:
        raise ValueError("Sorry, but b=1.0 causes a discontinuity in the derivative")
    if args.cosine_factor == 0.0:
        raise ValueError("Consider using generate_helix if you just want a circle")
    if args.cosine_factor < 0.0:
        raise ValueError("You can simply mirror the resulting curve and set cosine_factor > 0.0")
    if args.cosine_factor < 1.0:
        raise ValueError("0.0<b<1.0 not implemented yet")
    return args


def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_limacon(args), args.output_name)
            
if __name__ == '__main__':
    main()

