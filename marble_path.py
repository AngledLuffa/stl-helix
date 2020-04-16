import math

from enum import Enum

import marble_util

class Tube(Enum):
    ELLIPSE = 1
    OVAL = 2
    DEEP_ELLIPSE = 3
    DEEP_OVAL = 4

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
        
def arclength_height_function(x_t, y_t, num_time_steps,
                              slope_angle=None,
                              slope_angle_t=None):
    """
    Comes up with a function z(t) which works on the domain [0, num_time_steps]

    Does this by numerically integrating the arclength of x(t), y(t)
    then caching the arclength traveled for the various time steps
    """
    arclengths = calculate_arclengths(x_t, y_t, num_time_steps)
    if slope_angle is not None:
        angle = slope_angle / 180 * math.pi
    zs = [0.0]
    for t, (arc1, arc2) in enumerate(zip(arclengths[:-1], arclengths[1:])):
        if slope_angle_t is not None:
            angle = slope_angle_t(t) / 180 * math.pi
        delta_arc = arc1 - arc2   # flipping the negative: positive angle means down
        delta_z = math.tan(angle) * delta_arc
        zs.append(delta_z + zs[-1])

    def z_t(time_step):
        if time_step < 0 or time_step > num_time_steps:
            raise ValueError("time_step out of domain for z_t")
        # TODO: interpolate time_step?
        return zs[time_step]

    #for i, s in enumerate(zs):
    #    print(i, s)
    
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
        if dx >= 0 and dy > 0:
            # this gives us a negative rotation, meaning to the right
            rotation = -rotation
        elif dx >= 0 and dy < 0:
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
    y_disp = vert_disp * math.sin(slope_angle / 180 * math.pi)
    z_disp = vert_disp * math.cos(slope_angle / 180 * math.pi)
    return (y_disp, z_disp)

def rotate_tube(x_disp, y_disp, z_disp, rotation):
    r_x_disp = (x_disp * math.cos(rotation / 180 * math.pi) -
                y_disp * math.sin(rotation / 180 * math.pi))
    r_y_disp = (x_disp * math.sin(rotation / 180 * math.pi) +
                y_disp * math.cos(rotation / 180 * math.pi))
    return (r_x_disp, r_y_disp, z_disp)
    

def deep_trig(base):
    p_base = abs(base) ** 0.5
    if base < 0.0: p_base = -p_base
    base = (p_base + base) / 2
    return base
    

def oval_tube_coordinates(tube_method, tube_radius, wall_height, wall_thickness,
                          tube_start_angle, tube_end_angle,
                          num_tube_subdivisions, tube_subdivision,
                          slope_angle, inside, rotation):
    """
    Calculate the x,y,z of an oval tube based on the tube parameters.
    Tube is assumed to be 180 degrees on the bottom of the ramp, with two
      vertical walls to block the marble from flying off into space.
      (See: zigzag v1)
    wall_height is how high up to make the additional walls.
    rotation means how much to rotate the tube.
    tube_method is passed in because this can work for both OVAL and DEEP_OVAL
    """
    if inside:
        tube_radius = tube_radius - wall_thickness

    if tube_start_angle != 0:
        raise ValueError("Currently tube_start_angle != 0 is not handled for oval")
    if tube_end_angle > 360:
        tube_end_angle = 360
    if tube_end_angle < 180:
        raise ValueError("Currently tube_end_angle < 180 is not handled for oval")

    tube_arclength = 2 * wall_height + (tube_end_angle - tube_start_angle) * math.pi / 180 * tube_radius
    tube_position = tube_subdivision / num_tube_subdivisions

    bottom_arclength = 2 * wall_height + math.pi * tube_radius
    overhang_arclength = tube_arclength - bottom_arclength
    overhang_ratio = overhang_arclength / tube_arclength
    if tube_position > bottom_arclength / tube_arclength:
        tube_position = tube_position - bottom_arclength / tube_arclength
        # tube_position is now 0 .. overhang_ratio
        tube_position = tube_position / overhang_ratio
        tube_angle = math.pi - (tube_end_angle - 180) * tube_position * math.pi / 180

        cos = math.cos(tube_angle) if tube_method is Tube.OVAL else deep_trig(math.cos(tube_angle))
        sin = math.sin(tube_angle) if tube_method is Tube.OVAL else deep_trig(math.sin(tube_angle))
        x_disp = tube_radius * cos
        vert_disp = tube_radius * sin
        y_disp, z_disp = slope_tube(vert_disp, slope_angle)
        return rotate_tube(x_disp, y_disp, z_disp, rotation)
    else:
        tube_arclength = tube_arclength - overhang_arclength
        tube_position = tube_position / (1.0 - overhang_ratio)

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
        if wall_height * 2 / tube_arclength < 1.0:
            tube_position = tube_position / (1.0 - wall_height * 2 / tube_arclength)
        tube_angle = math.pi * tube_position
        cos = math.cos(tube_angle) if tube_method is Tube.OVAL else deep_trig(math.cos(tube_angle))
        sin = math.sin(tube_angle) if tube_method is Tube.OVAL else deep_trig(math.sin(tube_angle))
        x_disp = tube_radius * cos
        vert_disp = -tube_radius * sin - wall_height

    y_disp, z_disp = slope_tube(vert_disp, slope_angle)
    return rotate_tube(x_disp, y_disp, z_disp, rotation)
    

