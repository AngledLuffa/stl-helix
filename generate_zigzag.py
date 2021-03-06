import argparse
import math
import build_shape
import marble_path

"""
The defaults for this script produce the middle portion of a zigzag.

The zigzag produced is suitable for two posts 134mm apart
(the standard width of a two post narble toy)

Angle of the zigs for these defaults: 19.471.  Rotating by this much
makes it easier to assemble.  Then you can put one post at 0,0 and use
the pythagorean theorem to place the other post.  Need to wiggle it
around some so that the out post has the zigzag centered.

Default tube_radius 13.25 so that the rotated tube is still 25mm wide

Minor issue with a basic half circle tube: roughly 5% of marbles would
bounce out of the piece.  Fixed it by adding deeper walls.

python generate_zigzag.py

python generate_zigzag.py --output_name zigzig.hole.stl --tube_method ellipse --tube_end_angle 360 --wall_thickness 11.5 --tube_radius 11.13
"""

def generate_zigzag(args):
    num_time_steps = args.subdivisions_per_zigzag * args.num_zigzags
    y_delta = args.zigzag_length / args.subdivisions_per_zigzag * 2

    def x_t(time_step):
        return time_step * args.zigzag_width / args.subdivisions_per_zigzag

    def y_t(time_step):
        time_step = time_step % args.subdivisions_per_zigzag
        if time_step < args.subdivisions_per_zigzag / 2:
            return time_step * y_delta
        else:
            return args.zigzag_length - (time_step - args.subdivisions_per_zigzag / 2) * y_delta
        
    # overkill - we could easily calculate it ourselves
    z_t = marble_path.arclength_height_function(x_t, y_t, num_time_steps, args.slope_angle)

    def r_t(time_step):
        # west to east is represented by -90, since south to north is 0
        return -90

    build_shape.print_stats(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t, num_time_steps=num_time_steps)
    tangent = math.atan(args.zigzag_length / (args.zigzag_width / 2))
    print("Rotation of the zigzag: %.4f / %.4f degrees" % (tangent, tangent * 180 / math.pi))

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps):
        yield triangle    
    
def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl zigzag.')

    marble_path.add_tube_arguments(parser, default_slope_angle=5.0, default_output_name='zigzag.stl')

    parser.add_argument('--zigzag_length', default=-5, type=float,
                        help='How far a zigzag goes in the y direction.  Negative means go down first')
    parser.add_argument('--zigzag_width', default=30, type=float,
                        help='How far a zigzag goes in the x direction (for both up and down)')
    parser.add_argument('--num_zigzags', default=5, type=int,
                        help='How many zigzags to make')
    parser.add_argument('--subdivisions_per_zigzag', default=40, type=int,
                        help='Subdivisions for each of the zigzags.  Half up and half down')

    # Generally we find that 12.5 works great for the tube - walls of
    # thickness 2 led to the narbles rolling great without taking up
    # too much space.  The default slant of the zigzag means a
    # slightly higher default width is better
    parser.set_defaults(tube_radius=13.25)
    parser.set_defaults(tube_method=marble_path.Tube.OVAL)
    parser.set_defaults(tube_wall_height=6)

    args = parser.parse_args(args=sys_args)
    return args
    
    

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_zigzag(args), args.output_name)
            
if __name__ == '__main__':
    main()
