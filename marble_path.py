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

            
def coordinates(x_t, y_t, z_t, r_t,
                tube_function, tube_subdivision, inside,
                time_t):
    """
    Given the functions describing x, y, z, and r, along with a
    function describing how to build the tube, calculate the current
    location offset by the tube location
    """
    location = (x_t(time_t),
                y_t(time_t),
                z_t(time_t))

    tube_offset = tube_function(tube_subdivision=tube_subdivision,
                                inside=inside,
                                rotation=r_t(time_t))

    location = (location[0] + tube_offset[0],
                location[1] + tube_offset[1],
                location[2] + tube_offset[2])

    return location


def generate_path(x_t, y_t, z_t, r_t,
                  tube_function,
                  num_tube_subdivisions, num_helix_subdivisions,
                  has_inner_wall, full_tube):
    def call_coordinates(tube_subdivision, helix_subdivision, inside):
        return coordinates(x_t=x_t,
                           y_t=y_t,
                           z_t=z_t,
                           r_t=r_t,
                           tube_function=tube_function,
                           tube_subdivision=tube_subdivision,
                           inside=inside,
                           time_t=helix_subdivision)

    
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
    

def add_tube_arguments(parser):
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

                    

def main():
    write_stl(generate_cube(10), 'cube.stl')
            
if __name__ == '__main__':
    main()