def ellipse_tube_coordinates(tube_method, tube_radius, tube_eccentricity, wall_thickness,
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

    cos = math.cos(tube_angle) if tube_method is Tube.ELLIPSE else deep_trig(math.cos(tube_angle))
    sin = math.sin(tube_angle) if tube_method is Tube.ELLIPSE else deep_trig(math.sin(tube_angle))

    x_disp = tube_radius * cos * ellipse_r
    vert_disp = -tube_radius * sin * ellipse_r

    y_disp, z_disp = slope_tube(vert_disp, slope_angle)
    return rotate_tube(x_disp, y_disp, z_disp, rotation)

            
def coordinates(x_t, y_t, z_t, r_t,
                tube_function, tube_subdivision, inside,
                time_step):
    """
    Given the functions describing x, y, z, and r, along with a
    function describing how to build the tube, calculate the current
    location offset by the tube location
    """
    location = (x_t(time_step),
                y_t(time_step),
                z_t(time_step))

    tube_offset = tube_function(tube_subdivision=tube_subdivision,
                                inside=inside,
                                rotation=r_t(time_step),
                                time_step=time_step)

    #print("%.4f %d    %.4f %.4f %.4f   %.4f %.4f %.4f" %
    #      (time_step, tube_subdivision, location[0], location[1], location[2],
    #       tube_offset[0], tube_offset[1], tube_offset[2]))

    location = (location[0] + tube_offset[0],
                location[1] + tube_offset[1],
                location[2] + tube_offset[2])

    return location


def build_tube_angle_t(tube_angles, time_t):
    """Build a function from time to tube angle

    Expects time to either be a single number, or a sequence of tuples: (time, angle)

    Given a sequence of tuples, times before the start will get
    angle0, times after the end will get angleN, and times between two
    times will be interpolated between the two using a tanh for smoothness
    """
    if isinstance(tube_angles, (float, int)):
        tube_t = lambda t: tube_angles
    else:
        def tube_t(time_step):
            t = time_t(time_step)
            if t < tube_angles[0][0]:
                # before the first interval: return that angle
                return tube_angles[0][1]
            if t > tube_angles[-1][0]:
                # after the last interval: return that angle
                return tube_angles[-1][1]
            for i in tube_angles:
                # exactly on a interval boundary: return that angle
                if t == i[0]:
                    return i[1]
            # at this point, we are between two intervals.  figure out which one
            for i, interval in enumerate(tube_angles):
                if t < interval[0]:
                    break
            prev = tube_angles[i - 1]
            ratio = (t - prev[0]) / (interval[0] - prev[0])
            # use math.tanh so that we have a smooth transition rather than a corner
            return prev[1] + (math.tanh((ratio * 8) - 4) + 1.0) / 2.0 * (interval[1] - prev[1])
    return tube_t

def compose_triangles(x_t, y_t, z_t, r_t,
                      tube_args, num_time_steps,
                      time_t=None,
                      slope_angle_t=None):
    """
    Returns a list of vertices and triangles connecting those vertices.

    tube_args should be args including the tube arguments from below

    time_t, if present, converts time_step to some other range,
      usually represented by start_t or end_t

    slope_angle_t is a function returning the angle up/down of the path.
      if None, args.slope_angle is used instead
    """
    if tube_args.wall_thickness >= tube_args.tube_radius:
        has_inner_wall = False
        wall_thickness = tube_args.tube_radius
    else:
        has_inner_wall = True
        wall_thickness = tube_args.wall_thickness

    if slope_angle_t is None:
        slope_angle_t = lambda x: tube_args.slope_angle

    if time_t is None:
        time_t = lambda t: t

    tube_start_t = build_tube_angle_t(tube_args.tube_start_angle, time_t)
    tube_end_t = build_tube_angle_t(tube_args.tube_end_angle, time_t)

    #for i in range(0, num_time_steps+1):
    #    print("  %d %.4f %.4f" % (i, tube_start_t(i), tube_end_t(i)))

    def full_tube_t(first_step, second_step):
        if tube_end_t(first_step) < tube_start_t(first_step) + 360:
            return False
        if tube_end_t(second_step) < tube_start_t(second_step) + 360:
            return False
        return True
        
    if tube_args.tube_method is Tube.ELLIPSE or tube_args.tube_method is Tube.DEEP_ELLIPSE:
        num_tube_subdivisions = max(math.ceil((tube_end_t(t) - tube_start_t(t)) * tube_args.tube_sides / 360)
                                    for t in range(num_time_steps+1))
        num_tube_subdivisions = min(num_tube_subdivisions, tube_args.tube_sides)
        print("Num tube: {}".format(num_tube_subdivisions))
        def tube_function(tube_subdivision, inside, rotation, time_step):
            """
            Using the parameters given to the helix, create a function which
            returns the x, y, z offset from the tube coordinates.
            This will be an ellipsoid shell
            """
            return ellipse_tube_coordinates(tube_method=tube_args.tube_method,
                                            tube_radius=tube_args.tube_radius,
                                            tube_eccentricity=tube_args.tube_eccentricity,
                                            wall_thickness=wall_thickness,
                                            tube_start_angle=tube_start_t(time_step),
                                            tube_end_angle=tube_end_t(time_step),
                                            num_tube_subdivisions=num_tube_subdivisions,
                                            tube_subdivision=tube_subdivision,
                                            slope_angle=slope_angle_t(time_step),
                                            inside=inside,
                                            rotation=rotation)
    elif tube_args.tube_method is Tube.OVAL or tube_args.tube_method is Tube.DEEP_OVAL:
        num_tube_subdivisions = tube_args.tube_sides
        def tube_function(tube_subdivision, inside, rotation, time_step):
            """
            Create an oval instead.
            """
            return oval_tube_coordinates(tube_method=tube_args.tube_method,
                                         tube_radius=tube_args.tube_radius,
                                         wall_height=tube_args.tube_wall_height,
                                         wall_thickness=wall_thickness,
                                         tube_start_angle=tube_start_t(time_step),
                                         tube_end_angle=tube_end_t(time_step),
                                         num_tube_subdivisions=tube_args.tube_sides,
                                         tube_subdivision=tube_subdivision,
                                         slope_angle=slope_angle_t(time_step),
                                         inside=inside,
                                         rotation=rotation)

    # not thread safe, although that isn't a limitation
    vertex_list = []
    position_to_vertex_index = {}
    def call_coordinates(tube_subdivision, time_step, inside):
        position = (tube_subdivision, time_step, inside)
        if position in position_to_vertex_index:
            index = position_to_vertex_index[position]
            return index
        else:
            xyz = coordinates(x_t=x_t,
                              y_t=y_t,
                              z_t=z_t,
                              r_t=r_t,
                              tube_function=tube_function,
                              tube_subdivision=tube_subdivision,
                              inside=inside,
                              time_step=time_step)
            index = len(vertex_list)
            position_to_vertex_index[position] = index
            vertex_list.append(xyz)
            return index

    triangle_list = []
    def add_quad(bottom, right, top, left):
        # note that the names are meant to be evocative, not necessarily
        # exactly where the triangle is
        triangle_list.append((bottom, right, left))
        triangle_list.append((left, right, top))
    
    for time_step in range(num_time_steps):
        for tube_subdivision in range(num_tube_subdivisions):
            #print("Iterating over tube {} helix {}".format(tube_subdivision, time_step))
            # outside wall
            add_quad(call_coordinates(tube_subdivision, time_step, False),
                     call_coordinates(tube_subdivision+1, time_step, False),
                     call_coordinates(tube_subdivision+1, time_step+1, False),
                     call_coordinates(tube_subdivision, time_step+1, False))
            # inside wall
            if has_inner_wall:
                add_quad(call_coordinates(tube_subdivision, time_step, True),
                         call_coordinates(tube_subdivision, time_step+1, True),
                         call_coordinates(tube_subdivision+1, time_step+1, True),
                         call_coordinates(tube_subdivision+1, time_step, True))
            # start tube wall
            if tube_subdivision == 0 and not full_tube_t(time_step, time_step+1):
                add_quad(call_coordinates(tube_subdivision, time_step, False),
                         call_coordinates(tube_subdivision, time_step+1, False),
                         call_coordinates(tube_subdivision, time_step+1, True),
                         call_coordinates(tube_subdivision, time_step, True))
            # end tube wall
            if tube_subdivision == num_tube_subdivisions-1 and not full_tube_t(time_step, time_step+1):
                add_quad(call_coordinates(tube_subdivision+1, time_step, True),
                         call_coordinates(tube_subdivision+1, time_step+1, True),
                         call_coordinates(tube_subdivision+1, time_step+1, False),
                         call_coordinates(tube_subdivision+1, time_step, False))
            # start helix wall
            if time_step == 0:
                add_quad(call_coordinates(tube_subdivision, time_step, False),
                         call_coordinates(tube_subdivision, time_step, True),
                         call_coordinates(tube_subdivision+1, time_step, True),
                         call_coordinates(tube_subdivision+1, time_step, False))
            # end helix wall
            if time_step == num_time_steps-1:
                add_quad(call_coordinates(tube_subdivision, time_step+1, True),
                         call_coordinates(tube_subdivision, time_step+1, False),
                         call_coordinates(tube_subdivision+1, time_step+1, False),
                         call_coordinates(tube_subdivision+1, time_step+1, True))

    return vertex_list, triangle_list
                
def generate_path(x_t, y_t, z_t, r_t,
                  tube_args, num_time_steps,
                  time_t=None,
                  slope_angle_t=None):
    """
    Generates triangles one at a time for the path defined by x_t, y_t, z_t, and r_t
    """
    vertex_list, triangle_list = compose_triangles(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                                   tube_args=tube_args,
                                                   num_time_steps=num_time_steps,
                                                   time_t=time_t,
                                                   slope_angle_t=slope_angle_t)
                
    for left, right, top in triangle_list:
        yield (vertex_list[left], vertex_list[right], vertex_list[top])

def parse_eccentricity(e):
    """
    Turns a string into a float for the eccentricity of an ellipse wall.

    Applies constraints of 0 <= e < 1
    """
    e = float(e)
    if e < 0.0 or e >= 1:
        raise ValueError("Eccentricity must be 0 <= e < 1, got %f" % e)
    # TODO: maybe let <0 represent a flatter than expected tube?
    return e

def add_tube_arguments(parser,
                       default_slope_angle=-5.0,
                       default_output_name='foo.stl'):
    parser.add_argument('--tube_radius', default=12.5, type=float,
                        help='measurement from the center of ramp to its outer wall')
    parser.add_argument('--wall_thickness', default=2, type=float,
                        help='how thick to make the wall. special case: if wall_thickness >= tube_radius, there is no inner opening')
    parser.add_argument('--tube_start_angle', default=0, type=lambda arg: marble_util.parse_float_or_tuple_tuple(arg, '--tube_start_angle'),
                        help='angle to the start of the ramp.  0 represents the part furthest from the axis, 180 represents closest to the axis, -90 represents the top of the ramp, 90 represents the bottom.  0..180 represents the bottom of a ramp with no cover.  -90..90 will look like a loop-d-loop')
    parser.add_argument('--tube_end_angle', default=180, type=lambda arg: marble_util.parse_float_or_tuple_tuple(arg, '--tube_end_angle'),
                        help='angle to the end of the ramp.  same values as tube_start_angle')
    parser.add_argument('--tube_sides', default=64, type=int,
                        help='how many sides a complete tube would have.  tube_start_angle and tube_end_angle are discretized to these subdivisions')
    parser.add_argument('--tube_eccentricity', default=0.0, type=parse_eccentricity,
                        help='How much of an ellipse to make the tube.  0.0 is a circle.  Must be 0 <= e < 1')

    parser.add_argument('--tube_wall_height', default=0.0, type=float,
                        help='If creating an oval tube, how high to make the walls')

    parser.add_argument('--tube_method', default=Tube.ELLIPSE, type=lambda x: Tube[x.upper()],
                        help='How to generate the tube.  ELLIPSE means a circle, or an ellipse if tube_eccentricity is set.  OVAL means 0..180 half circle with vertical walls.  DEEP_OVAL and DEEP_ELLIPSE means the same, but with a deeper curve than a semicircle')

    parser.add_argument('--slope_angle', default=default_slope_angle, type=float,
                        help='Angle to tilt the curve')

    parser.add_argument('--output_name', default=default_output_name,
                        help='Where to put the stl')

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
