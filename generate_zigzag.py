import argparse
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
    z_t = marble_path.arclength_slope_function(x_t, y_t, num_time_steps, args.slope_angle)

    def r_t(time_step):
        return 90

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps,
                                              slope_angle=args.slope_angle):
        yield triangle    
    
def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for an stl zigzag.')

    marble_path.add_tube_arguments(parser, default_slope_angle=5.0)

    parser.add_argument('--zigzag_length', default=-5, type=float,
                        help='How far a zigzag goes in the y direction.  Negative means go down first')
    parser.add_argument('--zigzag_width', default=30, type=float,
                        help='How far a zigzag goes in the x direction (for both up and down)')
    parser.add_argument('--num_zigzags', default=5, type=int,
                        help='How many zigzags to make')
    parser.add_argument('--subdivisions_per_zigzag', default=40, type=int,
                        help='Subdivisions for each of the zigzags.  Half up and half down')

    parser.add_argument('--output_name', default='zigzag.stl',
                        help='Where to put the stl')

    # Generally we find that 12.5 works great for the tube - walls of
    # thickness 2 led to the narbles rolling great without taking up
    # too much space.  The default slant of the zigzag means a
    # slightly higher default width is better
    parser.set_defaults(tube_radius=13.25)
    parser.set_defaults(tube_method=marble_path.Tube.OVAL)
    parser.set_defaults(tube_wall_height=6)

    args = parser.parse_args()
    return args
    
    

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_zigzag(args), args.output_name)
            
if __name__ == '__main__':
    main()
