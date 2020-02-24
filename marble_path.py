import math

from enum import Enum

class Tube(Enum):
    ELLIPSE = 1
    OVAL = 2

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

def calculate_arclengths(x_t, y_t, num_time_steps):
    """
    Numerically calculate the arclength at each time step from 0..num_time_steps
    Returns a list of length num_time_steps+1
    """
    arclength = 0.0
    x2 = x_t(0)
    y2 = y_t(0)
    arclengths = [0.0]
    for i in range(0, num_time_steps):
        for j in range(1000):
            t1 = i + j / 1000
            t2 = i + (j + 1) / 1000
        
            x1 = x2
            x2 = x_t(t2)
        
            y1 = y2
            y2 = y_t(t2)

            arclength = arclength + ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        arclengths.append(arclength)
    return arclengths
        
def arclength_slope_function(x_t, y_t, num_time_steps, slope_angle):
    """
    Comes up with a function z(t) which works on the domain [0, num_time_steps]

    Does this by numerically integrating the arclength of x(t), y(t)
    then caching the arclength traveled for the various time steps
    """
    arclengths = calculate_arclengths(x_t, y_t, num_time_steps)
    slope_angle = slope_angle / 180 * math.pi
    zs = [-arc * math.tan(slope_angle) for arc in arclengths]

    def z_t(time_step):
        if time_step < 0 or time_step > num_time_steps:
            raise ValueError("time_step out of domain for z_t")
        # TODO: interpolate time_step?
        return zs[time_step]

    return z_t

def numerical_rotation_function(x_t, y_t, epsilon=0.001):
    """
    Returns a function r(t) which calculates the rotation of a tube based on its x, y functions.
    """
    def r_t(time_step):
        x2 = x_t(time_step + epsilon)
        x1 = x_t(time_step - epsilon)
        dx = (x2 - x1) / (epsilon * 2)

        y2 = y_t(time_step + epsilon)
        y1 = y_t(time_step - epsilon)
        dy = (y2 - y1) / (epsilon * 2)

        if dx == 0 and dy == 0:
            raise ValueError("derivative has a discontinuity at %f" % time_step)
        
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
    return r_t


def slope_tube(vert_disp, slope_angle):
    # tilt the tube a bit so that things going down the ramp
    # are going straight when they come out of the ramp
    y_disp = -vert_disp * math.sin(slope_angle / 180 * math.pi)
    z_disp =  vert_disp * math.cos(slope_angle / 180 * math.pi)
    return (y_disp, z_disp)

def rotate_tube(x_disp, y_disp, z_disp, rotation):
    r_x_disp = (x_disp * math.cos(rotation / 180 * math.pi) -
                y_disp * math.sin(rotation / 180 * math.pi))
    r_y_disp = (x_disp * math.sin(rotation / 180 * math.pi) +
                y_disp * math.cos(rotation / 180 * math.pi))
    return (r_x_disp, r_y_disp, z_disp)
    


def oval_tube_coordinates(tube_radius, wall_height, wall_thickness,
                          num_tube_subdivisions, tube_subdivision,
                          slope_angle, inside, rotation):
    """
    Calculate the x,y,z of an oval tube based on the tube parameters.
    Tube is assumed to be 180 degrees on the bottom of the ramp, with two
      vertical walls to block the marble from flying off into space.
      (See: zigzag v1)
    wall_height is how high up to make the additional walls.
    rotation means how much to rotate the tube.
    """
    if inside:
        tube_radius = tube_radius - wall_thickness
    
    tube_arclength = 2 * wall_height + math.pi * tube_radius
    tube_position = tube_subdivision / num_tube_subdivisions

    if tube_position < wall_height / tube_arclength:
        x_disp = tube_radius
        vert_disp = -wall_height * tube_position
    elif tube_position > (tube_arclength - wall_height) / tube_arclength:
        x_disp = -tube_radius
        tube_position = 1 - tube_position
        vert_disp = -wall_height * tube_position
    else:
        # angle should go from 0..pi
        tube_position = tube_position - wall_height / tube_arclength
        tube_position = tube_position / (1.0 - wall_height * 2 / tube_arclength)
        tube_angle = math.pi * tube_position
        x_disp = tube_radius * math.cos(tube_angle)
        vert_disp = -tube_radius * math.sin(tube_angle) - wall_height

    y_disp, z_disp = slope_tube(vert_disp, slope_angle)
    return rotate_tube(x_disp, y_disp, z_disp, rotation)
    

