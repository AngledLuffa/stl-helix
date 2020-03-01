import argparse
import ast
import math

import marble_path

"""
Generates a cycloid of the form (t + sin(4t), 1 - cos(4t))
There is a loop here from .16675 to 1.40405 which must go down >= 23mm
(Also the negative of that obviously needs to happen as well)

To get walls to hopefully stop the marble from jumping:
python generate_cycloid.py --slope_angle 3.0 --tube_method oval --tube_wall_height 6 --overlaps "((.16675,1.40405),(-.16675,-1.40405))"

Note that other arguments can make pretty interesting curves as well

p67 of Practical Handbook of Curve Dewsign and Generation

a possibly interesting variant:
  t - sin 4t, cos 3t
from -5pi/4 to pi/4

the regularization here is because otherwise the graph curves so much in the middle section that there is a kink
the phase change means it can go from -3pi/4 to 3pi/4

python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --width 222 --no_use_sign --y_scale 1.0 --y_phase 1.5708 --sigmoid_regularization 0.4
python generate_cycloid.py --extra_t 0.0 --min_domain -2.3562 --max_domain 2.3562 --x_coeff -1 --y0 0.0 --y_coeff 1.0 --y_t_coeff 3 --width 222 --no_use_sign --y_scale 1.0 --y_phase 1.5708 --sigmoid_regularization 0.4 --tube_radius 10.5 --wall_thickness 11 --tube_start_angle 0 --tube_end_angle 360
"""

def get_drop(arclengths, min_angle, max_angle, start_time_step, end_time_step):
    total_drop = 0.0
    delta_time_step = end_time_step - start_time_step
    for time_step in range(delta_time_step):
        if time_step < delta_time_step * 0.2:
            slope = min_angle + (max_angle - min_angle) * time_step / (delta_time_step * 0.2)
        elif time_step > delta_time_step * 0.8:
            slope = min_angle + (max_angle - min_angle) * (delta_time_step - time_step) / (delta_time_step * 0.2)
        else:
            slope = max_angle
        total_drop = total_drop + (arclengths[time_step + start_time_step + 1] - arclengths[time_step + start_time_step]) * math.tan(slope * math.pi / 180)
    #print("Total drop for angle", max_angle, "is", total_drop)
    return total_drop
    

def get_drop_angle(arclengths, slope_angle, start_time_step, end_time_step, needed_dz):
    total_drop = get_drop(arclengths, slope_angle, slope_angle, start_time_step, end_time_step)
    if total_drop > needed_dz:
        return

    total_drop = get_drop(arclengths, slope_angle, 45, start_time_step, end_time_step)
    if total_drop < needed_dz:
        raise ValueError("Even an angle of 45 is not sufficient to achieve this drop")

    min_angle = slope_angle
    max_angle = 45
    while max_angle - min_angle > 0.01:
        test_angle = (max_angle + min_angle) / 2
        total_drop = get_drop(arclengths, slope_angle, test_angle, start_time_step, end_time_step)
        if total_drop < needed_dz:
            min_angle = test_angle
        else:
            max_angle = test_angle
    return (max_angle + min_angle) / 2.0    

def get_time_step(times, t):
    # TODO: implement binary search?
    if times[0] > t:
        return 0
    if times[-1] < t:
        return len(times) - 1
    for i in range(len(times)):
        if times[i] <= t and times[i+1] > t:
            return i
    raise AssertionError("Oops")

def update_slopes(slopes, arclengths, times, slope_angle, start_t, end_t, needed_dz):
    start_time_step = get_time_step(times, start_t)
    end_time_step = get_time_step(times, end_t)
    if end_time_step < start_time_step:
        end_time_step, start_time_step = start_time_step, end_time_step

    best_angle = get_drop_angle(arclengths, slope_angle, start_time_step, end_time_step, needed_dz)

    delta_time_step = end_time_step - start_time_step
    for time_step in range(delta_time_step+1):
        if time_step < delta_time_step * 0.2:
            new_slope = slope_angle + (best_angle - slope_angle) * time_step / (delta_time_step * 0.2)
        elif time_step > delta_time_step * 0.8:
            new_slope = slope_angle + (best_angle - slope_angle) * (delta_time_step - time_step) / (delta_time_step * 0.2)
        else:
            new_slope = best_angle
        slopes[time_step+start_time_step] = max(new_slope, slopes[time_step+start_time_step])

