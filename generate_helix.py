import math

def generate_quad(a, b, c, d):
    yield((a, b, d))
    yield((b, c, d))

def generate_cube(size):
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

def coordinates(helix_radius, tube_radius, wall_thickness,
                start_angle, end_angle,
                tube_sides, helix_sides,
                vertical_displacement,
                tube_subdivision, helix_subdivision, inside):
    #print("GENERATING: {} {} {} {} {} {} {} {} {} {} {}".format(helix_radius, tube_radius, wall_thickness,
    #                                                            start_angle, end_angle,
    #                                                            tube_sides, helix_sides,
    #                                                            vertical_displacement,
    #                                                            tube_subdivision, helix_subdivision, inside))
    distance = helix_radius + tube_radius
    location = (distance, distance, tube_radius)   # x, y.  axis is pointing up
    location = (location[0], location[1],          # move up by the location in the helix
                location[2] + vertical_displacement * helix_subdivision / helix_sides)
    tube_angle = start_angle + 360 / tube_sides * tube_subdivision
    if tube_angle > end_angle:
        tube_angle = end_angle
    helix_angle = 360 / helix_sides * helix_subdivision

    if inside:
        tube_radius = tube_radius - wall_thickness
    
    vertical_disp = -tube_radius * math.sin(tube_angle / 180 * math.pi)
    radial_disp = helix_radius + math.cos(tube_angle / 180 * math.pi) * tube_radius
    x_disp = radial_disp * math.cos(helix_angle / 180 * math.pi)
    y_disp = radial_disp * math.sin(helix_angle / 180 * math.pi)

    location = (location[0] + x_disp,
                location[1] + y_disp,
                location[2] + vertical_disp)
    
    return location
    
def generate_helix(helix_radius, tube_radius, wall_thickness,
                   start_angle, end_angle,
                   tube_sides, helix_sides,
                   vertical_displacement,
                   rotations):
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
    if wall_thickness >= tube_radius:
        raise RuntimeError("TODO Not implemented")

    if end_angle < start_angle:
        start_angle, end_angle = end_angle, start_angle

    if end_angle >= start_angle + 360:
        start_angle = 0
        end_angle = 360
        num_tube_subdivisions = tube_sides
        full_tube = True
    else:
        num_tube_subdivisions = math.ceil((end_angle - start_angle) * tube_sides / 360)
        full_tube = False
    print("Num tube: {}".format(num_tube_subdivisions))

    num_helix_subdivisions = math.ceil(rotations * helix_sides)
    print("Num helix: {}".format(num_helix_subdivisions))
    if num_helix_subdivisions <= 0:
        raise ValueError("Must complete some positive fraction of a rotation")

    def call_coordinates(tube_subdivision, helix_subdivision, inside):
        return coordinates(helix_radius=helix_radius,
                           tube_radius=tube_radius,
                           wall_thickness=wall_thickness,
                           start_angle=start_angle,
                           end_angle=end_angle,
                           tube_sides=tube_sides,
                           helix_sides=helix_sides,
                           vertical_displacement=vertical_displacement,
                           tube_subdivision=tube_subdivision,
                           helix_subdivision=helix_subdivision,
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
    with open(filename, "w") as fout:
        for triangle in triangles:
            fout.write("facet normal 0 0 0\n")
            fout.write("    outer loop\n")
            for vertex in triangle:
                fout.write("        vertex %f %f %f\n" % vertex)
            fout.write("    endloop\n")
            fout.write("endfacet\n")

if __name__ == '__main__':
    write_stl(generate_helix(helix_radius=19, tube_radius=13, wall_thickness=2,
                             start_angle=-90, end_angle=90, tube_sides=64, helix_sides=64,
                             vertical_displacement=26,
                             rotations=1),
              "foo.stl")
    write_stl(generate_cube(10), 'cube.stl')