def ellipse_tube_coordinates(tube_radius, tube_eccentricity, wall_thickness,
                             tube_start_angle, tube_end_angle,
                             num_tube_subdivisions, tube_subdivision,
                             slope_angle, inside, rotation):
    """
    Calculate the x,y,z of an ellipse tube based on the tube parameters.
    Arguments have the same meaning as for generate_helix.
    rotation means how much to rotate the tube.  
      An unrotated tube will be along the x axis.
      For a helix, this probably represents where in the helix you are.
      For a zigzag, you will not want to rotate at all.
      For an arbitrary curve, you probably want to be normal to the current direction.
    """
    # TODO: maybe vary num_tube_subdivisions if the angle is changing?
    tube_angle = tube_start_angle + (tube_end_angle - tube_start_angle) / num_tube_subdivisions * tube_subdivision
    if tube_angle > tube_end_angle:
        tube_angle = tube_end_angle

    tube_angle = tube_angle / 180 * math.pi

    # we will figure out x, y, z as if we had not rotated around the
    # axis at all.  then we will rotate the resulting vector

    # TODO: cache the eccentricity computations or otherwise make them
    # more efficient?
    ellipse_A = 1.0 / (1 - tube_eccentricity ** 2) ** 0.5
    ellipse_r = ellipse_A / (ellipse_A ** 2 * math.cos(tube_angle) ** 2 + math.sin(tube_angle) ** 2) ** 0.5

    if inside:
        # the factor of ellipse_r will go back into the wall_thickness
        # in a moment.  without this, the wall becomes super thick at
        # the bottom of an ellipse
        wall_thickness = wall_thickness / ellipse_r
        tube_radius = tube_radius - wall_thickness

    x_disp = tube_radius * math.cos(tube_angle) * ellipse_r
    vert_disp = -tube_radius * math.sin(tube_angle) * ellipse_r

    y_disp, z_disp = slope_tube(vert_disp, slope_angle)
    return rotate_tube(x_disp, y_disp, z_disp, rotation)

            
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
                                rotation=r_t(time_t),
                                time_t=time_t)

    location = (location[0] + tube_offset[0],
                location[1] + tube_offset[1],
                location[2] + tube_offset[2])

    return location


def generate_path(x_t, y_t, z_t, r_t,
                  tube_args, num_time_steps, slope_angle,
                  tube_angle_t=None):
    """
    tube_args should be args including the tube arguments from below
    tube_angle_t, if it exists, is a function returning (start, end)
      and overrides tube_args.tube_start_angle and tube_end_angle for the ellipse
      TODO: add a flag to ignore that if desired
    """
    if tube_args.wall_thickness >= tube_args.tube_radius:
        has_inner_wall = False
        wall_thickness = tube_args.tube_radius
    else:
        has_inner_wall = True
        wall_thickness = tube_args.wall_thickness

    tube_start_angle = tube_args.tube_start_angle
    tube_end_angle = tube_args.tube_end_angle
    if tube_end_angle < tube_start_angle:
        tube_start_angle, tube_end_angle = tube_end_angle, tube_start_angle

    if tube_args.tube_method is Tube.ELLIPSE:
        if tube_end_angle >= tube_start_angle + 360:
            tube_start_angle = 0
            tube_end_angle = 360
            num_tube_subdivisions = tube_args.tube_sides
            full_tube = True
        else:
            num_tube_subdivisions = math.ceil((tube_end_angle - tube_start_angle) * tube_args.tube_sides / 360)
            full_tube = False
        print("Num tube: {}".format(num_tube_subdivisions))

        if tube_angle_t is None:
            tube_angle_t = lambda x: (tube_start_angle, tube_end_angle)

        def tube_function(tube_subdivision, inside, rotation, time_t):
            """
            Using the parameters given to the helix, create a function which
            returns the x, y, z offset from the tube coordinates.
            This will be an ellipsoid shell
            """
            tube_start_angle, tube_end_angle = tube_angle_t(time_t)
            return ellipse_tube_coordinates(tube_radius=tube_args.tube_radius,
                                            tube_eccentricity=tube_args.tube_eccentricity,
                                            wall_thickness=wall_thickness,
                                            tube_start_angle=tube_start_angle,
                                            tube_end_angle=tube_end_angle,
                                            num_tube_subdivisions=num_tube_subdivisions,
                                            tube_subdivision=tube_subdivision,
                                            slope_angle=slope_angle,
                                            inside=inside,
                                            rotation=rotation)
    elif tube_args.tube_method is Tube.OVAL:
        # if we are using an oval, start_angle, end_angle, and actual
        # subdivisions are all implicitly defined
        num_tube_subdivisions = tube_args.tube_sides
        # ... and we need to print the tube ceiling
        full_tube = False
        
        def tube_function(tube_subdivision, inside, rotation, time_t):
            """
            Create an oval instead.
            """
            return oval_tube_coordinates(tube_radius=tube_args.tube_radius,
                                         wall_height=tube_args.tube_wall_height,
                                         wall_thickness=wall_thickness,
                                         num_tube_subdivisions=tube_args.tube_sides,
                                         tube_subdivision=tube_subdivision,
                                         slope_angle=slope_angle,
                                         inside=inside,
                                         rotation=rotation)

    
    def call_coordinates(tube_subdivision, time_step, inside):
        return coordinates(x_t=x_t,
                           y_t=y_t,
                           z_t=z_t,
                           r_t=r_t,
                           tube_function=tube_function,
                           tube_subdivision=tube_subdivision,
                           inside=inside,
                           time_t=time_step)

    
    for tube_subdivision in range(num_tube_subdivisions):
        for time_step in range(num_time_steps):
            #print("Iterating over tube {} helix {}".format(tube_subdivision, time_step))
            quads = []
            # outside wall
            quads.append((call_coordinates(tube_subdivision, time_step, False),
                          call_coordinates(tube_subdivision+1, time_step, False),
                          call_coordinates(tube_subdivision+1, time_step+1, False),
                          call_coordinates(tube_subdivision, time_step+1, False)))
            # inside wall
            if has_inner_wall:
                quads.append((call_coordinates(tube_subdivision, time_step, True),
                              call_coordinates(tube_subdivision, time_step+1, True),
                              call_coordinates(tube_subdivision+1, time_step+1, True),
                              call_coordinates(tube_subdivision+1, time_step, True)))
            # start tube wall
            if tube_subdivision == 0 and not full_tube:
                quads.append((call_coordinates(tube_subdivision, time_step, False),
                              call_coordinates(tube_subdivision, time_step+1, False),
                              call_coordinates(tube_subdivision, time_step+1, True),
                              call_coordinates(tube_subdivision, time_step, True)))
            # end tube wall
            if tube_subdivision == num_tube_subdivisions-1 and not full_tube:
                quads.append((call_coordinates(tube_subdivision+1, time_step, True),
                              call_coordinates(tube_subdivision+1, time_step+1, True),
                              call_coordinates(tube_subdivision+1, time_step+1, False),
                              call_coordinates(tube_subdivision+1, time_step, False)))
            # start helix wall
            if time_step == 0:
                quads.append((call_coordinates(tube_subdivision, time_step, False),
                              call_coordinates(tube_subdivision, time_step, True),
                              call_coordinates(tube_subdivision+1, time_step, True),
                              call_coordinates(tube_subdivision+1, time_step, False)))
            # end helix wall
            if time_step == num_time_steps-1:
                quads.append((call_coordinates(tube_subdivision, time_step+1, True),
                              call_coordinates(tube_subdivision, time_step+1, False),
                              call_coordinates(tube_subdivision+1, time_step+1, False),
                              call_coordinates(tube_subdivision+1, time_step+1, True)))
            for quad in quads:
                for triangle in generate_quad(*quad):
                    yield triangle

