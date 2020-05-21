import combine_functions
import marble_path
import slope_function

def print_stats(x_t, y_t, z_t, r_t, num_time_steps):
    min_x = min(x_t(i) for i in range(num_time_steps + 1))
    max_x = max(x_t(i) for i in range(num_time_steps + 1))
    min_y = min(y_t(i) for i in range(num_time_steps + 1))
    max_y = max(y_t(i) for i in range(num_time_steps + 1))
    print("Min, max x: %.4f %.4f" % (min_x, max_x))
    print("Min, max y: %.4f %.4f" % (min_y, max_y))

    x0 = x_t(0)
    y0 = y_t(0)
    xn = x_t(num_time_steps)
    yn = y_t(num_time_steps)
    print("Start of the curve: (%.4f, %.4f)" % (x0, y0))
    print("End of the curve:   (%.4f, %.4f)" % (xn, yn))
    dist = ((xn - x0) ** 2 + (yn - y0) ** 2) ** 0.5
    print("Distance: %.4f (x %.4f, y %.4f)" % (dist, (xn - x0), (yn - y0)))
    print("Top: %.4f  Bottom: %.4f" % (z_t(0), z_t(num_time_steps)))
    print("Begin rotation: %.4f" % r_t(0))
    print("End rotation:   %.4f" % r_t(num_time_steps))

def generate_shape(module, args):
    module.describe_curve(args)

    if getattr(module, 'build_time_t', None) is not None:
        time_t = module.build_time_t(args)
    else:
        time_t = lambda t: t

    if getattr(module, 'build_x_y_r_t', None) is not None:
        x_t, y_t, r_t = module.build_x_y_r_t(args)
    elif getattr(module, 'build_x_y_t', None) is not None:
        x_t, y_t = module.build_x_y_t(args)
        r_t = marble_path.numerical_rotation_function(x_t, y_t)
    else:
        x_t = module.build_x_t(args)
        y_t = module.build_y_t(args)
        r_t = marble_path.numerical_rotation_function(x_t, y_t)

    num_time_steps = args.num_time_steps

    # TODO: because the circle replacement does not keep the endpoints
    # the same, this will disrupt any attempt to set a scale such as
    # in generate_hypotrochoid's closest_approach.  For now, those
    # arguments are incompatible
    if getattr(args, 'kink_replace_circle', None):
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
                                                  num_time_steps=num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=args)
    
    z_t = marble_path.arclength_height_function(x_t, y_t, num_time_steps, slope_angle_t=slope_angle_t)

    print_stats(x_t, y_t, z_t, r_t, num_time_steps)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              time_t=time_t,
                                              slope_angle_t=slope_angle_t):
        yield triangle

def main(module, sys_args=None):
    args = module.parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_shape(module, args), args.output_name)
