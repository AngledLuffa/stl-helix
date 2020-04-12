import combine_functions
import marble_path
import slope_function

def generate_shape(module, args):
    module.describe_curve(args)

    time_t = module.build_time_t(args)
    x_t = module.build_x_t(args)
    y_t = module.build_y_t(args)

    num_time_steps = args.num_time_steps
    
    r_t = marble_path.numerical_rotation_function(x_t, y_t)

    # TODO: because the circle replacement does not keep the endpoints
    # the same, this will disrupt any attempt to set a scale such as
    # in generate_hypotrochoid's closest_approach.  For now, those
    # arguments are incompatible
    if args.kink_replace_circle:
        x_t, y_t, r_t = combine_functions.replace_kinks_with_circles(args=args,
                                                                     time_t=time_t,
                                                                     x_t=x_t,
                                                                     y_t=y_t,
                                                                     r_t=r_t,
                                                                     kink_args=args,
                                                                     num_time_steps=args.num_time_steps)

    module.print_stats(x_t, y_t, args.num_time_steps)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=args.num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=None)
    
    z_t = marble_path.arclength_height_function(x_t, y_t, args.num_time_steps, args.slope_angle)

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=args.num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle

def main(module, sys_args=None):
    args = module.parse_args(sys_args)
    marble_path.print_args(args)

    marble_path.write_stl(generate_shape(module, args), args.output_name)