def parse_eccentricity(e):
    e = float(e)
    if e < 0.0 or e >= 1:
        raise ValueError("Eccentricity must be 0 <= e < 1, got %f" % e)
    # TODO: maybe let <0 represent a flatter than expected tube?
    return e

def add_tube_arguments(parser, default_slope_angle=-5.0):
    parser.add_argument('--tube_radius', default=12.5, type=float,
                        help='measurement from the center of ramp to its outer wall')
    parser.add_argument('--wall_thickness', default=2, type=float,
                        help='how thick to make the wall. special case: if wall_thickness >= tube_radius, there is no inner opening')
    parser.add_argument('--tube_start_angle', default=0, type=float,
                        help='angle to the start of the ramp.  0 represents the part furthest from the axis, 180 represents closest to the axis, -90 represents the top of the ramp, 90 represents the bottom.  0..180 represents the bottom of a ramp with no cover.  -90..90 will look like a loop-d-loop')
    parser.add_argument('--tube_end_angle', default=180, type=float,
                        help='angle to the end of the ramp.  same values as tube_start_angle')
    parser.add_argument('--tube_sides', default=64, type=int,
                        help='how many sides a complete tube would have.  tube_start_angle and tube_end_angle are discretized to these subdivisions')
    parser.add_argument('--tube_eccentricity', default=0.0, type=parse_eccentricity,
                        help='How much of an ellipse to make the tube.  0.0 is a circle.  Must be 0 <= e < 1')

    parser.add_argument('--tube_wall_height', default=0.0, type=float,
                        help='If creating an oval tube, how high to make the walls')

    parser.add_argument('--tube_method', default=Tube.ELLIPSE, type=lambda x: Tube[x.upper()],
                        help='How to generate the tube.  ELLIPSE means a circle, or an ellipse if tube_eccentricity is set.  OVAL means 0..180 half circle with vertical walls')

    parser.add_argument('--slope_angle', default=default_slope_angle, type=float,
                        help='Angle to tilt the curve')

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
    write_stl(generate_cube(10), 'cube.stl')
            
if __name__ == '__main__':
    main()
