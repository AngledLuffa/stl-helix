import argparse
import math

def generate_quad(a, b, c, d):
    """
    Given four points of a quadrilateral in clockwise order, yields
    two triangles in clockwise order
    """
    yield((a, b, d))
    yield((b, c, d))

def generate_cube(size):
    """
    Generates the facets for a cube of the given size.
    Mostly for debugging the stl writing.
    """
    sides = [((0, 0, 0), (size, 0, 0), (size, 0, size), (0, 0, size)),  # front
             ((size, 0, 0), (size, size, 0), (size, size, size), (size, 0, size)), # right side
             ((0, 0, 0), (0, 0, size), (0, size, size), (0, size, 0)), # left side
             ((0, 0, 0), (0, size, 0), (size, size, 0), (size, 0, 0)), # bottom
             ((0, 0, size), (size, 0, size), (size, size, size), (0, size, size)), # top
             ((0, size, 0), (0, size, size), (size, size, size), (size, size, 0))  # back
             ]
    for side in sides:
        for triangle in generate_quad(*side):
            yield triangle

def tube_coordinates(tube_radius, wall_thickness,
                     start_angle, end_angle, tube_sides,
                     tube_subdivision, slope_angle, inside, rotation):
    """
    Calculate the x,y,z based on the tube position.
    Arguments have the same meaning as for generate_helix.
    rotation means how much to rotate the tube.  
      An unrotated tube will be along the x axis.
      For a helix, this probably represents where in the helix you are.
      For a zigzag, you will not want to rotate at all.
      For an arbitrary curve, you probably want to be normal to the current direction.
    """
    tube_angle = start_angle + 360 / tube_sides * tube_subdivision
    if tube_angle > end_angle:
        tube_angle = end_angle

    if inside:
        tube_radius = tube_radius - wall_thickness

    # we will figure out x, y, z as if we had not rotated around the
    # axis at all.  then we will rotate the resulting vector
    x_disp = tube_radius * math.cos(tube_angle / 180 * math.pi)
    vert_disp = -tube_radius * math.sin(tube_angle / 180 * math.pi)
    # tilt the tube a bit so that things going down the ramp
    # are going straight when they come out of the ramp
    y_disp = -vert_disp * math.sin(slope_angle / 180 * math.pi)
    z_disp =  vert_disp * math.cos(slope_angle / 180 * math.pi)

    r_x_disp = (x_disp * math.cos(rotation / 180 * math.pi) -
                y_disp * math.sin(rotation / 180 * math.pi))
    r_y_disp = (x_disp * math.sin(rotation / 180 * math.pi) +
                y_disp * math.cos(rotation / 180 * math.pi))

    return (r_x_disp, r_y_disp, z_disp)

            
