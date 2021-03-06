import argparse
import math

import combine_functions
import marble_path
import slope_function

"""
p173 has some interesting alterations to trig waves


squared wave
------------
this is
x(t) = t + math.sin(t) ** 2
y(t) = 3 math.sin(t)

from 0 to 4pi

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 12 --tube_method deep_oval --tube_wall_height 8 --wall_thickness 3 --tube_radius 12.5  --kinks "(1.5708, 4.7124, 7.8540, 10.9956)" --kink_width 0.8 --kink_slope 2 --kink_sharpness 0.3 --output_name trig.stl

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 12 --tube_method deep_oval --tube_wall_height 8 --wall_thickness 11 --tube_radius 10.3  --kinks "(1.5708, 4.7124, 7.8540, 10.9956)" --kink_width 0.8 --kink_slope 2 --kink_sharpness 0.3 --output_name trig_hole.stl

python generate_trig.py --y_coeff 3 --power 2 --slope_angle 12 --tube_method deep_ellipse --wall_thickness 11 --tube_radius 10.5  --kinks "(1.5708, 4.7124, 7.8540, 10.9956)" --kink_width 0.8 --kink_slope 2 --kink_sharpness 0.3 --output_name trig_post_hole.stl --tube_start_angle 0 --tube_end_angle 360


to get this to work in the corners: copy 3 consecutive times, each 0.3 apart in the y direction.
also, rather than putting it at z=2, put at z=1.8

after putting this together, there is a tiny little notch in each
corner.  you can zoom in between the walls in tinkercad and see that
the bottom floor kind of peels up a bit.  perhaps there is some way to
smooth the normals so the corner isn't this tight, or some way to
patch it from beneath

left post rotates by 63 degrees
right post rotates by 97 degrees


Alternate construction for this shape:
-------------------------------------

python generate_trig.py --y_coeff 4.1 --power 2 --slope_angle 10.35 --tube_method deep_oval --tube_wall_height 6 --kink_replace_circle "((1.0,2.0),(4.14,5.14),(7.28,8.28),(10.42,11.42))" --scale 5.8572 --output_name trig.stl  --tube_end_angle "((4.1,240),(4.9,180))"


Hole:
python generate_trig.py --y_coeff 4.1 --power 2 --slope_angle 10.35 --tube_method deep_ellipse --kink_replace_circle "((1.0,2.0),(4.14,5.14),(7.28,8.28),(10.42,11.42))" --scale 5.8572 --tube_radius 10.5 --wall_thickness 11 --output_name trig_hole.stl  --tube_start_angle 0 --tube_end_angle 360

left post rotates by 77 degrees
right post rotates by 97 degrees

Issue with this formulation: the pleasing sharpness of the corners is a lot less now

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

    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    if args.kink_replace_circle:
        x_t, y_t, r_t = combine_functions.replace_kinks_with_circles(args=args,
                                                                     time_t=time_t,
                                                                     x_t=x_t,
                                                                     y_t=y_t,
                                                                     r_t=r_t,
                                                                     kink_args=args,
                                                                     num_time_steps=args.num_time_steps)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlap_args=None,
                                                  kink_args=args)
        
    z_t = marble_path.arclength_height_function(x_t, y_t, args.num_time_steps,
                                                slope_angle_t=slope_angle_t)

    print("Start x, y, z: %.4f %.4f %.4f" % (x_t(0), y_t(0), z_t(0)))
    print("End x, y, z:   %.4f %.4f %.4f" % (x_t(args.num_time_steps), y_t(args.num_time_steps), z_t(args.num_time_steps)))
    
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              time_t=time_t,
                                              slope_angle_t=slope_angle_t):
        yield triangle    
    

def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for a random trig graph  p173 of Curves.')

    marble_path.add_tube_arguments(parser, default_slope_angle=5.0, default_output_name='trig.stl')
    slope_function.add_kink_args(parser)
    combine_functions.add_kink_circle_args(parser)

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
                        help='How far apart to make the endpoints of the curve.  Note that the curve itself may extend past the endpoints.  Further note that using the circular kink removal will invalidate this argument.')

    parser.add_argument('--scale', default=None, type=float,
                        help='Multiple all samples by this value.  If set to None, will be calculated from the width.')

    args = parser.parse_args(args=sys_args)

    if args.scale is None:
        if args.kink_replace_circle:
            # TODO: this can be compensated for, actually
            print("WARNING: trying to calculate an exact width may be invalidated by using kink replacement.  Consider setting --scale")
        max_t = args.end_t
        min_t = args.start_t
        args.scale = args.width / (max_t - min_t)
        print("Calculated scale to be ", args.scale)
    
    return args
    
    

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_trig(args), args.output_name)
            
if __name__ == '__main__':
    main()

