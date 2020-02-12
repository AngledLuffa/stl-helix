import argparse
import math
import marble_path

def calculate_slope_angle(helix_radius, vertical_displacement):
    """
    tube_radius is adjacent, vertical_displacement is opposite
    returns asin in degrees
    this is the slope of the ramp
    """
    helix_distance = helix_radius * math.pi * 2
    slope_distance = (helix_distance ** 2 + vertical_displacement ** 2) ** 0.5
    # currently in radians
    slope_angle = math.asin(vertical_displacement / slope_distance)
    return slope_angle / math.pi * 180


def generate_helix(args):
    """
    helix_radius is the measurement from the axis to the center of any part of the ramp
    tube_radius is the measurement from the center of ramp to its outer wall
    wall_thickness is how thick to make the wall
      special case: if wall_thickness >= tube_radius, there is no inner opening
    tube_start_angle and tube_end_angle represent which part of the ramp to draw.
      0 represents the part furthest from the axis
      180 represents the part closest to the axis
      0..180 covers the bottom of the arc.  for the top, for example, do 180..0
      special case: if 0..360 or any rotation of that is supplied, the entire circle is drawn
    tube_sides is how many sides a complete tube would have.
      tube_start_angle and tube_end_angle are discretized to these subdivisions
    helix_sides is how many sides a complete helix rotation has
    vertical_displacement is how far to move up in one complete rotation
      tube_radius*2 means the next layer will be barely touching the previous layer
    rotations is how far around to go.  will be discretized using helix_sides
    """
    # slope_angle is the angle of the slope as it goes up the spiral
    # faces will be tilted this much to allow better connections with
    # the next piece
    slope_angle = calculate_slope_angle(args.helix_radius,
                                        args.vertical_displacement)
    print("Slope angle:", slope_angle)
    
    num_helix_subdivisions = math.ceil(args.rotations * args.helix_sides)
    print("Num helix: {}".format(num_helix_subdivisions))
    if num_helix_subdivisions <= 0:
        raise ValueError("Must complete some positive fraction of a rotation")

    def x_t(helix_subdivision):
        helix_angle = 360 / args.helix_sides * helix_subdivision
        r_x_disp = args.helix_radius * math.cos(helix_angle / 180 * math.pi)
        # helix_radius + tube_radius so that everything is positive
        return args.helix_radius + args.tube_radius + r_x_disp
    
    def y_t(helix_subdivision):
        helix_angle = 360 / args.helix_sides * helix_subdivision
        r_y_disp = args.helix_radius * math.sin(helix_angle / 180 * math.pi)
        # helix_radius + tube_radius so that everything is positive
        return args.helix_radius + args.tube_radius + r_y_disp

    def z_t(helix_subdivision):
        # tube_radius included again to keep everything positive
        # TODO: need to look for negative slope and possibly increase
        # all values by the maximum negative displacement
        return args.tube_radius + math.sin(slope_angle / 180 * math.pi) * 2 * math.pi * args.helix_radius * helix_subdivision / args.helix_sides

    def r_t(helix_subdivision):
        helix_angle = 360 / args.helix_sides * helix_subdivision
        return helix_angle
    
    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_helix_subdivisions,
                                              slope_angle=slope_angle):
        yield triangle

    
def parse_args():
    # TODO: add an argument which does the math for rotations if you give it the angle of helix you want, for example
    #   add an argument for the slope of the ramp instead of vertical_displacement
    parser = argparse.ArgumentParser(description='Arguments for an stl helix.')

    marble_path.add_tube_arguments(parser)
    
    parser.add_argument('--helix_radius', default=19, type=float,
                        help='measurement from the axis to the center of any part of the ramp')    
    parser.add_argument('--helix_sides', default=64, type=int,
                        help='how many sides it takes to go around the axis once')
    parser.add_argument('--vertical_displacement', default=25, type=float,
                        help='how far to move up in one complete rotation.  tube_radius*2 means the next layer will be barely touching the previous layer')
    parser.add_argument('--rotations', default=1, type=float,
                        help='rotations is how far around to go.  will be discretized using helix_sides')

    parser.add_argument('--output_name', default='foo.stl',
                        help='Where to put the stl')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    marble_path.print_args(args)

    marble_path.write_stl(generate_helix(args), args.output_name)

            
if __name__ == '__main__':
    main()