def coordinates(helix_radius, tube_radius, wall_thickness,
                start_angle, end_angle,
                tube_sides, helix_sides,
                vertical_displacement,
                tube_subdivision, helix_subdivision,
                slope_angle, inside):
    #print("GENERATING: {} {} {} {} {} {} {} {} {} {} {} {}".format(
    #    helix_radius, tube_radius, wall_thickness,
    #    start_angle, end_angle,
    #    tube_sides, helix_sides,
    #    vertical_displacement,
    #    tube_subdivision, helix_subdivision,
    #    slope_angle, inside))
    
    # to make the math easy, we start from 0, 0, do some rotations,
    # and then translate by center so it is all positive
    center = helix_radius + tube_radius
    
    # we do the initial calculations with the axis pointing up
    # at (0, 0)
    location = (0, 0, # move up by the location in the helix
                tube_radius +
                vertical_displacement * helix_subdivision / helix_sides)
    helix_angle = 360 / helix_sides * helix_subdivision

    #print("    ", x_disp, vert_disp, y_disp, z_disp)
    #print("    ", helix_angle / 180 * math.pi)
    r_x_disp = helix_radius * math.cos(helix_angle / 180 * math.pi)
    r_y_disp = helix_radius * math.sin(helix_angle / 180 * math.pi)
    #print("    ", r_x_disp, r_y_disp)

    location = (location[0] + r_x_disp,
                location[1] + r_y_disp,
                location[2])

    tube_offset = tube_coordinates(tube_radius=tube_radius,
                                   wall_thickness=wall_thickness,
                                   start_angle=start_angle,
                                   end_angle=end_angle,
                                   tube_sides=tube_sides,
                                   tube_subdivision=tube_subdivision,
                                   slope_angle=slope_angle,
                                   inside=inside,
                                   rotation=helix_angle)

    location = (location[0] + tube_offset[0],
                location[1] + tube_offset[1],
                location[2] + tube_offset[2])

    #print("    ", location)
    
    # adjust the center to be positive so there are no
    # negative numbers
    location = (location[0] + center,
                location[1] + center,
                location[2])
    
    #print("    ", location)

    return location

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
    start_angle and end_angle represent which part of the ramp to draw.
      0 represents the part furthest from the axis
      180 represents the part closest to the axis
      0..180 covers the bottom of the arc.  for the top, for example, do 180..0
      special case: if 0..360 or any rotation of that is supplied, the entire circle is drawn
    tube_sides is how many sides a complete tube would have.
      start_angle and end_angle are discretized to these subdivisions
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
    
    if args.wall_thickness >= args.tube_radius:
        has_inner_wall = False
        wall_thickness = args.tube_radius
    else:
        has_inner_wall = True
        wall_thickness = args.wall_thickness

    start_angle = args.start_angle
    end_angle = args.end_angle
    if end_angle < start_angle:
        start_angle, end_angle = end_angle, start_angle

    if end_angle >= start_angle + 360:
        start_angle = 0
        end_angle = 360
        num_tube_subdivisions = args.tube_sides
        full_tube = True
    else:
        num_tube_subdivisions = math.ceil((end_angle - start_angle) * args.tube_sides / 360)
        full_tube = False
    print("Num tube: {}".format(num_tube_subdivisions))

    num_helix_subdivisions = math.ceil(args.rotations * args.helix_sides)
    print("Num helix: {}".format(num_helix_subdivisions))
    if num_helix_subdivisions <= 0:
        raise ValueError("Must complete some positive fraction of a rotation")

    def call_coordinates(tube_subdivision, helix_subdivision, inside):
        return coordinates(helix_radius=args.helix_radius,
                           tube_radius=args.tube_radius,
                           wall_thickness=wall_thickness,
                           start_angle=start_angle,
                           end_angle=end_angle,
                           tube_sides=args.tube_sides,
                           helix_sides=args.helix_sides,
                           vertical_displacement=args.vertical_displacement,
                           tube_subdivision=tube_subdivision,
                           helix_subdivision=helix_subdivision,
                           slope_angle=slope_angle,
                           inside=inside)
    

    for tube_subdivision in range(num_tube_subdivisions):
        for helix_subdivision in range(num_helix_subdivisions):
            #print("Iterating over tube {} helix {}".format(tube_subdivision, helix_subdivision))
            quads = []
            # outside wall
            quads.append((call_coordinates(tube_subdivision, helix_subdivision, False),
                          call_coordinates(tube_subdivision+1, helix_subdivision, False),
                          call_coordinates(tube_subdivision+1, helix_subdivision+1, False),
                          call_coordinates(tube_subdivision, helix_subdivision+1, False)))
            # inside wall
            if has_inner_wall:
                quads.append((call_coordinates(tube_subdivision, helix_subdivision, True),
                              call_coordinates(tube_subdivision, helix_subdivision+1, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision+1, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision, True)))
            # start tube wall
            if tube_subdivision == 0 and not full_tube:
                quads.append((call_coordinates(tube_subdivision, helix_subdivision, False),
                              call_coordinates(tube_subdivision, helix_subdivision+1, False),
                              call_coordinates(tube_subdivision, helix_subdivision+1, True),
                              call_coordinates(tube_subdivision, helix_subdivision, True)))
            # end tube wall
            if tube_subdivision == num_tube_subdivisions-1 and not full_tube:
                quads.append((call_coordinates(tube_subdivision+1, helix_subdivision, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision+1, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision+1, False),
                              call_coordinates(tube_subdivision+1, helix_subdivision, False)))
            # start helix wall
            if helix_subdivision == 0:
                quads.append((call_coordinates(tube_subdivision, helix_subdivision, False),
                              call_coordinates(tube_subdivision, helix_subdivision, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision, True),
                              call_coordinates(tube_subdivision+1, helix_subdivision, False)))
            # end helix wall
            if helix_subdivision == num_helix_subdivisions-1:
                quads.append((call_coordinates(tube_subdivision, helix_subdivision+1, True),
                              call_coordinates(tube_subdivision, helix_subdivision+1, False),
                              call_coordinates(tube_subdivision+1, helix_subdivision+1, False),
                              call_coordinates(tube_subdivision+1, helix_subdivision+1, True)))
            for quad in quads:
                for triangle in generate_quad(*quad):
                    yield triangle
    
def write_stl(triangles, filename):
    """
    Given a list of triangles, writes each facet to the given filename
    """
    with open(filename, "w") as fout:
        for triangle in triangles:
            # facet normal of 0 0 0 is often used as a convention - processing program can figure it out
            fout.write("facet normal 0 0 0\n")
            fout.write("    outer loop\n")
            for vertex in triangle:
                fout.write("        vertex %f %f %f\n" % vertex)
            fout.write("    endloop\n")
            fout.write("endfacet\n")

def parse_args():
    # TODO: add an argument which does the math for rotations if you give it the angle of helix you want, for example
    #   add an argument for the slope of the ramp instead of vertical_displacement
    parser = argparse.ArgumentParser(description='Arguments for an stl helix.')
    parser.add_argument('--helix_radius', default=19, type=float,
                        help='measurement from the axis to the center of any part of the ramp')
    parser.add_argument('--tube_radius', default=12.5, type=float,
                        help='measurement from the center of ramp to its outer wall')
    parser.add_argument('--wall_thickness', default=2, type=float,
                        help='how thick to make the wall. special case: if wall_thickness >= tube_radius, there is no inner opening')
    parser.add_argument('--start_angle', default=0, type=float,
                        help='angle to the start of the ramp.  0 represents the part furthest from the axis, 180 represents closest to the axis, -90 represents the top of the ramp, 90 represents the bottom.  0..180 represents the bottom of a ramp with no cover.  -90..90 will look like a loop-d-loop')
    parser.add_argument('--end_angle', default=180, type=float,
                        help='angle to the end of the ramp.  same values as start_angle')
    parser.add_argument('--tube_sides', default=64, type=int,
                        help='how many sides a complete tube would have.  start_angle and end_angle are discretized to these subdivisions')
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

def print_args(args):
    """
    For record keeping purposes, print out the arguments
    """
    args = vars(args)
    keys = sorted(args.keys())
    print('ARGS:')
    for k in keys:
        print('%s: %s' % (k, args[k]))

def main():
    args = parse_args()
    print_args(args)

    write_stl(generate_helix(args), args.output_name)
    #write_stl(generate_cube(10), 'cube.stl')

            
if __name__ == '__main__':
    main()