def generate_cycloid(args):
    min_t = args.min_domain - args.extra_t
    max_t = args.max_domain + args.extra_t
    def time_t(time_step):
        return min_t + (max_t - min_t) * time_step / args.num_time_steps

    scale = args.width / (max_t - min_t)

    def x_t(time_step):
        t = time_t(time_step)
        if t < args.min_domain or t > args.max_domain:
            return t * scale
        reg = (1.0 - args.sigmoid_regularization) + args.sigmoid_regularization * math.exp(4 * t ** 2) / (1.0 + math.exp(4 * t ** 2))
        return (t + reg * args.x_coeff * math.sin(args.x_t_coeff * t)) * scale

    def y_t(time_step):
        t = time_t(time_step)
        if t < args.min_domain:
            t = args.min_domain
        elif t > args.max_domain:
            t = args.max_domain
        if t < 0 and args.use_sign:
            sign = -1
        else:
            sign = 1
        return ((sign * (args.y0 + args.y_coeff * math.cos(args.y_t_coeff * t + args.y_phase))) *
                scale * args.y_scale)

    arclengths = marble_path.calculate_arclengths(x_t, y_t, args.num_time_steps)
    times = [time_t(t) for t in range(args.num_time_steps+1)]
    slopes = [args.slope_angle for t in range(args.num_time_steps+1)]
    if args.overlaps:
        for start_t, end_t in args.overlaps:
            # for the basic 2 loop cycloid, want +/- .16675, 1.40405
            update_slopes(slopes, arclengths, times, args.slope_angle, start_t, end_t, 25)

    slope_angle_t = lambda time_step_t: slopes[time_step_t]
    
    z_t = marble_path.arclength_slope_function(x_t, y_t, args.num_time_steps,
                                               slope_angle_t=slope_angle_t)
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    #for i in range(args.num_time_steps+1):
    #    print("%.4f %.4f %.4f %.4f" % (time_t(i), x_t(i), y_t(i), z_t(i)))
    
    x0 = x_t(0)
    y0 = y_t(0)
    z0 = z_t(0)
    x1 = x_t(args.num_time_steps)
    y1 = y_t(args.num_time_steps)
    z1 = z_t(args.num_time_steps)
    
    print("X,Y,Z of start:   %.4f %.4f %.4f" % (x0, y0, z0))
    print("X,Y,Z of end:     %.4f %.4f %.4f" % (x1, y1, z1))
    print("dx, dy, dz:       %.4f %.4f %.4f" % ((x1 - x0), (y1 - y0), (z1 - z0)))
    print("Corner to corner: %.4f" % ((y1 - y0) ** 2 + (x1 - x0) ** 2) ** 0.5)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle    

def parse_overlaps(overlap_str):
    overlap_tuple = ast.literal_eval(overlap_str)
    for i in overlap_tuple:
        if len(i) != 2:
            raise ValueError('Overlaps need to be a tuple of tuples')
    return overlap_tuple
        
def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl cycloid.')

    marble_path.add_tube_arguments(parser, default_slope_angle=8.0)

    parser.add_argument('--domain', default=None, type=float,
                        help='If set, the domain will be -domain..domain')
    parser.add_argument('--min_domain', default=None, type=float,
                        help='t0 in the domain [t0, t1]')
    parser.add_argument('--max_domain', default=None, type=float,
                        help='t1 in the domain [t0, t1].  If left None, will be derived from the coefficients')

    parser.add_argument('--x_coeff', default=1, type=float,
                      help='Coefficient A of x=t+A sin(Bt)')
    parser.add_argument('--x_t_coeff', default=4, type=int,
                      help='Coefficient B of x=t+A sin(Bt)')
    parser.add_argument('--y0', default=1, type=float,
                        help='Coefficient y0 of y = y0 + C cos(Dt)')
    parser.add_argument('--y_coeff', default=-1, type=float,
                        help='Coefficient C of y(t) = y0 + C cos(Dt)')
    parser.add_argument('--y_t_coeff', default=4, type=int,
                      help='Coefficient D of y(t) = y0 + C cos(Dt)')

    parser.add_argument('--use_sign', dest='use_sign',
                        default=True, action='store_true',
                        help='multiply y by sign(t)')
    parser.add_argument('--no_use_sign', dest='use_sign',
                        action='store_false',
                        help="Don't multiply y by sign(t)")
    
    
    parser.add_argument('--num_time_steps', default=400, type=int,
                      help='Number of time steps to model')

    parser.add_argument('--extra_t', default=0.5, type=float,
                        help='Extra time to build the model as a straight line before & after the domain')

    parser.add_argument('--width', default=134.0, type=float,
                        help='How far apart to make the endpoints of the curve.  Note that the curve itself may extend past the endpoints')
    parser.add_argument('--y_scale', default=0.8, type=float,
                        help='Make the model a little squished or stretched vertically')
    parser.add_argument('--y_phase', default=0.0, type=float,
                        help='Adjust the phase of y(t) = y0 + C cos(Dt + phase)')

    parser.add_argument('--sigmoid_regularization', default=0.0, type=float,
                        help='How much to use regularization around x=0.  Idea is to make squiggle with loops not have sharp corners')

    parser.add_argument('--overlaps', default=None, type=parse_overlaps,
                        help='Tuple of (start, end) pairs which represents the time periods where overlaps occur.  Angle will be changed to enforce a large enough drop there.')

    # TODO: refactor the output_name
    parser.add_argument('--output_name', default='cycloid.stl',
                        help='Where to put the stl')

    args = parser.parse_args()

    if args.domain is not None:
        args.min_domain = -args.domain
        args.max_domain = args.domain

    if args.min_domain is None or args.max_domain is None:
        width = math.pi * 4 / math.gcd(args.x_t_coeff, args.y_t_coeff)
        if args.min_domain is None and args.max_domain is None:
            args.min_domain = -width / 2
            args.max_domain =  width / 2
        elif args.min_domain is None:
            args.min_domain = args.max_domain - width
        else:
            args.max_domain = args.min_domain + width
            
    return args
    

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_cycloid(args), args.output_name)

if __name__ == '__main__':
    main()

